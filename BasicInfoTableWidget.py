#!/usr/bin/env python3

from pymobiledevice3.lockdown import LockdownClient

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy, QTableView, QWidget, QStyledItemDelegate)
from BasicInfoTableModel import BasicInfoTableModel

class SelectableTextDelegate(QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		editor = QLineEdit(parent)
		editor.setReadOnly(True)  # Make the editor read-only
		editor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		return editor
	
	def setEditorData(self, editor, index):
		value = index.model().data(index, Qt.DisplayRole)
		editor.setText(str(value))
		
class BasicInfoTableWidget(QWidget):
	def __init__(self, data):
		QWidget.__init__(self)
		
		# Getting the Model
		self.model = BasicInfoTableModel(data)
		
		# Creating a QTableView
		self.table_view = QTableView()
#		self.table_view.horizontalHeaderVisible = False
		self.table_view.verticalHeader().setVisible(False)
		self.table_view.setModel(self.model)
		
		# QTableView Headers
		self.horizontal_header = self.table_view.horizontalHeader()
#		self.vertical_header = self.table_view.verticalHeader()
		self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
#		self.vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
		self.horizontal_header.setStretchLastSection(True)
		
		# QWidget Layout
		self.main_layout = QHBoxLayout()
		size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
		
		## Left layout
		size.setHorizontalStretch(1)
		self.table_view.setSizePolicy(size)
		self.main_layout.addWidget(self.table_view)
		
		# Set the layout to the QWidget
		self.setLayout(self.main_layout)
		
		self.table_view.setItemDelegate(SelectableTextDelegate())  # Set the custom delegate
		
#		self.table_view.setItemDelegate(SelectableItemDelegate(self.table_view))
	
	def loadBasicInfoFromLockdownClient(self, lockdownClient:LockdownClient):
		self.model = BasicInfoTableModel(lockdownClient)
		self.table_view.setModel(self.model)