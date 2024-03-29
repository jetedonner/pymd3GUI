#!/usr/bin/env python3
#import sys
from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3 import usbmux
from pymobiledevice3.cli.cli_common import Command, print_json, default_json_encoder

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

from BasicInfoTableWidget import *
from pyqtDeviceHelper import *

from pyqtTabBase import *

from QSwitch import *

usbmux_address = None

class GeneralReceiver(QObject):
	pass
#	data_received = pyqtSignal(str)
	
class GeneralWorkerSignals(QObject):
	finished = pyqtSignal(dict)
	sendProgressUpdate = pyqtSignal(int)
	
class GeneralWorker(QRunnable):
	def __init__(self, data_receiver, LockdownClientExt):
		super(GeneralWorker, self).__init__()
		self.my_dict = {}
		self.lockdownClientExt = LockdownClientExt
		self.data_receiver = data_receiver
		self.signals = GeneralWorkerSignals()
		
	def run(self):
		QCoreApplication.processEvents()	
		self.runGeneral()
		
	def runGeneral(self):
		allDom = self.lockdownClientExt.all_domains
		itemsCount = len(allDom.keys())
		idx = 0
		for item in allDom.keys():
			idx += 1
			newPrgVal = int(idx/itemsCount*100)
			self.signals.sendProgressUpdate.emit(int(newPrgVal))
			QCoreApplication.processEvents()
			daVal = allDom[item]
			try:
				valForKey = daVal
				self.my_dict.update({str(item): str(valForKey)})
			except Exception as e:
				self.my_dict.update({str(item): "<Error>"})
				continue
				
		self.signals.finished.emit(self.my_dict)
		
		
	def handle_interrupGeneral(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
		pass

def lockdown_get(service_provider: LockdownClient, domain, key, color):
	""" query lockdown values by their domain and key names """
	retVal = service_provider.get_value(domain=domain, key=key)
	return retVal
	
	
def usbmux_list(usbmux_address: str, color: bool, usb: bool, network: bool) -> LockdownClient:
	""" list connected devices """
#	connected_devices = []
#	try:
#		for device in usbmux.list_devices(usbmux_address=usbmux_address):
#			udid = device.serial
#			
#			if usb and not device.is_usb:
#				continue
#			
#			if network and not device.is_network:
#				continue
#			
#			lockdown = create_using_usbmux(udid, autopair=False, connection_type=device.connection_type,
#											usbmux_address=usbmux_address)
#			connected_devices.append(lockdown.short_info)
#			return lockdown
#	except Exception as e:
#		print(f'Error: {e}')
##		pass
#	return None
	pass
	
class TabGeneral(TabBase):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setLayout(QVBoxLayout())
		self.gbSelection = QGroupBox("Selection")
		self.gbSelection.setLayout(QHBoxLayout())
		self.gbSelection.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		
		self.layMode = QVBoxLayout()
		self.widMode = QWidget()
		self.widMode.setLayout(self.layMode)
		
		self.layChannel = QVBoxLayout()
		self.widChannel = QWidget()
		self.widChannel.setLayout(self.layChannel)

		self.optBasic = QRadioButton("Basic")
		self.optBasic.setChecked(True)
		self.optExt = QRadioButton("Extended")
	
		self.optBasic.toggled.connect(self.optBasicToggled)
		self.optExt.toggled.connect(self.optExtToggled)
	
		self.layMode.addWidget(self.optBasic)
		self.layMode.addWidget(self.optExt)
		self.gbSelection.layout().addWidget(self.widMode)
		
#		self.chkWireless = QCheckBox("Wireless On")
#		self.chkWireless.stateChanged.connect(self.wireless_changed)
#		self.layChannel.addWidget(self.chkWireless)
		
		self.swtWireless = QSwitch("Wireless On", SwitchSize.Small, SwitchLabelPos.Trailing)
		self.swtWireless.checked.connect(self.wireless_checked)
		self.layChannel.addWidget(self.swtWireless)
		
		self.gbSelection.layout().addWidget(self.widChannel)
		
#		self.refreshButton = QPushButton("Reload Infos")
#		self.refreshButton.clicked.connect(self.refreshInfos)
#		self.gbSelection.layout().addWidget(self.refreshButton)
		
		self.lblDeviceName = QLabel("Name:")
		self.lblDeviceName.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.gbSelection.layout().addWidget(self.lblDeviceName)
		self.txtDeviceName = QLineEdit("") # _mysocket
		self.gbSelection.layout().addWidget(self.txtDeviceName)
		
		self.cmdUpdateName = QPushButton("Update name")
		self.cmdUpdateName.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdUpdateName.clicked.connect(self.updateName)
		self.gbSelection.layout().addWidget(self.cmdUpdateName)
		
		self.gbBasic = QGroupBox("Basic Infos")
		self.gbBasic.setLayout(QHBoxLayout())
		self.gbBasic.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)		
		self.layout().addWidget(self.gbSelection)
		self.layout().addWidget(self.gbBasic)
		
		self.tblBasicInfos = BasicInfoTableWidget(None)
		self.gbBasic.layout().addWidget(self.tblBasicInfos)
		
