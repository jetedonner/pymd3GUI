#!/usr/bin/env python3

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
#from pymobiledevice3.services.usbmux import *
from pymobiledevice3 import usbmux
from pymobiledevice3.cli.cli_common import Command, print_json, default_json_encoder
#from pymobiledevice3.services.afc import AfcService, AfcShell, afc_opcode_t, afc_read_dir_req_t, afc_header_t

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

from BasicInfoTableWidget import *

usbmux_address = None

class GeneralReceiver(QObject):
	pass
#	data_received = pyqtSignal(str)
#	interruptSysLog = pyqtSignal()
	
class GeneralWorkerSignals(QObject):
	finished = pyqtSignal(dict)
	sendProgressUpdate = pyqtSignal(int)
	
class GeneralWorker(QRunnable):
	def __init__(self, data_receiver, LockdownClientExt):
		super(GeneralWorker, self).__init__()
#		self.isAFCActive = False
		self.my_dict = {}
		self.lockdownClientExt = LockdownClientExt
#		self.root_item = root_item
		self.data_receiver = data_receiver
		self.signals = GeneralWorkerSignals()
		
	def run(self):
		QCoreApplication.processEvents()	
		self.runGeneral()
		
	def runGeneral(self):
#		QCoreApplication.processEvents()
#		if self.isAFCActive:
#			interruptFCActive = True
#			return
#		else:
#			interruptFCActive = False
#		QCoreApplication.processEvents()	
#		self.isAFCActive = True
#		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
#		if len(devices) <= 1:
#			afc_ls(create_using_usbmux(usbmux_address=usbmux_address), self.root_item, "/", False, self.signals.sendProgressUpdate)
#		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
#		if len(devices) <= 1:
#			self.window().updateStatusBar("Loading extended device infos ...")
#			LockdownClientExt = create_using_usbmux(usbmux_address=usbmux_address)
		itemsCount = len(self.lockdownClientExt.all_domains)
		idx = 0
		for item in self.lockdownClientExt.all_domains:
			idx += 1
			newPrgVal = int(idx/itemsCount*100)
			self.signals.sendProgressUpdate.emit(int(newPrgVal))
			QCoreApplication.processEvents()
			try:
				valForKey = str(lockdown_get(self.lockdownClientExt, "", item, True))
#						print(f'Key: {item} = {valForKey}')
				self.my_dict.update({str(item): valForKey})
			except Exception as e:
				self.my_dict.update({str(item): "<Error>"})
				continue
				
#			self.tblBasicInfos.loadExtendedInfoFromLockdownClient(self.my_dict)
#			newPrgVal = int(idx/itemsCount*100)
#			self.window().updateProgress(newPrgVal)
				
	#		print(f"idx: {idx}, root_item.childCount(): {childCountCurr}, childCountOrig: {childCountOrig}, newPrgVal: {newPrgVal}")
#				root_item.removeChild(root_item.child(0))
#				sendProgressUpdate.emit(int(newPrgVal))
#				QCoreApplication.processEvents()	
#		self.isAFCActive = False
#		QCoreApplication.processEvents()
		self.signals.finished.emit(self.my_dict)
		
		
	def handle_interrupGeneral(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
		pass

def lockdown_get(service_provider: LockdownClient, domain, key, color):
	""" query lockdown values by their domain and key names """
#	service_provider.get_value(domain=domain, key=key)
#	print_json(service_provider.get_value(domain=domain, key=key), colored=color)
	retVal = service_provider.get_value(domain=domain, key=key)
#	print(retVal)
	return retVal
	
	
def usbmux_list(usbmux_address: str, color: bool, usb: bool, network: bool) -> LockdownClient:
#	print("BASIC INFOS - IONHEA")
	""" list connected devices """
	connected_devices = []
	for device in usbmux.list_devices(usbmux_address=usbmux_address):
#		print("BASIC INFOS - IONHEA 123")
		udid = device.serial
		
		if usb and not device.is_usb:
			continue
		
		if network and not device.is_network:
			continue
		
		lockdown = create_using_usbmux(udid, autopair=False, connection_type=device.connection_type,
										usbmux_address=usbmux_address)
		connected_devices.append(lockdown.short_info)
		return lockdown
	return None
		
#	print_json(connected_devices, colored=color)
	
class TabGeneral(QWidget):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setLayout(QVBoxLayout())
#		print("BASIC INFOS")
		self.gbSelection = QGroupBox("Selection")
		self.gbSelection.setLayout(QHBoxLayout())
		self.gbSelection.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		
		self.layMode = QVBoxLayout()
		self.widMode = QWidget()
		self.widMode.setLayout(self.layMode)
		
		self.layChannel = QVBoxLayout()
		self.widChannel = QWidget()
		self.widChannel.setLayout(self.layChannel)
		
		# Create two radio buttons
		self.optBasic = QRadioButton("Basic")
		self.optBasic.setChecked(True)
		self.optExt = QRadioButton("Extended")
	
		# Create a button to clear the selection
#		clearButton = QPushButton("Clear Selection")
	
		# Connect the radio buttons to a slot
		self.optBasic.toggled.connect(self.optBasicToggled)
		self.optExt.toggled.connect(self.optExtToggled)
	
		# Connect the clear button to a slot
#		clearButton.clicked.connect(self.clearSelection)
	
		# Create a layout to arrange the radio buttons and the button
#		layout = QVBoxLayout()
		self.layMode.addWidget(self.optBasic)
		self.layMode.addWidget(self.optExt)
		self.gbSelection.layout().addWidget(self.widMode)
		
		# Create a checkbox
		self.chkUSB = QCheckBox("USB Devices")
		self.chkUSB.setChecked(True)
		self.chkNetwork = QCheckBox("Network Devices")
		# Create a button to toggle the checkbox
#		cmdRefresh = QPushButton("Refresh")
	
		# Connect the checkbox to a slot
#		chkUSB.stateChanged.connect(self.checkboxToggled)
		
		self.layChannel.addWidget(self.chkUSB)
		self.layChannel.addWidget(self.chkNetwork)
		self.gbSelection.layout().addWidget(self.widChannel)
		
		# Create a button to resize the group box
		self.refreshButton = QPushButton("Reload Infos")
		self.refreshButton.clicked.connect(self.refreshInfos)
		self.gbSelection.layout().addWidget(self.refreshButton)
			
		self.gbBasic = QGroupBox("Basic Infos")
		self.gbBasic.setLayout(QHBoxLayout())
		self.gbBasic.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)		
		self.layout().addWidget(self.gbSelection)
		self.layout().addWidget(self.gbBasic)
		
