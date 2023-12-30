#!/usr/bin/env python3

from datetime import datetime
from typing import IO, Optional

import click
from pygments import formatters, highlight, lexers
import hexdump

from pymobiledevice3.cli.cli_common import Command, print_hex
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.os_trace import OsTraceService, SyslogLogLevel
from pymobiledevice3.services.pcapd import PcapdService

#from pyqtTabBase import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QIntValidator, QColor
from PyQt6.QtWidgets import *
from pyqtTabBase import *

from pyqtDeviceHelper import *

from QSwitch import *

def print_packet_header(packet, color: bool):
	date = datetime.fromtimestamp(packet.seconds + (packet.microseconds / 1000000))
	data = (
		f'{date}: '
		f'Process {packet.comm} ({packet.pid}), '
		f'Interface: {packet.interface_name} ({packet.interface_type.name}), '
		f'Family: {packet.protocol_family.name}'
	)
	if not color:
		print(data)
	else:
		print(highlight(data, lexers.HspecLexer(), formatters.TerminalTrueColorFormatter(style='native')), end='')
		
		
def print_packet(packet, color: bool):
	""" Return the packet so it can be chained in a generator """
	print_packet_header(packet, color)
	print_hex(packet.data, color)
	QCoreApplication.processEvents()
	return packet

def get_packet_header(packet, color: bool):
	date = datetime.fromtimestamp(packet.seconds + (packet.microseconds / 1000000))
	data = (
		f'{date}: '
		f'Process {packet.comm} ({packet.pid}), '
		f'Interface: {packet.interface_name} ({packet.interface_type.name}), '
		f'Family: {packet.protocol_family.name}'
	)
	return data
#	if not color:
#		print(data)
#	else:
#		print(highlight(data, lexers.HspecLexer(), formatters.TerminalTrueColorFormatter(style='native')), end='')
		
		
def get_packet(packet, color: bool):
	""" Return the packet so it can be chained in a generator """
	sRet = get_packet_header(packet, color)
	sRet += "\n" + hexdump.hexdump(packet.data, result='return') + "\n"
#	print_hex(packet.data, color)
#	QCoreApplication.processEvents()
	return sRet

class PCapReceiver(QObject):
#	data_received = pyqtSignal(str)
	interruptPCap = pyqtSignal()
	
class PCapWorkerSignals(QObject):
	finished = pyqtSignal()
	sendPCap = pyqtSignal(str, str)
	
class PCapWorker(QRunnable):
	def __init__(self, data_receiver):
		super(PCapWorker, self).__init__()
		self.isPCapActive = False
		self.data_receiver = data_receiver
		self.signals = PCapWorkerSignals()
		
	def run(self):
		self.data_receiver.interruptPCap.connect(self.handle_interruptPCap)
		QCoreApplication.processEvents()
		self.runPCap()
		
	def runPCap(self):
		self.isPCapActive = True
		result, lockdown = lockdownForFirstDevice()
		print(f'{result}: {lockdown}')
		if result:
#				diagnostics_restart(lockdown)
			service = PcapdService(lockdown=lockdown)
			packets_generator = service.watch(packets_count=-1, process=None, interface_name=None)
			out = None
			if out is not None:
				packets_generator_with_print = map(lambda p: print(f'{p}'), packets_generator) # print_packet(p, True), packets_generator)
				service.write_to_pcap(out, packets_generator_with_print)
				self.signals.finished.emit()
				return
			
			for packet in packets_generator:
#				print(f'IN FOR LOOP: {packet}')
				print_packet(packet, False)
				self.signals.sendPCap.emit(get_packet(packet, False), "white")
				QCoreApplication.processEvents()
				if not self.isPCapActive:
					break
				
#		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
#		if len(devices) <= 1:
#		result, lockdown = lockdownForFirstDevice()
#		if result:
#			for syslog_entry in OsTraceService(lockdown=lockdown).syslog(pid=-1):
##				print(syslog_entry.timestamp)
#				self.signals.sendPCap.emit(str(syslog_entry.timestamp), "green")
#				self.signals.sendPCap.emit(str(syslog_entry.message), "white")
#				self.signals.sendPCap.emit(str("\n"), "white")
#				QCoreApplication.processEvents()
#				if self.isPCapActive is False:
#					break
				
		self.signals.finished.emit()
		QCoreApplication.processEvents()
		
	def handle_interruptPCap(self):
#		print(f"Received interrupt in the sysLog worker thread")
		self.isPCapActive = False
		
class TabPCap(TabLogBase):
	
	def interruptPcapThread(self):
#		QCoreApplication.processEvents()
		self.window().pcap_receiver.interruptPCap.emit()
		QCoreApplication.processEvents()
		
	def __init__(self, parent=None):
		super().__init__(True, True, True, parent)
		
		validator = QIntValidator(-1, 1000000)
		
		self.layPidFilter = QVBoxLayout()
		self.wdtPidFilter = QWidget()
		self.wdtPidFilter.setLayout(self.layPidFilter)
		
		self.lblPidFilter = QLabel("Process (-1 = No Filter):")
		self.txtPidFilter = QLineEdit("-1")
		self.txtPidFilter.setValidator(validator)
		
		self.cmbPid = QComboBox()
		self.cmbPid.setEditable(True)
		self.cmbPid.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)
		
		self.my_processes = {str("-1"): "(No Filter)"}
