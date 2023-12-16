#!/usr/bin/env python3

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
#from pymobiledevice3.services.usbmux import *
from pymobiledevice3 import usbmux
from pymobiledevice3.cli.cli_common import Command, print_json, default_json_encoder
#from pymobiledevice3.services.afc import AfcService, AfcShell, afc_opcode_t, afc_read_dir_req_t, afc_header_t

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

usbmux_address = None

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
		print(lockdown)
		
		print(lockdown.short_info.get("BuildVersion"))
		return lockdown
	return None
		
#	print_json(connected_devices, colored=color)
	
class TabGeneral(QWidget):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setLayout(QVBoxLayout())
#		print("BASIC INFOS")
		self.BasicGP = QGroupBox("Basic Infos")
		self.BasicGP.setLayout(QHBoxLayout())
		
		self.layout().addWidget(self.BasicGP)
		
		self.lblBuildVersion = QLabel("BuildVersion:")
		self.txtBuildVersion = QLineEdit()
		self.txtBuildVersion.setReadOnly(True)
		self.BasicGP.layout().addWidget(self.lblBuildVersion)
		self.BasicGP.layout().addWidget(self.txtBuildVersion)
		
		
		self.lblConnectionType = QLabel("ConnectionType:")
		self.txtConnectionType = QLineEdit()
		self.txtConnectionType.setReadOnly(True)
		self.BasicGP.layout().addWidget(self.lblConnectionType)
		self.BasicGP.layout().addWidget(self.txtConnectionType)
		
		
#		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
#		if len(devices) <= 1:
		lockdownClient = usbmux_list(usbmux_address, True, True, False)
		self.txtBuildVersion.setText(lockdownClient.short_info.get("BuildVersion"))
		self.txtConnectionType.setText(lockdownClient.short_info.get("ConnectionType"))
#		self.tree_widget = AFCTreeWidget()
#		self.tree_widget.setHeaderLabels(['File/Folder', 'Size', 'Created'])
		
#		self.root_item = QTreeWidgetItem(self.tree_widget, ['/', '', '/var/mobile/Media'])
		
		# Expand the root item
#		self.tree_widget.expandItem(self.root_item)
#		self.tree_widget.header().resizeSection(0, 256)
#		self.tree_widget.itemExpanded.connect(itemExpanded)
		
#		def contextMenuRequested(position):
#			menu = QMenu(treeWidget)
#			editAction = QAction('Edit', menu)
#			deleteAction = QAction('Delete', menu)
#			
#			editAction.triggered.connect(lambda: print('Edit menu item clicked'))
#			deleteAction.triggered.connect(lambda: print('Delete menu item clicked'))
#			
#			menu.addAction(editAction)
#			menu.addAction(deleteAction)
#			
#			menu.popup(treeWidget.mapToGlobal(position))
#			
#			# Get the selected item model
#			selected_model = treeWidget.model()  # Get the QAbstractItemModel instance
#			
#			# Get the selected item index
#			selected_index = treeWidget.selectedIndexes()[0]  # Get the first selected index
#			
#			# Get the selected item
#			selected_item = selected_model.itemFromIndex(selected_index)  # Get the item at the index
#			
#			# Do something with the selected item
#			print(selected_item.text())
			
#		self.tree_widget.customContextMenuRequested.connect(contextMenuRequested)
#		self.layout().addWidget(self.tree_widget)