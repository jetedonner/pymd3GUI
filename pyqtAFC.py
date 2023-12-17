#!/usr/bin/env python3
import os
import pyperclip
import datetime

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3.services.afc import AfcService, AfcShell, afc_opcode_t, afc_read_dir_req_t, afc_header_t

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from pyqtHelper import human_readable_size
#from pyqtDialog import InputDialog
from helper.pyqtDialog import *
from helper.pyqtMultilineTextDialog import *
from helper.pyqtFileContentDialog import *
from helper.pyqtIconHelper import *

usbmux_address = None

interruptFCActive = False

class AFCReceiver(QObject):
#	data_received = pyqtSignal(str)
	interruptSysLog = pyqtSignal()
	
class AFCWorkerSignals(QObject):
	finished = pyqtSignal()
	sendProgressUpdate = pyqtSignal(int)
	
class AFCWorker(QRunnable):
	def __init__(self, data_receiver, root_item):
		super(AFCWorker, self).__init__()
		self.isAFCActive = False
		self.root_item = root_item
		self.data_receiver = data_receiver
		self.signals = AFCWorkerSignals()
		
	def run(self):
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
		if len(devices) <= 1:
			afc_ls(create_using_usbmux(usbmux_address=usbmux_address), self.root_item, "/", False, self.signals.sendProgressUpdate)
			
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
	
	sp.makedirs(remote_file + "/" + foldername)
	return sp.stat(remote_file + "/" + foldername)
	
def afc_ls(service_provider: LockdownClient, root_item: QTreeWidgetItem, remote_file = '/', recursive = False, sendProgressUpdate = None):
	""" perform a dirlist rooted at /var/mobile/Media """
	childCountOrig = root_item.childCount()
#	print(f"childCountOrig: {childCountOrig}")
	idx = 1
	while root_item.childCount() > 0:
		childCountCurr = root_item.childCount()
		newPrgVal = int(idx/childCountOrig*100)
#		print(f"idx: {idx}, root_item.childCount(): {childCountCurr}, childCountOrig: {childCountOrig}, newPrgVal: {newPrgVal}")
		root_item.removeChild(root_item.child(0))
		if sendProgressUpdate != None:
#			QCoreApplication.processEvents()
			sendProgressUpdate.emit(int(newPrgVal))
			QCoreApplication.processEvents()
		idx = idx + 1
		
	sp = AfcService(lockdown=service_provider)
	afc_ls_proccess_dir(sp, root_item, remote_file, recursive, False, sendProgressUpdate)
	
def afc_rm(service_provider: LockdownClient, remote_file):
	""" remove a file rooted at /var/mobile/Media """
	AfcService(lockdown=service_provider).rm(remote_file)
	
def afc_openFile(service_provider: LockdownClient, remote_file):
	""" remove a file rooted at /var/mobile/Media """
	return AfcService(lockdown=service_provider).get_file_contents(remote_file)

def afc_updateFile(service_provider: LockdownClient, remote_file, data):
	""" remove a file rooted at /var/mobile/Media """
	return AfcService(lockdown=service_provider).set_file_contents(remote_file, data)

def afc_ls_proccess_dir(sp: AfcService, root_item: QTreeWidgetItem, remote_file = '/', recursive = False, subDir = False, sendProgressUpdate = None):
#	iconFolder = QIcon(os.path.join('resources', 'folder.png'))
#	iconFile = QIcon(os.path.join('resources', 'file.png'))
	global iconFolder
	global iconFile