#		self.cmbPid.setStyle(MyComboBoxStyle())
		self.cmbPid.setItemDelegate(MyComboBoxStyledItemDelegate())
		self.cmbPid.setStyleSheet("QComboBox { selection-background-color: #ccc; }")
		
		result, lockdown = lockdownForFirstDevice()
		if result:
			processes_list = OsTraceService(lockdown=lockdown).get_pid_list().get('Payload')
			for pid, process_info in processes_list.items():
				process_name = process_info.get('ProcessName')
#				print(f'{pid} ({process_name})')
				self.cmbPid.addItem(f'{pid} ({process_name})')
				self.my_processes.update({str(pid): process_name})
		else:
			print("No device detected!")
			
		self.layPidFilter.layout().addWidget(self.lblPidFilter)
		self.layPidFilter.layout().addWidget(self.cmbPid)
		self.gbCtrl.layout().addWidget(self.wdtPidFilter)
		
		
		self.layInterfaceFilter = QVBoxLayout()
		self.wdtInterfaceFilter = QWidget()
		self.wdtInterfaceFilter.setLayout(self.layInterfaceFilter)
		
		self.lblInterfaceFilter = QLabel("Interface (en):")
#		self.txtInterfaceFilter = QLineEdit("en")
#		self.txtInterfaceFilter.setValidator(validator)
		
		self.cmbInterface = QComboBox()
		self.cmbInterface.setEditable(True)
		self.cmbInterface.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)
		
		self.layInterfaceFilter.layout().addWidget(self.lblInterfaceFilter)
		self.layInterfaceFilter.layout().addWidget(self.cmbInterface)
		self.gbCtrl.layout().addWidget(self.wdtInterfaceFilter)
		
		self.layPackets = QVBoxLayout()
		self.wdtPackets = QWidget()
		self.wdtPackets.setLayout(self.layPackets)
		
		self.lblPackets = QLabel("Packet count:")
		self.txtPackets = QLineEdit("100")
		self.txtPackets.setValidator(validator)
		
#		self.cmbInterface = QComboBox()
#		self.cmbInterface.setEditable(True)
#		self.cmbInterface.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)
		
		self.layPackets.layout().addWidget(self.lblPackets)
		self.layPackets.layout().addWidget(self.txtPackets)
		self.gbCtrl.layout().addWidget(self.wdtPackets)
		
		self.swtColorize = QSwitch("Colorize", SwitchSize.Small, SwitchLabelPos.Trailing)
#		self.swtColorize.checked.connect(self.wireless_checked)
		self.gbCtrl.layout().addWidget(self.swtColorize)
		
#		self.setLayout(QVBoxLayout())
#		self.cmdStartCapture = QPushButton("Start capture")
#		self.cmdStartCapture.setToolTip("Start capture device traffic")
#		
#		def cmdStartCaptureHandler():
##			result, lockdown = lockdownForFirstDevice()
##			if result:
###				diagnostics_restart(lockdown)
##				service = PcapdService(lockdown=lockdown)
##				packets_generator = service.watch(packets_count=-1, process=None, interface_name=None)
##				out = None
##				if out is not None:
##					packets_generator_with_print = map(lambda p: print_packet(p, True), packets_generator)
##					service.write_to_pcap(out, packets_generator_with_print)
##					return
##			
##				for packet in packets_generator:
##					print_packet(packet, True)
#			self.window().start_workerPCap()
#			self.updateStatusBar("Capturing traffic started ...")
#				
#		self.cmdStartCapture.clicked.connect(cmdStartCaptureHandler)
#		self.gbCtrl.layout().addWidget(self.cmdStartCapture)
	
	def capture_checked(self, checked):
#		pass
#	def listen_checked(self, checked):
		if checked:
#			result, lockdown = lockdownForFirstDevice()
			#			if result:
			##				diagnostics_restart(lockdown)
			#				service = PcapdService(lockdown=lockdown)
			#				packets_generator = service.watch(packets_count=-1, process=None, interface_name=None)
			#				out = None
			#				if out is not None:
			#					packets_generator_with_print = map(lambda p: print_packet(p, True), packets_generator)
			#					service.write_to_pcap(out, packets_generator_with_print)
			#					return
			#			
			#				for packet in packets_generator:
			#					print_packet(packet, True)
			self.window().start_workerPCap()
			self.updateStatusBar("Capturing traffic started ...")			
			pass
		else:
			self.interruptPcapThread()
#			self.window().start_workerComm()
#			self.addConsoleTxt("Communication listener started ...")
##			self.cmdStartListening.setText("Stop listening")
#			QCoreApplication.processEvents()
			pass
			#		self.updateStatusBar(f"WirelessOn changed to {checked}")
		pass
		
	def clear_clicked(self):
		super().clear_clicked()
		self.updateStatusBar("PCap log cleared ...")