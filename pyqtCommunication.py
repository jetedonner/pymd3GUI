#!/usr/bin/env python3
import subprocess
import threading
import time

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux

from PyQt6.QtCore import *
from PyQt6.QtGui import QIntValidator, QColor
from PyQt6.QtWidgets import *

from pyqtDeviceHelper import *
from socatListener import *
from helper import pyqtIconHelper

class CommReceiver(QObject):
	#	data_received = pyqtSignal(str)
	interruptComm = pyqtSignal()
	
class CommWorkerSignals(QObject):
	finished = pyqtSignal()
	#	result = pyqtSignal(str)
	sendComm = pyqtSignal(str)
	
class CommWorker(QRunnable):
	
	mv_command = "sudo mv /var/run/usbmux_real /var/run/usbmux_real2"
	mv_command_revert = "sudo mv /var/run/usbmux_real2 /var/run/usbmux_real"
	
	socat_command = [
		"sudo", "socat",
		"-t100", "-v", # "-x",
		"UNIX-LISTEN:/var/run/usbmux_real,mode=777,reuseaddr,fork",
		"UNIX-CONNECT:/var/run/usbmux_real2"
	]
	
	def __init__(self, data_receiver):
		super(CommWorker, self).__init__()
		self.isCommActive = False
		self.data_receiver = data_receiver
		self.data_receiver.interruptComm.connect(self.handle_interruptComm)
		print(f'self.data_receiver: {self.data_receiver}')
		self.signals = CommWorkerSignals()
		self.proc = None
		
	def run(self):
		self.isCommActive = True
