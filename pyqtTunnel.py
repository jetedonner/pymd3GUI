#!/usr/bin/env python3

import subprocess
import asyncio
import logging
import sys
import tempfile
from functools import partial
from typing import List, TextIO

import click

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
#from pymobiledevice3.services.afc import AfcService, AfcShell, afc_opcode_t, afc_read_dir_req_t, afc_header_t

from pymobiledevice3.cli.cli_common import RSDCommand, print_json, prompt_device_list, sudo_required
from pymobiledevice3.exceptions import NoDeviceConnectedError
from pymobiledevice3.remote.bonjour import get_remoted_addresses
from pymobiledevice3.remote.module_imports import MAX_IDLE_TIMEOUT, start_quic_tunnel, verify_tunnel_imports
from pymobiledevice3.remote.remote_service_discovery import RSD_PORT, RemoteServiceDiscoveryService
from pymobiledevice3.remote.utils import TUNNELD_DEFAULT_ADDRESS, stop_remoted
from pymobiledevice3.tunneld import TunneldRunner

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
#from PyQt6.QtCore import QIODevice, QTextStream, QTextEdit

from pyqtDeviceHelper import *

import time
import threading
import queue
# The new Stream Object which replaces the default stream associated with sys.stdout
# This object just puts data in a queue!
class WriteStream(object):
	def __init__(self,queue):
		self.queue = queue
		
	def write(self, text):
		self.queue.put(text)
		
# A QObject (to be run in a QThread) which sits waiting for data to come through a Queue.Queue().
# It blocks until data is available, and one it has got something from the queue, it sends
# it to the "MainThread" by emitting a Qt Signal 
class MyReceiver(QObject):
	mysignal = pyqtSignal(str)
	
	def __init__(self,queue,*args,**kwargs):
		QObject.__init__(self,*args,**kwargs)
		self.queue = queue
		
	@pyqtSlot()
	def run(self):
		while True:
			text = self.queue.get()
			self.mysignal.emit(text)
			
# An example QObject (to be run in a QThread) which outputs information with print
class LongRunningThing(QObject):
	@pyqtSlot()
	def run(self):
		for i in range(1000):
			time.sleep(0.1)
			print(i)
#import pyperclip
#
#from pyqtHelper import human_readable_size
logger = logging.getLogger(__name__)

usbmux_address = None

async def tunnel_task(service_provider: RemoteServiceDiscoveryService, secrets: TextIO, script_mode: bool = False, max_idle_timeout: float = MAX_IDLE_TIMEOUT) -> None:
		if start_quic_tunnel is None:
				raise NotImplementedError('failed to start the QUIC tunnel on your platform')
			
		async with start_quic_tunnel(service_provider, secrets=secrets, max_idle_timeout=max_idle_timeout) as tunnel_result:
				logger.info('tunnel created')
				if script_mode:
						print(f'{tunnel_result.address} {tunnel_result.port}')
				else:
					sys.stdout.write("INSIDE YESSSSS!!!!!")
					if secrets is not None:
						print(click.style('Secrets: ', bold=True, fg='magenta') + click.style("secrets.name", bold=True, fg='white'))
						print(click.style('UDID: ', bold=True, fg='yellow') + click.style(service_provider.udid, bold=True, fg='white'))
						print(click.style('ProductType: ', bold=True, fg='yellow') + click.style(service_provider.product_type, bold=True, fg='white'))
						print(click.style('ProductVersion: ', bold=True, fg='yellow') + click.style(service_provider.product_version, bold=True, fg='white'))
						print(click.style('Interface: ', bold=True, fg='yellow') + click.style(tunnel_result.interface, bold=True, fg='white'))
						print(click.style('RSD Address: ', bold=True, fg='yellow') + click.style(tunnel_result.address, bold=True, fg='white'))
						print(click.style('RSD Port: ', bold=True, fg='yellow') + click.style(tunnel_result.port, bold=True, fg='white'))
						print(click.style('Use the follow connection option:\n', bold=True, fg='yellow') + click.style(f'--rsd {tunnel_result.address} {tunnel_result.port}', bold=True, fg='cyan'))
				sys.stdout.flush()
			
				await tunnel_result.client.wait_closed()
				logger.info('tunnel was closed')
			
			
def get_device_list() -> List[RemoteServiceDiscoveryService]:
	result = []
	with stop_remoted():
		for address in get_remoted_addresses():
			rsd = RemoteServiceDiscoveryService((address, RSD_PORT))
			try:
				rsd.connect()
			except ConnectionRefusedError:
				continue
			result.append(rsd)
	return result