#		self.lblBuildVersion = QLabel("BuildVersion:")
#		self.txtBuildVersion = QLineEdit()
#		self.txtBuildVersion.setReadOnly(True)
#		
#		self.lblConnectionType = QLabel("ConnectionType:")
#		self.txtConnectionType = QLineEdit()
#		self.txtConnectionType.setReadOnly(True)
		
		self.tblBasicInfos = BasicInfoTableWidget(None)
		self.gbBasic.layout().addWidget(self.tblBasicInfos)
		
#		self.gbSelection.setMinimumHeight(0)
#		self.gbSelection.adjustSize()
		
		self.lockdownClient = usbmux_list(usbmux_address, True, True, False)
#		self.tblBasicInfos.loadBasicInfoFromLockdownClient(lockdownClient)
		self.my_dict = {}
#		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
#		if len(devices) <= 1:
#			for item in create_using_usbmux(usbmux_address=usbmux_address).all_values:
#				print(item)
#				try:
#					print(lockdown_get(create_using_usbmux(usbmux_address=usbmux_address), "", item, True))
##					self.my_dict.update({str(item): str(lockdown_get(create_using_usbmux(usbmux_address=usbmux_address), "", item, True))})
#				except Exception as e:
#					continue
				
		self.tblBasicInfos.loadBasicInfoFromLockdownClient(self.lockdownClient)
	
	def optBasicToggled(self, state):
		if(state):
			self.window().updateStatusBar("Loading basic device infos ...")
			self.lockdownClient = usbmux_list(usbmux_address, True, True, False)
			self.tblBasicInfos.loadBasicInfoFromLockdownClient(self.lockdownClient)
		pass
		
	def optExtToggled(self, state):
		if(state):
			self.my_dict = {}
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				LockdownClientExt = create_using_usbmux(usbmux_address=usbmux_address)
				self.window().updateStatusBar("Loading extended device infos ...")
				self.window().start_workerGeneral(LockdownClientExt)
#			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
#			if len(devices) <= 1:
#				self.window().updateStatusBar("Loading extended device infos ...")
#				LockdownClientExt = create_using_usbmux(usbmux_address=usbmux_address)
#				itemsCount = len(LockdownClientExt.all_domains)
#				idx = 0
#				for item in LockdownClientExt.all_domains:
#					idx += 1
#					try:
#						valForKey = str(lockdown_get(LockdownClientExt, "", item, True))
##						print(f'Key: {item} = {valForKey}')
#						self.my_dict.update({str(item): valForKey})
#					except Exception as e:
#						self.my_dict.update({str(item): "<Error>"})
#						continue
#				self.tblBasicInfos.loadExtendedInfoFromLockdownClient(self.my_dict)
#				newPrgVal = int(idx/itemsCount*100)
#				self.window().updateProgress(newPrgVal)
#		#		print(f"idx: {idx}, root_item.childCount(): {childCountCurr}, childCountOrig: {childCountOrig}, newPrgVal: {newPrgVal}")
##				root_item.removeChild(root_item.child(0))
##				sendProgressUpdate.emit(int(newPrgVal))
##				QCoreApplication.processEvents()
		pass


	def refreshInfos(self):
		
#		oldHeight = self.gbSelection.height()
#		print(oldHeight)
#		self.gbSelection.setMinimumHeight(0)
#		self.gbSelection.resize(self.gbSelection.width(), self.gbSelection.sizeHint().height())
#		newHeight = self.gbSelection.sizeHint().height()
#		print(newHeight)
#		
#		print(self.gbBasic.height())
#		self.gbBasic.setMinimumHeight(0)
#		self.gbBasic.resize(self.gbBasic.width(), self.gbBasic.sizeHint().height() + (oldHeight - newHeight))
#		self.gbBasic.move(self.gbBasic.x(), self.gbBasic.y() - (oldHeight - newHeight))		
#		print(self.gbBasic.sizeHint().height())
		pass
		