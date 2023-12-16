#!/usr/bin/env python3

from pymobiledevice3.lockdown import LockdownClient

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor


class ExtendedInfoTableModel(QAbstractTableModel):
	def __init__(self, data:dict = None):
		QAbstractTableModel.__init__(self)
		self.data = data
		self.load_data(data)
		
	def load_data(self, data:dict = None):
		if data == None:
			self.input_keys = None
			self.input_values = None
			self.data = None
			self.row_count = 0
		else:
			self.input_keys = data.keys() # lockdownClient.all_domains # lockdownClient.short_info.keys() # ["BuildVersion", "Name"]
			self.input_values = data.values() # lockdownClient.all_values # .all_values # lockdownClient.short_info.values() # ["KJGHER", "iPhone 14.6"]
			self.row_count = len(self.input_values)
		self.column_count = 2 # Key / Value
		
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
				date = list(self.input_keys)[row] #.toPython()
				return str(date)#[:-3]
			elif column == 1:
				#print(f"GETTING VALUE {list(self.input_values)[row]} / {self.lockdownClient.get_value(list(self.input_keys)[row], list(self.input_keys)[row])}")
#				return self.lockdownClient.get_value("", list(self.input_keys)[row])
				return self.data.get(list(self.input_keys)[row]) # [list(self.input_keys)[row]]
			#elif role == Qt.ItemDataRole.BackgroundRole:
				#return QColor(Qt.GlobalColor.white)
		elif role == Qt.ItemDataRole.TextAlignmentRole:
			return Qt.AlignmentFlag.AlignLeft
		
		return None