def cli_start_quic_tunnel(udid: str, secrets: TextIO, script_mode: bool, max_idle_timeout: float):
	""" start quic tunnel """
	if not verify_tunnel_imports():
		return
	devices = get_device_list()
	if not devices:
		# no devices were found
		raise NoDeviceConnectedError()
	if len(devices) == 1:
		# only one device found
		rsd = devices[0]
	else:
		# several devices were found
		if udid is None:
			# show prompt if non explicitly selected
			rsd = prompt_device_list(devices)
		else:
			rsd = [device for device in devices if device.udid == udid]
			if len(rsd) > 0:
				rsd = rsd[0]
			else:
				raise NoDeviceConnectedError()
				
	if udid is not None and rsd.udid != udid:
		raise NoDeviceConnectedError()
		
	asyncio.run(tunnel_task(rsd, secrets, script_mode, max_idle_timeout=max_idle_timeout), debug=True)

class TextIODevice(QIODevice):
	
	def __init__(self, textedit):
		super().__init__()
		self.textedit = textedit
		
	def open(self, mode='r'):
		self.textedit.setReadOnly(False)
		if mode == 'w':
			self.textedit.clear()
		self.textstream = QTextStream(self.textedit.document())
		self.textstream.setCodec('utf-8')
		return True
	
	def close(self):
		self.textedit.setReadOnly(True)
		self.textstream.flush()
		self.textstream.reset()
		return True
	
	def write(self, data):
		self.textstream.write(data)
		self.textedit.ensureCursorVisible()
		
	def read(self, size):
		data = self.textstream.read(size)
		return data
	
	def atEnd(self):
		return self.textstream.atEnd()
	
	def pos(self):
		return self.textstream.pos()
	
	def seek(self, pos):
		self.textstream.seek(pos)
		
class RedirectOutput:
	def __init__(self, text_edit):
		self.text_edit = text_edit
		self.text_stream = QTextStream(self.text_edit)
		
	def write(self, text):
		# Append the text to the QTextEdit
		self.text_stream << text

class OutputRedirector:
	
	def __init__(self, textedit):
		self.stdout = sys.stdout
		self.textedit = textedit
		self.textedit.insertPlainText("INITED")
		
	def write(self, text):
		self.stdout.write(text)
		self.textedit.insertPlainText(text)
#		if text != "":
#			sys.stderr.write(f"DEBUG TXT: {text}")
		
	def flush(self):
		self.stdout.flush()
		
	def close(self):
		self.stdout.close()
		
class SubprocessThread(QThread):
	def __init__(self, cmd):
		super().__init__()
		self.cmd = cmd
		self.process = None
		self.stopped = True
		self.output = ""
		
	def run(self):
		self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
		while True:
			if not self.stopped:
				try:
					output = self.process.stdout.readline().decode('utf-8')
					with mutex:
						print("Output: {output}")
#						textEdit.append(output)
						self.output += output
						
					if not output:
						if self.process.poll() != None:
							break
				except:
					# Catch any exceptions and kill the process
					self.process.kill()
					break
				
	def stop(self):
		self.stopped = True
		self.process.terminate()
		
class TabTunnel(QWidget):
	
	tunnelCreated:bool = False
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setLayout(QVBoxLayout())
		
		self.gbCtrl = QGroupBox("Tunnel control")
		self.gbCtrl.setLayout(QHBoxLayout())
		
		self.layCtrlInnerSudo = QVBoxLayout()
		self.widCtrlInnerSudo = QWidget()
		self.widCtrlInnerSudo.setLayout(self.layCtrlInnerSudo)
		
		self.layCtrlInnerHost = QVBoxLayout()
		self.widCtrlInnerHost = QWidget()
		self.widCtrlInnerHost.setLayout(self.layCtrlInnerHost)
		
		self.layCtrlInnerPort = QVBoxLayout()
		self.widCtrlInnerPort = QWidget()
		self.widCtrlInnerPort.setLayout(self.layCtrlInnerPort)
		
		self.lblPassword = QLabel("Sudu password (required):")
		
		self.txtSudoPassword = QLineEdit()
		self.txtSudoPassword.setEchoMode(QLineEdit.EchoMode.Password)
		self.txtSudoPassword.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)
		self.txtSudoPassword.setPlaceholderText("Enter sudo password ...")
#		self.txtSudoPassword.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layCtrlInnerSudo.addWidget(self.lblPassword)
		self.layCtrlInnerSudo.addWidget(self.txtSudoPassword)
		
		self.lblHost = QLabel("Host (optional):")
		
		self.txtHost = QLineEdit()
		self.txtHost.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)
#		self.txtHost.setEchoMode(QLineEdit.EchoMode.Password)
		self.txtHost.setPlaceholderText("Hostname (optional)")