#		self.data_receiver.interruptComm.connect(self.handle_interruptComm)
#		print(f'self.data_receiver: {self.data_receiver}')
		QCoreApplication.processEvents()
		self.runComm()
		
	def runComm(self):
		try:
			result, msg, stdout = self.runCommand(self.mv_command)
			if result:
				print(msg)
				print(stdout)
				try:
					# Start socat as a subprocess with stdout and stderr as pipes
					self.proc = subprocess.Popen(self.socat_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
					
					# Start a thread to read and print the subprocess output
					self.output_thread = threading.Thread(target=self.read_output, args=(self.proc,), daemon=True)
					self.output_thread.start()
					
					#	input("Press Enter to exit...")
					while self.isCommActive:
						print("WAITING ....")
						time.sleep(0.1)
						
				except Exception as e:
					print(f"Error: {e}")
				finally:
					resultRevert, msgRevert, stdoutRevert = self.runCommand(self.mv_command_revert)
					self.signals.finished.emit()
					QCoreApplication.processEvents()
			else:
				print(msg)
				print(stdout)
		except Exception as e:
			print(f"Error starting communication listener. Exception: {e}")
			
	def runCommand(self, cmd):
		try:
			process = subprocess.run(cmd, shell=True, check=True, text=True, universal_newlines=True, stdout=subprocess.PIPE)
			stdout = process.stdout
			
			if process.returncode == 0:
				return True, f"Command executed successfully: {cmd}", stdout
			else:
				return False, f"Command execution failed: {cmd}", stdout
		except Exception as e:
			return False, f"Command execution failed: {cmd}, Error: {e}", None
			
	# Function to read and print subprocess output
	def read_output(self, proc):
		while self.isCommActive:
			line = self.proc.stdout.readline()
			if not line:
				break
			print(f'{line}')
			self.signals.sendComm.emit(str(f"{line}"))
			QCoreApplication.processEvents()
			
	def handle_interruptComm(self):
		QCoreApplication.processEvents()
		print(f"Received interrupt in the communication worker thread")
		self.isCommActive = False
		QCoreApplication.processEvents()

class TabCommunication(QWidget):
		
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.doAutoScroll = True
		
		self.setLayout(QVBoxLayout())
		
		self.gbCtrl = QGroupBox("Communication settings")
		self.gbCtrl.setLayout(QHBoxLayout())
		
		self.layCtrlInnerSocat = QVBoxLayout()
		self.widCtrlInnerSocat = QWidget()
		self.widCtrlInnerSocat.setLayout(self.layCtrlInnerSocat)
		
		self.layCtrlInnerSudo = QVBoxLayout()
		self.widCtrlInnerSudo = QWidget()
		self.widCtrlInnerSudo.setLayout(self.layCtrlInnerSudo)
		
#		self.layCtrlInnerHost = QVBoxLayout()
#		self.widCtrlInnerHost = QWidget()
#		self.widCtrlInnerHost.setLayout(self.layCtrlInnerHost)
		
		self.optSocat = QRadioButton("Socat")
		self.optSocat.setToolTip("Use system 'socat' command for capturing communication")
		self.optSocat.setChecked(True)
		self.optSocat.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
#		self.gbDevices.layout().addWidget(self.optUSB)
		
		self.optOwn = QRadioButton("Internal")
		self.optOwn.setToolTip("Use python implenmentation for capturing communication (experimental)")
		self.optOwn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
#		self.gbDevices.layout().addWidget(self.optNet)
		
		self.layCtrlInnerSocat.addWidget(self.optSocat)
		self.layCtrlInnerSocat.addWidget(self.optOwn)
		
		self.lblPassword = QLabel("Sudu password (required):")
		
		self.txtSudoPassword = QLineEdit()
		self.txtSudoPassword.setEchoMode(QLineEdit.EchoMode.Password)
		self.txtSudoPassword.setPlaceholderText("Enter sudo password ...")
#		self.txtSudoPassword.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layCtrlInnerSudo.addWidget(self.lblPassword)
		self.layCtrlInnerSudo.addWidget(self.txtSudoPassword)
		
		
		self.gbCtrl.layout().addWidget(self.widCtrlInnerSocat)
		self.gbCtrl.layout().addWidget(self.widCtrlInnerSudo)
		
		self.gbConsole = QGroupBox("Communication output")
		self.gbConsole.setLayout(QVBoxLayout())
		self.gbConsole.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
		
		self.txtConsole = QTextEdit()
		self.txtConsole.setReadOnly(True)
		self.txtConsole.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.gbConsole.layout().addWidget(self.txtConsole)
		
		self.cmdStartListening = QPushButton("Start listening")
		self.cmdStartListening.setToolTip("Start / Stop listening for communication with the connected idevice")
		self.cmdStartListening.clicked.connect(self.cmdStartListening_clicked)
		self.gbCtrl.layout().addWidget(self.cmdStartListening)
		
		self.layout().addWidget(self.gbCtrl)
		self.layout().addWidget(self.gbConsole)
		
		self.layCtrl = QHBoxLayout()
		self.widCtrl = QWidget()
		self.widCtrl.setLayout(self.layCtrl)
		
		self.commActive = QCheckBox("Communication active")
		self.commActive.setToolTip("Is the communication log active?")
#		self.commActive.stateChanged.connect(self.commActive_changed)
		self.layCtrl.addWidget(self.commActive)
		
		self.autoScroll = QCheckBox("Autoscroll")
		self.autoScroll.setToolTip("Set autoscroll for the communication log")
		self.autoScroll.setChecked(True)
		self.autoScroll.stateChanged.connect(self.commAutoScroll_changed)
		self.layCtrl.addWidget(self.autoScroll)
		
		self.cmdClear = QPushButton()
		self.cmdClear.setIcon(pyqtIconHelper.IconHelper.getBinIcon())
		self.cmdClear.setToolTip("Clear the communication log")
		self.cmdClear.setIconSize(QSize(16, 16))
		self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdClear.clicked.connect(self.clear_clicked)
		self.layCtrl.addWidget(self.cmdClear)
		
		self.gbConsole.layout().addWidget(self.widCtrl)
		
#		self.comm_receiver = CommReceiver()
#		self.commWorker = CommWorker(self.comm_receiver)
#		self.commWorker.signals.sendComm.connect(self.handle_sendComm)
#	
#	def handle_sendComm(self, text):
#		if text[0] == "<":
#			self.txtConsole.setTextColor(QColor("green"))
#		elif text[0] == ">":
#			self.txtConsole.setTextColor(QColor("red"))
#		else:
#			self.txtConsole.setTextColor(QColor("white"))
#		self.txtConsole.insertPlainText(text) #.append(text, color)
#		if self.doAutoScroll:
#			self.sb = self.txtConsole.verticalScrollBar()
#			self.sb.setValue(self.sb.maximum())
	
	def commAutoScroll_changed(self, state):
		autoScrollComm = (state == 2)
		
		self.doAutoScroll = autoScrollComm
#		QMetaObject.invokeMethod(self.textLog,
#				"updateAutoScroll", Qt.ConnectionType.QueuedConnection, 
#				Q_ARG(bool, autoScrollSysLog))
			
	def clear_clicked(self):
		self.txtConsole.clear()
		
	def cmdStartListening_clicked(self):
		if self.cmdStartListening.text() == "Stop listening":
			QCoreApplication.processEvents()
			print(f'self.window().comm_receiver: {self.window().comm_receiver}')
			self.window().comm_receiver.interruptComm.emit()
#			print("Before deactivating communication listener!")
#			self.comm_receiver.interruptComm.emit()
			self.addConsoleTxt("Communication listener stopped ...")
			self.cmdStartListening.setText("Start listening")
#			print("End deactivating communication listener!")
			QCoreApplication.processEvents()
			pass
		else:
			self.window().start_workerComm() #.threadpool.start(self.commWorker)
			self.addConsoleTxt("Communication listener started ...")
			self.cmdStartListening.setText("Stop listening")
			QCoreApplication.processEvents()
			pass
		
	def addConsoleTxt(self, msg):
		self.txtConsole.insertPlainText(f'{msg}\n')