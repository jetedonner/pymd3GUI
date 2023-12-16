#!/usr/bin/env python3

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
#from pymobiledevice3.services.afc import AfcService, AfcShell, afc_opcode_t, afc_read_dir_req_t, afc_header_t

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

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
		
class TabTunnel(QWidget):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setLayout(QVBoxLayout())
		
		self.gbCtrl = QGroupBox("Tunnel control")
		self.gbCtrl.setLayout(QVBoxLayout())
		self.layout().addWidget(self.gbCtrl)
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
		
		