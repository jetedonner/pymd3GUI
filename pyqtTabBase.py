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

from QSwitch import *

class MyComboBoxStyledItemDelegate(QStyledItemDelegate):
	pass
#	def paint(self, painter, option, index):
#		print("paint ...")
#		# Check if the item is focused
#		if option.state & QStyle.StateFlag.State_HasFocus:
#			# Disable focus rectangle
#			print("Has focus ...")
#			painter.setBrush(Qt.BrushStyle.NoBrush)
#			
#		# Otherwise, use the default paint method
#		super().paint(painter, option, index)
#		painter.end()
		
		
class LoggingOutput(QTextEdit):
	
	def __init__(self, parent=None):
		super(LoggingOutput, self).__init__(parent)
		self.setReadOnly(True)
		self.document().setMaximumBlockCount(4096)
		# self.setLineWrapMode(self.NoWrap)
		self.insertPlainText("")
		self.doAutoScroll = True
		self.sb = self.verticalScrollBar()
		
	@pyqtSlot(bool)
	def updateAutoScroll(self, doAutoScroll):
		self.doAutoScroll = doAutoScroll
		
	@pyqtSlot(str, str)
	def append(self, text, color):
		self.setTextColor(QColor(color))
		self.insertPlainText(text)
		if self.doAutoScroll:
			self.sb.setValue(self.sb.maximum())
			
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
	
#	autoScrollConsole = True
	
#	toggleActiveVisible:bool = False
#	toggleAutoscrollVisible:bool = False
#	swtCapture = None
	
	@property
	def toggleActiveVisible(self):
		return self._toggleActiveVisible
	
	@toggleActiveVisible.setter
	def toggleActiveVisible(self, new_toggleActiveVisible):
		self._toggleActiveVisible = new_toggleActiveVisible
		self.swtCapture.setHidden(not new_toggleActiveVisible)
#		self.hideCtrl()
#		self.formatHexString()
	
	@property
	def toggleAutoscrollVisible(self):
		return self._toggleAutoscrollVisible
	
	@toggleAutoscrollVisible.setter
	def toggleAutoscrollVisible(self, new_toggleAutoscrollVisible):
		self._toggleAutoscrollVisible = new_toggleAutoscrollVisible
		self.swtAutoScroll.setHidden(not new_toggleAutoscrollVisible)
#		self.hideCtrl()
	
	@property
	def toggleClearVisible(self):
		return self._toggleClearVisible
	
	@toggleClearVisible.setter
	def toggleClearVisible(self, new_toggleClearVisible):
		self._toggleClearVisible = new_toggleClearVisible
		self.cmdClear.setHidden(not new_toggleClearVisible)
#		self.hideCtrl()
		
	def hideCtrl(self):
		if not self.toggleActiveVisible and not self.toggleAutoscrollVisible and not self.toggleClearVisible:
			self.widConcoleCtrl.setHidden(True)
		
	def __init__(self, toggleActiveVisible:bool = True, toggleAutoscrollVisible:bool = True, toggleClearVisible:bool = True, parent=None):
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
		self.cmdClear.setHidden(not toggleClearVisible)
		
		self.layConcoleCtrl = QHBoxLayout()
		self.widConcoleCtrl = QWidget()
		self.widConcoleCtrl.setLayout(self.layConcoleCtrl)
		
		
		self.swtCapture = QSwitch("Capture traffic", SwitchSize.Small, SwitchLabelPos.Trailing)
		self.swtCapture.checked.connect(self.capture_checked)
		self.layConcoleCtrl.addWidget(self.swtCapture)
		self.swtCapture.setHidden(not toggleActiveVisible)
#		print(f'self.swtCapture.getHidden(): {self.swtCapture.isHidden()}')
		
		self.swtAutoScroll = QSwitch("Autoscroll", SwitchSize.Small, SwitchLabelPos.Trailing)
		self.swtAutoScroll.checked.connect(self.autoscroll_checked)
		self.layConcoleCtrl.addWidget(self.swtAutoScroll)
		self.swtAutoScroll.setHidden(not toggleAutoscrollVisible)
#		print(f'self.swtAutoScroll.getHidden(): {self.swtAutoScroll.isHidden()} / toggleAutoscrollVisible: {toggleAutoscrollVisible}')
		
		self.layConcoleCtrl.addStretch()
		
		self.layConcoleCtrl.addWidget(self.cmdClear)
		self.gbConsole.layout().addWidget(self.widConcoleCtrl)
		
		self.txtConsole = LoggingOutput()
		self.txtConsole.setReadOnly(True)
		self.txtConsole.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.gbConsole.layout().addWidget(self.txtConsole)

		self.layout().addWidget(self.gbCtrl)
		self.addWidgetAfterCtrl()
		self.layout().addWidget(self.gbConsole)
		
		self.toggleActiveVisible = toggleActiveVisible
		self.toggleAutoscrollVisible = toggleAutoscrollVisible
		self.toggleClearVisible = toggleClearVisible
		self.hideCtrl()
		
	def capture_checked(self, checked):
		pass
		
	def autoscroll_checked(self, checked):
		self.txtConsole.updateAutoScroll(checked)
		
	def clear_clicked(self):
		self.txtConsole.clear()
		
	def addWidgetAfterCtrl(self):
#		print("IN addWidgetAfterCtrl ParentClass")
		pass