#	print(remote_file)
	
	listDirs = sp.listdir(remote_file)
	dirs = sp.dirlist(remote_file, -1 if recursive else 1)
	dirCount = len(listDirs) #dirs
	idx = 1
	for path in dirs:
		if(path != remote_file):
			if sendProgressUpdate != None and subDir == False:
				newPrgVal = int(idx/10*100)
				sendProgressUpdate.emit(int(newPrgVal))
				QCoreApplication.processEvents()
			if interruptFCActive:
				break
			print(path)
			print(sp.stat(path))
			sp_stat = sp.stat(path)
			child1_item = QTreeWidgetItem(root_item, [path[len(remote_file) + (1 if subDir else 0):], str(human_readable_size(sp_stat["st_size"])), formateDateTime(sp_stat["st_birthtime"]), formateDateTime(sp_stat["st_mtime"]), str(sp_stat["st_ifmt"])])
			if sp.isdir(path):
				child1_item.setIcon(0, IconHelper.getFolderIcon())
				afc_ls_proccess_dir(sp, child1_item, path, recursive, True, sendProgressUpdate)
			else:
				child1_item.setIcon(0, IconHelper.getFileIcon())
			idx += 1

def formateDateTimeString(dateTimeString):
	formatted_string = dateTimeString
	try:
		date = datetime.datetime.strptime(formatted_string, "%Y-%m-%d %H:%M:%S.%f")
		formatted_string = date.strftime("%Y-%m-%d %H:%M:%S")
	except Exception as e:
		pass
	return formatted_string

def formateDateTime(dateTimeObj):
	formatted_string = "<ERROR>"
	try:
#		date = datetime.datetime.strptime(formatted_string, "%Y-%m-%d %H:%M:%S.%f")
		formatted_string = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
	except Exception as e:
		pass
	return formatted_string

def afc_pull(service_provider: LockdownClient, remote_file, local_file):
	""" pull remote file from /var/mobile/Media """
	fileContent = AfcService(lockdown=service_provider).get_file_contents(remote_file)
	# Open file in binary write mode
	with open(f"{local_file}", "wb") as binary_file:
		binary_file.write(fileContent)
		binary_file.close()
		return True
	return False

def afc_push(service_provider: LockdownClient, local_file, remote_path):
	""" push local file into /var/mobile/Media """
#	for local_file in local_files:
	with open(local_file, mode="rb") as local_fileHandle:
#			contents = local_file.read()
		AfcService(lockdown=service_provider).set_file_contents(remote_path + "/" + os.path.basename(local_file), local_fileHandle.read())
		local_fileHandle.close()
	return True
		
class AFCTreeWidget(QTreeWidget):
	def __init__(self):
		super().__init__()
		
		# Create the context menu and add some actions
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		actionOpenFile = self.context_menu.addAction("Open File / Folder")
#		actionOpenFile.setEnabled(False)
		actionCopyPath = self.context_menu.addAction("Copy Path to File/Folder")
		self.context_menu.addSeparator()
		actionPullFile = self.context_menu.addAction("Pull file")
		actionPushFile = self.context_menu.addAction("Push file")
		self.context_menu.addSeparator()
		actionDeleteFile = self.context_menu.addAction("Delete file")
		actionCreateDir = self.context_menu.addAction("Create directory")
		self.context_menu.addSeparator()
		actionRefresh = self.context_menu.addAction("Refresh")
		
		actionOpenFile.triggered.connect(self.actionOpenFile_triggered)
		actionCopyPath.triggered.connect(self.actionCopyPath_triggered)
		actionPullFile.triggered.connect(self.actionPullFile_triggered)
		actionPushFile.triggered.connect(self.actionPushFile_triggered)
		actionDeleteFile.triggered.connect(self.actionDeleteFile_triggered)
		actionCreateDir.triggered.connect(self.actionCreateDir_triggered)
		actionRefresh.triggered.connect(self.actionRefresh_triggered)
#		self.parent_window = self.window()
		self.show()
		
	def itemSelectionChanged(self):
		selected_items = self.selectedItems()
		if selected_items:
			first_selected_item = selected_items[0]
			print(first_selected_item.text())
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
	def actionOpenFile_triggered(self):
		selected_items = self.selectedItems()
		if selected_items:
			first_selected_item = selected_items[0]
			print(first_selected_item.text(0))
			
			path_to_open = self.getPathForItem(first_selected_item)
			if path_to_open != '':
				devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
				if len(devices) <= 1:
					
					fileBytes = afc_openFile(create_using_usbmux(usbmux_address=usbmux_address), path_to_open)
					file_content = fileBytes.decode('utf-8')
					print(file_content)
					hexData = [format(byte, '02x') for byte in fileBytes]
					# Format the hexadecimal data for display
					formattedHexData = ' '.join(hexData)
					print(formattedHexData)
					
					self.window().updateStatusBar(f"Opening file '{first_selected_item.text(0)}' ...")
