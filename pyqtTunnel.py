#!/usr/bin/env python3

import subprocess
import sys

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
#from pymobiledevice3.services.afc import AfcService, AfcShell, afc_opcode_t, afc_read_dir_req_t, afc_header_t

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from pyqtDeviceHelper import *

#import pyperclip
#
#from pyqtHelper import human_readable_size

usbmux_address = None

#class AFCReceiver(QObject):
##	data_received = pyqtSignal(str)
#	interruptSysLog = pyqtSignal()
#	
#class AFCWorkerSignals(QObject):
#	finished = pyqtSignal()
##	result = pyqtSignal(str)
#	sendSysLog = pyqtSignal(str, str)
#	
#class AFCWorker(QRunnable):
#	def __init__(self, data_receiver, root_item):
#		super(AFCWorker, self).__init__()
##		self.isSysLogActive = False
#		self.root_item = root_item
#		self.data_receiver = data_receiver
#		self.signals = AFCWorkerSignals()
#		
#	def run(self):
##		self.data_receiver.interruptSysLog.connect(self.handle_interruptAFC)
#		QCoreApplication.processEvents()	
#		self.runAFCLs()
#		
#	def runAFCLs(self):
##		self.isSysLogActive = True
#		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
##		print(f"usbmux_address: {usbmux_address}")
#		if len(devices) <= 1:
#			afc_ls(create_using_usbmux(usbmux_address=usbmux_address), self.root_item)
##			print(f"usbmux_address: {usbmux_address}")
##			for syslog_entry in OsTraceService(lockdown=create_using_usbmux(usbmux_address=usbmux_address)).syslog(pid=-1):
###				print(syslog_entry.timestamp)
##				self.signals.sendSysLog.emit(str(syslog_entry.timestamp), "green")
##				self.signals.sendSysLog.emit(str(syslog_entry.message), "white")
##				self.signals.sendSysLog.emit(str("\n"), "white")
##				QCoreApplication.processEvents()
##				if self.isSysLogActive is False:
##					break
#		QCoreApplication.processEvents()		
#		self.signals.finished.emit()
#		
#	def handle_interruptAFC(self):
##		print(f"Received interrupt in the sysLog worker thread")
##		self.isSysLogActive = False
#		pass
#		
#def afc_ls(service_provider: LockdownClient, root_item: QTreeWidgetItem, remote_file = '/', recursive = False):
#	""" perform a dirlist rooted at /var/mobile/Media """
#	sp = AfcService(lockdown=service_provider)
#	afc_ls_proccess_dir(sp, root_item, remote_file, recursive, False)
#	
#def afc_ls_proccess_dir(sp: AfcService, root_item: QTreeWidgetItem, remote_file = '/', recursive = False, subDir = False):
#	for path in sp.dirlist(remote_file, -1 if recursive else 1):
##		print(path)
#		if(path != remote_file):
#			child1_item = QTreeWidgetItem(root_item, [path[len(remote_file) + (1 if subDir else 0):], str(human_readable_size(sp.stat(path)["st_size"])), str(sp.stat(path)["st_birthtime"])]) # 'Dir' if AfcService(lockdown=service_provider).isdir(path) else 'File'])
#			if sp.isdir(path):
#				afc_ls_proccess_dir(sp, child1_item, path, recursive, True)
				
#def itemExpanded(item):
#	if item.parent() != None:
#		print(f"Item {item.text(0)} / {item.parent().text(0)} expanded")
				
#class AFCTreeWidget(QTreeWidget):
#	def __init__(self):
#		super().__init__()
#		
#		# Create the context menu and add some actions
#		self.context_menu = QMenu(self)
#		actionShowInfos = self.context_menu.addAction("Show infos")
#		actionOpenFile = self.context_menu.addAction("Open File / Folder")
#		actionOpenFile.setEnabled(False)
#		actionCopyPath = self.context_menu.addAction("Copy Path to File/Folder")
#		self.context_menu.addSeparator()
#		actionPullFile = self.context_menu.addAction("Pull file")
#		actionPushFile = self.context_menu.addAction("Push file")
#		self.context_menu.addSeparator()
#		actionDeleteFile = self.context_menu.addAction("Delete file")
#		actionCreateDir = self.context_menu.addAction("Create directory")
#		
#		actionCopyPath.triggered.connect(self.actionCopyPath_triggered)
##		self.parent_window = self.window()
#		self.show()
#		
#	def itemSelectionChanged(self):
#		# Get the selected items
#		selected_items = self.selectedItems()
#		
#		# Check if there are any selected items
#		if selected_items:
#			# Get the first selected item
#			first_selected_item = selected_items[0]
#			
#			# Do something with the selected item
#			print(first_selected_item.text())
#			
#	def contextMenuRequested(self, point):
#		# Get the selected item model
#		selected_model = self.model()  # Get the QAbstractItemModel instance
#		
#		# Get the selected item index
#		selected_index = self.selectedIndexes()[0]  # Get the first selected index
#		
#		# Get the selected item
#		selected_item = selected_model.itemFromIndex(selected_index)  # Get the item at the index
#		
#		# Do something with the selected item
#		print(selected_item.text())
#		
#	def contextMenuEvent(self, event):
#		# Show the context menu
#		self.context_menu.exec(event.globalPos())
#		
#	def actionCopyPath_triggered(self):
#		selected_items = self.selectedItems()
#		
#		if selected_items:
#			first_selected_item = selected_items[0]
#			current_item = first_selected_item
#			path_to_copy = ("/" if current_item.text(0) != "/" else "") + current_item.text(0)
#			while current_item.parent() != None:
#				current_item = current_item.parent()
#				if current_item.text(0) != "/":
#					path_to_copy = "/" + current_item.text(0) + path_to_copy
#					
#		pyperclip.copy(path_to_copy)
#		
#		if isinstance(self.window(), QMainWindow):
#			self.window().updateStatusBar(f"Copied path: '{path_to_copy}' to clipboard ...")
#		pass

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
		self.gbConsole.layout().addWidget(self.txtConsole)
		
		self.layout().addWidget(self.gbCtrl)
		self.layout().addWidget(self.gbConsole)
		
		self.mutex = QMutex()
		self.stopEvent = QWaitCondition()

		self.thread = SubprocessThread(["find", "/", "python3"])
		self.thread.start()

#		self.textEdit.show()

		# Start a loop to check if the user wants to abort the process
		while True:
			if self.thread.stopped:
				print("Subprocess stopped")
				break
			else:
				try:
					self.exec()
				except:
					print("Subprocess exception catched")
					break
		
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
		
		