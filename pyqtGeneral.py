#!/usr/bin/env python3

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3 import usbmux
from pymobiledevice3.cli.cli_common import Command, print_json, default_json_encoder

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

from BasicInfoTableWidget import *

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
#		self.isAFCActive = False
		self.my_dict = {}
		self.lockdownClientExt = LockdownClientExt
		self.data_receiver = data_receiver
		self.signals = GeneralWorkerSignals()
		
	def run(self):
		QCoreApplication.processEvents()	
		self.runGeneral()
		
	def runGeneral(self):
		itemsCount = len(self.lockdownClientExt.all_domains)
		idx = 0
#		print(f'AllValues: {self.lockdownClientExt.all_domains}')
		allDom = self.lockdownClientExt.all_domains
		for item in self.lockdownClientExt.all_domains.keys():
			daVal = allDom[item]
			print(f"item: {item}, key: {daVal}")
			try:
				valForKey = daVal
				#				item.keys()
#				valForKey = str(lockdown_get(self.lockdownClientExt, "", item, True))
				self.my_dict.update({str(item): str(valForKey)})
			except Exception as e:
				self.my_dict.update({str(item): "<Error>"})
				continue
#		for item in self.lockdownClientExt.all_domains:
#			idx += 1
#			newPrgVal = int(idx/itemsCount*100)
#			self.signals.sendProgressUpdate.emit(int(newPrgVal))
#			QCoreApplication.processEvents()
#			try:
##				item.keys()
#				valForKey = str(lockdown_get(self.lockdownClientExt, "", item, True))
#				self.my_dict.update({str(item): valForKey})
#			except Exception as e:
#				self.my_dict.update({str(item): "<Error>"})
#				continue
				
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
	connected_devices = []
	for device in usbmux.list_devices(usbmux_address=usbmux_address):
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
	
class TabGeneral(QWidget):
	
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
		
		self.chkUSB = QCheckBox("USB Devices")
		self.chkUSB.setChecked(True)
		self.chkNetwork = QCheckBox("Network Devices")

		self.layChannel.addWidget(self.chkUSB)
		self.layChannel.addWidget(self.chkNetwork)
		self.gbSelection.layout().addWidget(self.widChannel)
		
		self.refreshButton = QPushButton("Reload Infos")
		self.refreshButton.clicked.connect(self.refreshInfos)
		self.gbSelection.layout().addWidget(self.refreshButton)
			
		self.gbBasic = QGroupBox("Basic Infos")
		self.gbBasic.setLayout(QHBoxLayout())
		self.gbBasic.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)		
		self.layout().addWidget(self.gbSelection)
		self.layout().addWidget(self.gbBasic)
		
		self.tblBasicInfos = BasicInfoTableWidget(None)
		self.gbBasic.layout().addWidget(self.tblBasicInfos)
		
		self.lockdownClient = usbmux_list(usbmux_address, True, True, False)
#		self.tblBasicInfos.loadBasicInfoFromLockdownClient(lockdownClient)
		self.my_dict = {}
				
		self.tblBasicInfos.loadBasicInfoFromLockdownClient(self.lockdownClient)
	
	def optBasicToggled(self, state):
		QCoreApplication.processEvents()
		if(state):
			self.window().updateStatusBar("Loading basic device infos ...")
			self.lockdownClient = usbmux_list(usbmux_address, True, True, False)
			QCoreApplication.processEvents()
			self.tblBasicInfos.loadBasicInfoFromLockdownClient(self.lockdownClient)
		pass
		
	def optExtToggled(self, state):
		QCoreApplication.processEvents()
		if(state):
			self.my_dict = {}
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				LockdownClientExt = create_using_usbmux(usbmux_address=usbmux_address)
				QCoreApplication.processEvents()
				self.window().updateStatusBar("Loading extended device infos ...")
				self.window().start_workerGeneral(LockdownClientExt)
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
		