#					self.window().mlDialog = MultilineTextDialog("File content", f"Content of file '{first_selected_item.text(0)}'", file_content, path_to_open, self.saveFileContentCallback)
					self.window().fileContentDialog = FileContentDialog(first_selected_item.text(0), f"Content of file '{first_selected_item.text(0)}'", fileBytes, path_to_open, self.saveFileContentCallback)
					
					self.window().fileContentDialog.setModal(True)
					self.window().fileContentDialog.show()
#					self.window().mlDialog.raise_()
		
	def actionRefresh_triggered(self):
		self.window().start_workerAFC()
	
	def actionPullFile_triggered(self):
		selected_item = self.getFirstSelectedItem()
		if selected_item:
			pathToRemoteFile = self.getPathForItem(selected_item)
			if pathToRemoteFile != "":
				pathToLocalDir = QFileDialog.getExistingDirectory(None, "Select a download location", "~/", QFileDialog.Option.ShowDirsOnly)
				print(pathToLocalDir)
				if pathToLocalDir != "":
					devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
					if len(devices) <= 1:
						pathToLocalFile = pathToLocalDir + "/" + selected_item.text(0)
						if afc_pull(create_using_usbmux(usbmux_address=usbmux_address), pathToRemoteFile, pathToLocalFile):
							self.window().updateStatusBar(f"Pulled file '{selected_item.text(0)}' to '{pathToLocalFile}' successfully")
		pass
		
	def actionPushFile_triggered(self):
		selected_item = self.getFirstSelectedItem()
		if selected_item:
			pathToLocalFiles = QFileDialog.getOpenFileNames(None, "Select file(s) to push", "~/", "", "")
#			print(pathToLocalFiles)
			if len(pathToLocalFiles[0]) > 0:
				lockdown = create_using_usbmux(usbmux_address=usbmux_address)
				afcService = AfcService(lockdown=lockdown)
				remotePath = self.getPathForItem(selected_item)
				if not afcService.isdir(remotePath):
					remotePath = os.path.dirname(remotePath)
#				print("REMOTEPATH: " + remotePath)
				devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
				if len(devices) <= 1:
					iconFolder = QIcon(os.path.join('resources', 'folder.png'))
					iconFile = QIcon(os.path.join('resources', 'file.png'))
					idx = 0
					skipFilesAll = False
					overwriteFilesAll = False
					for pathToLocalFile in pathToLocalFiles[0]:
						idx += 1
#						print(pathToLocalFile)
#						print(remotePath)
						localFilename = os.path.basename(pathToLocalFile)
						skipFile = False
						if afcService.exists(remotePath + "/" + localFilename) and not overwriteFilesAll:
							if skipFilesAll:
								continue
							dlg = QMessageBox(self)
							dlg.setWindowTitle("File exists!")
							dlg.setText("The file already exists on the device! Do you want to overwrite it?")
							dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.YesToAll | QMessageBox.StandardButton.No | QMessageBox.StandardButton.NoToAll)
							dlg.setIcon(QMessageBox.Icon.Question)
							button = dlg.exec()
					
							if button == QMessageBox.StandardButton.Yes:
								print("Yes!")
							elif button == QMessageBox.StandardButton.YesToAll:
								overwriteFilesAll = True
							elif button == QMessageBox.StandardButton.NoToAll:
								print("No To All!")
								skipFilesAll = True
							else:
								print("No!")
								skipFile = True
								
						if skipFile or skipFilesAll:
							continue
						
						if afc_push(lockdown, pathToLocalFile, remotePath):
							sp_stat = afcService.stat(remotePath + "/" + localFilename)
							child1_item = QTreeWidgetItem(selected_item, [localFilename, str(human_readable_size(sp_stat["st_size"])), formateDateTime(sp_stat["st_birthtime"]), formateDateTime(sp_stat["st_mtime"]), str(sp_stat["st_ifmt"])])
							
							if afcService.isdir(remotePath + "/" + localFilename):
								child1_item.setIcon(0, iconFolder)
							else:
								child1_item.setIcon(0, iconFile)
								
							self.window().updateStatusBar(f"Pushed file '{pathToLocalFile}' to '{remotePath}' successfully")
							newProgress = int(idx / len(pathToLocalFiles[0]) * 100)
