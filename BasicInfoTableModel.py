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
			self.input_keys = lockdownClient.short_info.keys()
			self.input_values = lockdownClient.short_info.values()
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
				return list(self.input_keys)[row]
			elif column == 1:
				return list(self.input_values)[row]
			#elif role == Qt.ItemDataRole.BackgroundRole:
				#return QColor(Qt.GlobalColor.white)
		elif role == Qt.ItemDataRole.TextAlignmentRole:
			return Qt.AlignmentFlag.AlignLeft
		
		return None