#		self.txtSudoPassword.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layCtrlInnerHost.addWidget(self.lblHost)
		self.layCtrlInnerHost.addWidget(self.txtHost)
		
		self.lblPort = QLabel("Port (optional):")
		
		self.txtPort = QLineEdit()
		self.txtPort.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)
#		self.txtHost.setEchoMode(QLineEdit.EchoMode.Password)
		self.txtPort.setPlaceholderText("Port (optional)")
		self.portValidator = QIntValidator(0, 65535)
		self.txtPort.setValidator(self.portValidator)
		
#		self.txtSudoPassword.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layCtrlInnerPort.addWidget(self.lblPort)
		self.layCtrlInnerPort.addWidget(self.txtPort)
		
		self.chkDeamonize = QCheckBox("Deamonize")
#		self.chkDeamonize.stateChanged.connect(self.chkDeamonize_changed)
#		self.layCtrl.addWidget(self.chkDeamonize)
		
		self.cmdStartTunnel = QPushButton("Create tunnel service")
		self.cmdStartTunnel.clicked.connect(self.cmdStartTunnel_clicked)
		
		self.gbCtrl.layout().addWidget(self.widCtrlInnerSudo)
		self.gbCtrl.layout().addWidget(self.widCtrlInnerHost)
		self.gbCtrl.layout().addWidget(self.widCtrlInnerPort)
		self.gbCtrl.layout().addWidget(self.chkDeamonize)
		self.gbCtrl.layout().addWidget(self.cmdStartTunnel)
#		self.gbCtrl.layout().addWidget(self.txtSudoPassword)
		
		self.gbConsole = QGroupBox("Console output")
		self.gbConsole.setLayout(QHBoxLayout())
		self.gbConsole.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
		
		self.txtConsole = QTextEdit()
		self.txtConsole.setReadOnly(True)
		self.txtConsole.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		# Create an OutputRedirector and connect it to the QTextEdit
		self.redirector = OutputRedirector(self.txtConsole)
		
		# Replace sys.stdout with the OutputRedirector
		sys.stdout = self.redirector
		
		self.gbConsole.layout().addWidget(self.txtConsole)
		
		self.layout().addWidget(self.gbCtrl)
		self.layout().addWidget(self.gbConsole)
		
#		self.mutex = QMutex()
#		self.stopEvent = QWaitCondition()
#
#		self.thread = SubprocessThread(["find", "/", "python3"])
#		self.thread.start()
#
##		self.textEdit.show()
#
#		# Start a loop to check if the user wants to abort the process
#		while True:
#			if self.thread.stopped:
#				print("Subprocess stopped")
#				break
#			else:
#				try:
#					self.exec()
#				except:
#					print("Subprocess exception catched")
#					break
		
	def cmdStartTunnel_clicked(self):
		if self.tunnelCreated:
			self.addConsoleTxt("Tunnel service removed ...")
			self.cmdStartTunnel.setText("Create tunnel service")
			self.tunnelCreated = False
		else:
			if self.txtSudoPassword.text() == "":
				self.txtConsole.setTextColor(QColor("red"))
				self.addConsoleTxt("No sudo password entered. Sudo is required to create tunnel!")
				self.txtConsole.setTextColor(QColor("white"))
				self.tunnelCreated = False
			else:
				self.addConsoleTxt("Tunnel service created ...")
				self.cmdStartTunnel.setText("Remove tunnel service")
				self.tunnelCreated = True
				# Redirect sys.stdout to the QTextEdit
#				sys.stdout = RedirectOutput(self.txtConsole)
				cli_start_quic_tunnel("00008110-001241591460201E", sys.stdout, False, 3000)
		
		self.txtSudoPassword.setEnabled(not self.tunnelCreated)
		self.txtHost.setEnabled(not self.tunnelCreated)
		self.txtPort.setEnabled(not self.tunnelCreated)
		self.chkDeamonize.setEnabled(not self.tunnelCreated)
	
	
		
	def addConsoleTxt(self, msg):
#		self.txtConsole.document.append(msg)
		self.txtConsole.insertPlainText(f'{msg}\n')
#		self.tree_widget = AFCTreeWidget()
#		self.tree_widget.setHeaderLabels(['File/Folder', 'Size', 'Created'])
#		
#		self.root_item = QTreeWidgetItem(self.tree_widget, ['/', '', '/var/mobile/Media'])
#		
#		# Expand the root item
#		self.tree_widget.expandItem(self.root_item)
#		self.tree_widget.header().resizeSection(0, 256)
##		self.tree_widget.itemExpanded.connect(itemExpanded)
#		
#		self.layout().addWidget(self.tree_widget)
		
		