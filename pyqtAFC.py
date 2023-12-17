#!/usr/bin/env python3
from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3.services.afc import AfcService, AfcShell, afc_opcode_t, afc_read_dir_req_t, afc_header_t

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

import pyperclip
import datetime

from pyqtHelper import human_readable_size
#from pyqtDialog import InputDialog
from helper.pyqtDialog import *

usbmux_address = None

interruptFCActive = False

class AFCReceiver(QObject):
#	data_received = pyqtSignal(str)
	interruptSysLog = pyqtSignal()
	
class AFCWorkerSignals(QObject):
	finished = pyqtSignal()
#	result = pyqtSignal(str)
	sendSysLog = pyqtSignal(str, str)
	
class AFCWorker(QRunnable):
	def __init__(self, data_receiver, root_item):
		super(AFCWorker, self).__init__()
		self.isAFCActive = False
		self.root_item = root_item
		self.data_receiver = data_receiver
		self.signals = AFCWorkerSignals()
		
	def run(self):
#		self.data_receiver.interruptSysLog.connect(self.handle_interruptAFC)
		QCoreApplication.processEvents()	
		self.runAFCLs()
		
	def runAFCLs(self):
		QCoreApplication.processEvents()
		if self.isAFCActive:
			interruptFCActive = True
			return
		else:
			interruptFCActive = False
		QCoreApplication.processEvents()	
		self.isAFCActive = True
		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
#		print(f"usbmux_address: {usbmux_address}")
		if len(devices) <= 1:
			afc_ls(create_using_usbmux(usbmux_address=usbmux_address), self.root_item)
