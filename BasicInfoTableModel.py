#!/usr/bin/env python3

from pymobiledevice3.lockdown import LockdownClient

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor


class BasicInfoTableModel(QAbstractTableModel):
	def __init__(self, lockdownClient:LockdownClient = None):
		QAbstractTableModel.__init__(self)
		self.lockdownClient = lockdownClient
		self.load_data(lockdownClient)
		
	def load_data(self, lockdownClient:LockdownClient):
		if lockdownClient == None:
			self.input_keys = None
			self.input_values = None
			self.row_count = 0
		else:
#			lockdownClient.developer_mode_status
			self.input_keys = list(lockdownClient.short_info.keys())
			self.input_keys.append("developer_mode_status")
			self.input_keys.append("board_id")
			self.input_keys.append("chip_id")
			self.input_keys.append("unique_chip_id")
			self.input_keys.append("product_version")
			self.input_keys.append("date")
			self.input_keys.append("device_class")
			self.input_keys.append("display_name")
			self.input_keys.append("ecid")
			self.input_keys.append("device_public_key")
			self.input_keys.append("hardware_model")
			self.input_keys.append("host_id")
			self.input_keys.append("identifier")
#			self.input_keys.append("label")
			self.input_keys.append("language")
			self.input_keys.append("locale")
#			self.input_keys.append("logger")
			self.input_keys.append("port")
			self.input_keys.append("preflight_info")
			self.input_keys.append("service")
			self.input_keys.append("session_id")
			self.input_keys.append("system_buid")
			self.input_keys.append("udid")
			self.input_keys.append("wifi_mac_address")
			
			self.input_values = list(lockdownClient.short_info.values())
			self.input_values.append(str(lockdownClient.developer_mode_status))
			self.input_values.append(str(lockdownClient.board_id))
			self.input_values.append(str(lockdownClient.chip_id))
			self.input_values.append(str(lockdownClient.unique_chip_id))
			self.input_values.append(str(lockdownClient.product_version))
			self.input_values.append(str(lockdownClient.date))
			self.input_values.append(str(lockdownClient.device_class))
			self.input_values.append(str(lockdownClient.display_name))
			self.input_values.append(str(lockdownClient.ecid))
			self.input_values.append(str(lockdownClient.device_public_key))
			self.input_values.append(str(lockdownClient.hardware_model))
			self.input_values.append(str(lockdownClient.host_id))
			self.input_values.append(str(lockdownClient.identifier))
#			self.input_values.append(str(lockdownClient.label))
			self.input_values.append(str(lockdownClient.language))
			self.input_values.append(str(lockdownClient.locale))
#			self.input_values.append(str(lockdownClient.logger))
			self.input_values.append(str(lockdownClient.port))
			self.input_values.append(str(lockdownClient.preflight_info))
			self.input_values.append(str(lockdownClient.service))
			self.input_values.append(str(lockdownClient.session_id))
			self.input_values.append(str(lockdownClient.system_buid))
			self.input_values.append(str(lockdownClient.udid))
			self.input_values.append(str(lockdownClient.wifi_mac_address))
			self.row_count = len(self.input_values)
		self.column_count = 2
		
	def rowCount(self, parent=QModelIndex()):
		return self.row_count
	
	def columnCount(self, parent=QModelIndex()):
		return self.column_count
	
	def headerData(self, section, orientation, role):
		if role != Qt.ItemDataRole.DisplayRole:
			return None
		if orientation == Qt.Orientation.Horizontal:
			return ("Key", "Value")[section]
		else:
			return f"{section}"
		
	def data(self, index, role=Qt.ItemDataRole.DisplayRole):
		column = index.column()
		row = index.row()
		
		if role == Qt.ItemDataRole.DisplayRole:
			if column == 0:
				return self.input_keys[row]
			elif column == 1:
				return self.input_values[row]
			#elif role == Qt.ItemDataRole.BackgroundRole:
				#return QColor(Qt.GlobalColor.white)
		elif role == Qt.ItemDataRole.TextAlignmentRole:
			return Qt.AlignmentFlag.AlignLeft
		
		return None