#							print(f"newProgress: {newProgress}")
							self.window().updateProgress(newProgress)
							
					self.window().handle_progressFinished()
			pass
		
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
					
					current_item = first_selected_item
					path_to_copy = ("/" if current_item.text(0) != "/" else "") + current_item.text(0)
					while current_item.parent() != None:
						current_item = current_item.parent()
						if current_item.text(0) != "/":
							path_to_copy = "/" + current_item.text(0) + path_to_copy
					
					if path_to_copy != '/':
						devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
						if len(devices) <= 1:
							afc_rm(create_using_usbmux(usbmux_address=usbmux_address), path_to_copy)
							if first_selected_item.parent() != None:
								first_selected_item.parent().removeChild(first_selected_item)
			#				wind:Pymobiledevice3GUIWindow = self.window()
			#				self.window().start_workerAFC()	
				else:
					print("No!")
					
	def getPathForItem(self, current_item: QTreeWidgetItem, withOwnItem:bool = True):
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
	
	def getFirstSelectedItem(self):
		selected_items = self.selectedItems()
		if selected_items:
			return selected_items[0]
		return None
	
	def getPathFirstSelectedItem(self):
		selected_item = self.getFirstSelectedItem()
		if selected_item:
			return self.getPathForItem(selected_item)
		return None
			
	def actionCopyPath_triggered(self):
		path_to_copy = self.getPathFirstSelectedItem()
		if path_to_copy != '':
			pyperclip.copy(path_to_copy)
			
			if isinstance(self.window(), QMainWindow):
				self.window().updateStatusBar(f"Copied path: '{path_to_copy}' to clipboard ...")
			pass
	
	def actionCreateDir_triggered(self):
		selected_item = self.getFirstSelectedItem()
		if selected_item:
			text, ok = QInputDialog().getText(self, "Enter folder name!", "Enter new folder name:", QLineEdit.EchoMode.Normal, "")
			if ok and text:
				if text != '':
					print(text)
					path_to_create_folder = self.getPathForItem(selected_item)
					if path_to_create_folder != '':
						print(path_to_create_folder)
						devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
						if len(devices) <= 1:
							sp_stat = afc_mkdir(create_using_usbmux(usbmux_address=usbmux_address), text, path_to_create_folder)
							child1_item = QTreeWidgetItem(selected_item, [text, str(human_readable_size(sp_stat["st_size"])), formateDateTime(sp_stat["st_birthtime"]), formateDateTime(sp_stat["st_mtime"]), str(sp_stat["st_ifmt"])])
	
	def saveFileContentCallback(self, success, filepath, result):
		print(f'In saveFileContentCallback => success: {success} / result: {result}')
		if(success and result != ''):
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				afc_updateFile(create_using_usbmux(usbmux_address=usbmux_address), filepath, str(result).encode("utf-8"))
				self.window().updateStatusBar(f"Saved file content to: '{filepath}' ...")
				
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
		self.tree_widget.setHeaderLabels(['File/Folder', 'Size', 'Created', 'Modified', 'Type'])
		
		self.root_item = QTreeWidgetItem(self.tree_widget, ['/', '', '/var/mobile/Media', '', ''])
		
		# Expand the root item
		self.tree_widget.expandItem(self.root_item)
		self.tree_widget.header().resizeSection(0, 256)
#		self.tree_widget.itemExpanded.connect(itemExpanded)
		self.gbBrowser.layout().addWidget(self.tree_widget)
		self.layout().addWidget(self.gbBrowser)
		
			