#			print(f"usbmux_address: {usbmux_address}")
#			for syslog_entry in OsTraceService(lockdown=create_using_usbmux(usbmux_address=usbmux_address)).syslog(pid=-1):
##				print(syslog_entry.timestamp)
#				self.signals.sendSysLog.emit(str(syslog_entry.timestamp), "green")
#				self.signals.sendSysLog.emit(str(syslog_entry.message), "white")
#				self.signals.sendSysLog.emit(str("\n"), "white")
#				QCoreApplication.processEvents()
#				if self.isSysLogActive is False:
#					break
		self.isAFCActive = False
		QCoreApplication.processEvents()		
		self.signals.finished.emit()
		
		
	def handle_interruptAFC(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
		pass

def afc_mkdir(service_provider: LockdownClient, foldername: str, remote_file = '/'):
	""" perform a dirlist rooted at /var/mobile/Media """
	sp = AfcService(lockdown=service_provider)
	
	sp.makedirs(remote_file + foldername)
	return sp.stat(remote_file + foldername)
#	afc_ls_proccess_dir(sp, root_item, remote_file, recursive, False)
	
def afc_ls(service_provider: LockdownClient, root_item: QTreeWidgetItem, remote_file = '/', recursive = False):
	""" perform a dirlist rooted at /var/mobile/Media """
#	rootItem = self.topLevelItem(0)
	childCountOrig = root_item.childCount()
#		print(f'childCountOrig: {childCountOrig}')
#	if rAFCTreeWidget(oot_item.treeWidget())
	while root_item.childCount() > 0:
		root_item.removeChild(root_item.child(0))
		
	sp = AfcService(lockdown=service_provider)
	afc_ls_proccess_dir(sp, root_item, remote_file, recursive, False)
	
def afc_rm(service_provider: LockdownClient, remote_file):
	""" remove a file rooted at /var/mobile/Media """
	AfcService(lockdown=service_provider).rm(remote_file)
	
def afc_ls_proccess_dir(sp: AfcService, root_item: QTreeWidgetItem, remote_file = '/', recursive = False, subDir = False):
	for path in sp.dirlist(remote_file, -1 if recursive else 1):
		if(path != remote_file):
			QCoreApplication.processEvents()
			if interruptFCActive:
				break
			formatted_string = str(sp.stat(path)["st_birthtime"])
			try:
				date = datetime.datetime.strptime(formatted_string, "%Y-%m-%d %H:%M:%S.%f")
				formatted_string = date.strftime("%Y-%m-%d %H:%M:%S")
			except Exception as e:
				pass
				
			child1_item = QTreeWidgetItem(root_item, [path[len(remote_file) + (1 if subDir else 0):], str(human_readable_size(sp.stat(path)["st_size"])), formatted_string]) # 'Dir' if AfcService(lockdown=service_provider).isdir(path) else 'File'])
			if sp.isdir(path):
				afc_ls_proccess_dir(sp, child1_item, path, recursive, True)

#def itemExpanded(item):
#	if item.parent() != None:
#		print(f"Item {item.text(0)} / {item.parent().text(0)} expanded")
		
class AFCTreeWidget(QTreeWidget):
	def __init__(self):
		super().__init__()
		
		# Create the context menu and add some actions
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		actionOpenFile = self.context_menu.addAction("Open File / Folder")
		actionOpenFile.setEnabled(False)
		actionCopyPath = self.context_menu.addAction("Copy Path to File/Folder")
		self.context_menu.addSeparator()
		actionPullFile = self.context_menu.addAction("Pull file")
		actionPushFile = self.context_menu.addAction("Push file")
		self.context_menu.addSeparator()
		actionDeleteFile = self.context_menu.addAction("Delete file")
		actionCreateDir = self.context_menu.addAction("Create directory")
		self.context_menu.addSeparator()
		actionRefresh = self.context_menu.addAction("Refresh")
		
		actionCopyPath.triggered.connect(self.actionCopyPath_triggered)
		actionDeleteFile.triggered.connect(self.actionDeleteFile_triggered)
		actionCreateDir.triggered.connect(self.actionCreateDir_triggered)
		actionRefresh.triggered.connect(self.actionRefresh_triggered)
#		self.parent_window = self.window()
		self.show()
		
	def itemSelectionChanged(self):
		# Get the selected items
		selected_items = self.selectedItems()
		
		# Check if there are any selected items
		if selected_items:
			# Get the first selected item
			first_selected_item = selected_items[0]
			
			# Do something with the selected item
			print(first_selected_item.text())
			
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
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
	def actionRefresh_triggered(self):
#		wind:Pymobiledevice3GUIWindow = self.window()
		self.window().start_workerAFC()
		
	def actionDeleteFile_triggered(self):
		selected_items = self.selectedItems()
		
		if selected_items:
			first_selected_item = selected_items[0]
			if first_selected_item.text(0) != '/':
				dlg = QMessageBox(self)
				dlg.setWindowTitle(f"Delete '{first_selected_item.text(0)}'?")
				dlg.setText(f"Do you really want to delete '{first_selected_item.text(0)}'?")
				dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
				dlg.setIcon(QMessageBox.Icon.Question)
				button = dlg.exec()
		
				if button == QMessageBox.StandardButton.Yes:
					print("Yes!")
					devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
					if len(devices) <= 1:
						current_item = first_selected_item
						path_to_copy = ("/" if current_item.text(0) != "/" else "") + current_item.text(0)
						while current_item.parent() != None:
							current_item = current_item.parent()
							if current_item.text(0) != "/":
								path_to_copy = "/" + current_item.text(0) + path_to_copy
						
						if path_to_copy != '/':
							afc_rm(create_using_usbmux(usbmux_address=usbmux_address), path_to_copy)
							if first_selected_item.parent() != None:
								first_selected_item.parent().removeChild(first_selected_item)
			#				wind:Pymobiledevice3GUIWindow = self.window()
			#				self.window().start_workerAFC()	
				else:
					print("No!")
					
	def getPathForItem(self, current_item: QTreeWidgetItem):
		path_to_copy = ''
		try:
	#		current_item = first_selected_item
			path_to_copy = ("/" if current_item.text(0) != "/" else "") + current_item.text(0)
			while current_item.parent() != None:
				current_item = current_item.parent()
				if current_item.text(0) != "/":
					path_to_copy = "/" + current_item.text(0) + path_to_copy
		except Exception as e:
			pass
		return path_to_copy
	
	def actionCopyPath_triggered(self):
		selected_items = self.selectedItems()
		
		if selected_items:
			first_selected_item = selected_items[0]
			path_to_copy = self.getPathForItem(first_selected_item)		
			pyperclip.copy(path_to_copy)
			
			if isinstance(self.window(), QMainWindow):
				self.window().updateStatusBar(f"Copied path: '{path_to_copy}' to clipboard ...")
			pass
	
	def actionCreateDir_triggered(self):
		selected_items = self.selectedItems()
		if selected_items:
			first_selected_item = selected_items[0]
			print(first_selected_item.text(0))
			
			text, ok = QInputDialog().getText(self, "Enter folder name!", "Enter new folder name:", QLineEdit.EchoMode.Normal, "")
			if ok and text:
				if text != '':
					print(text)
					path_to_create_folder = self.getPathForItem(first_selected_item)
					if path_to_create_folder != '':
						devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
						if len(devices) <= 1:
							sp_stat = afc_mkdir(create_using_usbmux(usbmux_address=usbmux_address), text, path_to_create_folder)
#							QCoreApplication.processEvents()
#							if interruptFCActive:
#								break
							formatted_string = str(sp_stat["st_birthtime"])
							try:
								date = datetime.datetime.strptime(formatted_string, "%Y-%m-%d %H:%M:%S.%f")
								formatted_string = date.strftime("%Y-%m-%d %H:%M:%S")
							except Exception as e:
								pass
								
							child1_item = QTreeWidgetItem(first_selected_item, [text, str(human_readable_size(sp_stat["st_size"])), formatted_string])
#							first_selected_item.addChild(<#child#>)
#							child1_item = QTreeWidgetItem(first_selected_item, text, '', '')
				
#				textLabel.setText(text)
				
#			self.window().inputDialog = InputDialog("Enter folder name", "Please enter a name for the new folder", self.getNewFolderNameCallback)
#			self.window().inputDialog.setModal(True)
#			self.window().inputDialog.show()
#			self.window().inputDialog.raise_()
	
	def getNewFolderNameCallback(self, success, result):
		print(f'In getNewFolderNameCallback => success: {success} / result: {result}')
		if(success and result != ''):
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				afc_mkdir(create_using_usbmux(usbmux_address=usbmux_address), result, '/')
			
		
class TabAFC(QWidget):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setLayout(QVBoxLayout())
		
		self.gbBrowser = QGroupBox("Browser")
		self.gbBrowser.setLayout(QHBoxLayout())
		self.gbBrowser.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		
		self.tree_widget = AFCTreeWidget()
		self.tree_widget.setHeaderLabels(['File/Folder', 'Size', 'Created'])
		
		self.root_item = QTreeWidgetItem(self.tree_widget, ['/', '', '/var/mobile/Media'])
		
		# Expand the root item
		self.tree_widget.expandItem(self.root_item)
		self.tree_widget.header().resizeSection(0, 256)
#		self.tree_widget.itemExpanded.connect(itemExpanded)
		self.gbBrowser.layout().addWidget(self.tree_widget)
		self.layout().addWidget(self.gbBrowser)
		
			