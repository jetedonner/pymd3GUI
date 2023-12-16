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
		self.gbSelection.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
		
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
		self.chkNetwork = QCheckBox("Network Devices")
		# Create a button to toggle the checkbox
#		cmdRefresh = QPushButton("Refresh")
	
		# Connect the checkbox to a slot
#		chkUSB.stateChanged.connect(self.checkboxToggled)
		
		self.layChannel.addWidget(self.chkUSB)
		self.layChannel.addWidget(self.chkNetwork)
		self.gbSelection.layout().addWidget(self.widChannel)
		
		# Create a button to resize the group box
		self.resizeButton = QPushButton("Resize Group Box")
	
		# Connect the resize button to a slot
		self.resizeButton.clicked.connect(self.resizeGroupBox)
		self.gbSelection.layout().addWidget(self.resizeButton)
			
		self.gbBasic = QGroupBox("Basic Infos")
		self.gbBasic.setLayout(QHBoxLayout())
		self.gbBasic.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
		
		self.layout().addWidget(self.gbSelection)
		self.layout().addWidget(self.gbBasic)
		
		self.lblBuildVersion = QLabel("BuildVersion:")
		self.txtBuildVersion = QLineEdit()
		self.txtBuildVersion.setReadOnly(True)
#		self.gbBasic.layout().addWidget(self.lblBuildVersion)
#		self.gbBasic.layout().addWidget(self.txtBuildVersion)
		
		
		self.lblConnectionType = QLabel("ConnectionType:")
		self.txtConnectionType = QLineEdit()
		self.txtConnectionType.setReadOnly(True)
#		self.gbBasic.layout().addWidget(self.lblConnectionType)
#		self.gbBasic.layout().addWidget(self.txtConnectionType)
		
		self.tblBasicInfos = BasicInfoTableWidget(None)
		self.gbBasic.layout().addWidget(self.tblBasicInfos)
		
		self.gbSelection.setMinimumHeight(0)
		self.gbSelection.adjustSize()
		
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
#		print(f'optBasicToggled: {state}')
		if(state):
			self.tblBasicInfos.loadBasicInfoFromLockdownClient(self.lockdownClient)
		pass
		
	def optExtToggled(self, state):
#		print(f'optExtToggled: {state}')
		if(state):
#			print("LOADING EXT IBNFOS 1")
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				LockdownClientExt = create_using_usbmux(usbmux_address=usbmux_address)
				for item in LockdownClientExt.all_domains:
#					print(item)
#					item = item
					try:
						valForKey = str(lockdown_get(LockdownClientExt, "", item, True))
#						print(f'Key: {item} = {valForKey}')
						self.my_dict.update({str(item): valForKey})
					except Exception as e:
						print(item)
						self.my_dict.update({str(item): "<Error>"})
						continue
				self.tblBasicInfos.loadExtendedInfoFromLockdownClient(self.my_dict)
		pass


	def resizeGroupBox(self):
#		self.gbSelection.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
#		self.gbBasic.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
		
		# Resize the first group box to the space it needs
#		groupBox1 = self.findChild(QGroupBox, "Group Box 1")
		oldHeight = self.gbSelection.height()
		print(oldHeight)
		self.gbSelection.setMinimumHeight(0)
		self.gbSelection.resize(self.gbSelection.width(), self.gbSelection.sizeHint().height())
		newHeight = self.gbSelection.sizeHint().height()
		print(newHeight)
#		self.gbSelection.adjustSize()
	
		# Resize the second group box to fill the remaining space
#		groupBox2 = self.findChild(QGroupBox, "Group Box 2")
		print(self.gbBasic.height())
		self.gbBasic.setMinimumHeight(0)
		self.gbBasic.resize(self.gbBasic.width(), self.gbBasic.sizeHint().height() + (oldHeight - newHeight))
		
		self.gbBasic.move(self.gbBasic.x(), self.gbBasic.y() - (oldHeight - newHeight))
		
		print(self.gbBasic.sizeHint().height())
#		# Resize the group box to the space it needs
#		groupBox = self.gbSelection #self.findChild(QGroupBox)
#		groupBox.setMinimumHeight(0)
##		groupBox.setSizePolicy(QSizePolicy., <#ver#>)# (self.window().width())
#		groupBox.adjustSize()
#		groupBox.sizePolicy().setHorizontalStretch(100)
#		self.gbBasic.sizePolicy().setVerticalPolicy(QSizePolicy.Policy.Maximum)
##		self.gbBasic.adjustSize()