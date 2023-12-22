#!/usr/bin/env python3
import subprocess
import threading
import time

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux

from PyQt6.QtCore import *
from PyQt6.QtGui import QIntValidator, QColor
from PyQt6.QtWidgets import *

from helper import pyqtIconHelper
from pyqt import *

class TabBase(QWidget):
		
	def __init__(self, parent=None):
		super().__init__(parent)
		
	def updateStatusBar(self, msg):
		self.window().statusBar.showMessage(msg)
		
	def updateProgress(self, newValue, finished = False):
		self.window().progressbar.setValue(int(newValue))
		if finished:
			self.window().handle_progressFinished()
		
class TabLogBase(TabBase):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setLayout(QVBoxLayout())
		
		self.gbCtrl = QGroupBox("Control")
		self.gbCtrl.setLayout(QHBoxLayout())

		self.gbConsole = QGroupBox("Console")
		self.gbConsole.setLayout(QVBoxLayout())
		self.gbConsole.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
	
		self.cmdClear = QPushButton()
		self.cmdClear.setIcon(pyqtIconHelper.IconHelper.getBinIcon())
		self.cmdClear.setToolTip("Clear the console")
		self.cmdClear.setIconSize(QSize(16, 16))
		self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdClear.clicked.connect(self.clear_clicked)
		self.gbConsole.layout().addWidget(self.cmdClear)
		
		self.txtConsole = QTextEdit()
		self.txtConsole.setReadOnly(True)
		self.txtConsole.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.gbConsole.layout().addWidget(self.txtConsole)

		self.layout().addWidget(self.gbCtrl)
		self.layout().addWidget(self.gbConsole)
		
	def clear_clicked(self):
		self.txtConsole.clear()