#		print(f'usbmux_address: {usbmux_address}')
		self.lockdownClient = usbmux_list(usbmux_address, True, True, False)
#		self.loadData()
		self.optBasicToggled(True)
	
	def wireless_checked(self, checked):
#		print(f"CHECKED CHANGED: {checked}!!!!")
		if self.lockdownClient is not None:
			self.lockdownClient.set_value(checked, 'com.apple.mobile.wireless_lockdown', 'EnableWifiConnections')
			self.updateStatusBar(f"WirelessOn changed to {checked}")
		else:
			self.updateStatusBar(f"WirelessOn switch to {checked} failed: No connection!")
		pass
		
	def wireless_changed(self, state):
		wirelessOn = (state == 2)
		self.lockdownClient.set_value(wirelessOn, 'com.apple.mobile.wireless_lockdown', 'EnableWifiConnections')
		self.updateStatusBar(f"WirelessOn changed to {wirelessOn}")
			
	def loadData(self, loadDeviceName=True):
		self.my_dict = {}
#		print("LOAD DATA")
		if self.lockdownClient is not None:
#			print(self.lockdownClient.get_value(key='DeviceName'))
			if loadDeviceName:
				self.txtDeviceName.setText(self.lockdownClient.get_value(key='DeviceName'))
				
			strWirelessOn = self.lockdownClient.get_value('com.apple.mobile.wireless_lockdown').get('EnableWifiConnections', False)
	#		print(f'WirelessOn: {strWirelessOn}')
			self.swtWireless.setChecked(strWirelessOn)
	#		self.chkWireless.setChecked(strWirelessOn)
			self.tblBasicInfos.loadBasicInfoFromLockdownClient(self.lockdownClient)
		
	def optBasicToggled(self, state):
		QCoreApplication.processEvents()
		if(state):
			self.gbBasic.setTitle("Basic infos")
#			self.updateStatusBar("Loading basic device infos ...")
			QCoreApplication.processEvents()
#			self.lockdownClient = usbmux_list("/var/run/usbmuxd", True, True, False)
#			QCoreApplication.processEvents()
#			self.tblBasicInfos.loadBasicInfoFromLockdownClient(self.lockdownClient)
			self.my_dict = {}
			result, lockdown = lockdownForFirstDevice()
			if result:
				self.lockdownClient = lockdown
				strWirelessOn = self.lockdownClient.get_value('com.apple.mobile.wireless_lockdown').get('EnableWifiConnections', False)
		#		print(f'WirelessOn: {strWirelessOn}')
				self.swtWireless.setChecked(strWirelessOn)
				self.tblBasicInfos.loadBasicInfoFromLockdownClient(self.lockdownClient)
				QCoreApplication.processEvents()
		pass
		
	def optExtToggled(self, state):
		QCoreApplication.processEvents()
		if(state):
			self.gbBasic.setTitle("Extended infos")
			self.window().updateProgress(25)
			QCoreApplication.processEvents()
			self.my_dict = {}
			result, lockdown = lockdownForFirstDevice()
			if result:
				self.updateStatusBar("Loading extended device infos ...")
				QCoreApplication.processEvents()
				self.window().start_workerGeneral(lockdown)
		pass


	def refreshInfos(self):
		pass
		
	def updateName(self):
		if self.lockdownClient is not None:
			if self.txtDeviceName.text() != "":
				self.lockdownClient.set_value(self.txtDeviceName.text(), key='DeviceName')
				self.loadData(False)
			else:
				self.updateStatusBar("Please enter a valid name!")
		pass
		