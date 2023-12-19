#!/usr/bin/env python3

import sys
#import subprocess
import enum
from enum import StrEnum

from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QComboBox, QSizePolicy, QSplitter, QCheckBox
from PyQt6.QtCore import Qt

class Encoding(StrEnum):
	utf8 = "utf-8"
	utf16 = "utf-16"
	ascii = "ascii"
	
class FileContentDialog(QDialog):
	
	fileContent:bytes = None
	
	def __init__(self, promtTitle, promtMsg, fileContent:bytes, path_to_open, callback):
		super().__init__()
		self.inputCallback = callback
		self.path_to_open = path_to_open
		self.fileContent = fileContent
		
		self.setWindowTitle(f"{promtTitle}")
		self.setSizeGripEnabled(True)
		self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.instructionsLabel = QLabel(f"{promtMsg}")
		
		# Create a line edit to enter the password
		self.splitter = QSplitter()
		self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		
		self.txtMultiline = QTextEdit()
		self.txtMultiline.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtMultilineHex = QTextEdit()
		self.txtMultilineHex.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.hexData = [format(byte, '02x') for byte in self.fileContent]
		# Format the hexadecimal data for display
		self.formattedHexData = ' '.join(self.hexData)
		self.txtMultilineHex.setText(str.upper(self.formattedHexData))
		self.setTextWithEncoding("utf-8")
		
		# Create a button to confirm the password
		self.confirmButton = QPushButton("Save")
		self.confirmButton.clicked.connect(self.confirmInput)
		self.confirmButton.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		
		self.cancelButton = QPushButton("Close")
		self.cancelButton.clicked.connect(self.cancelAction)
		self.cancelButton.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		
		self.showHex = QCheckBox("HEX View")
		self.showHex.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.showHex.setChecked(True)
		self.showHex.stateChanged.connect(self.showHex_changed)
		
		self.cmbEncoding = QComboBox()
		self.cmbEncoding.addItem("utf-8")
		self.cmbEncoding.addItem("utf-16")
		self.cmbEncoding.addItem("ascii")
		self.cmbEncoding.currentIndexChanged.connect(self.cmbEncoding_changed)
		self.cmbEncoding.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		
		encodingLabel = QLabel(f"Encoding:")
		encodingLabel.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		layoutTop = QHBoxLayout()
		widTop = QWidget()
		widTop.setLayout(layoutTop)
		
		
		layoutTop.addWidget(self.instructionsLabel)
		
		layoutTop.addWidget(encodingLabel)
		layoutTop.addWidget(self.cmbEncoding)
		
		layoutTop.addWidget(self.showHex)
		
		layout = QVBoxLayout()
		layout.addWidget(widTop)
		self.splitter.addWidget(self.txtMultiline)
		self.splitter.addWidget(self.txtMultilineHex)
		layout.addWidget(self.splitter)
		layButtons = QHBoxLayout()
		widButtons = QWidget()
		widButtons.setLayout(layButtons)
		
		layButtons.addStretch()
		
		# Add the buttons to the layout
		layButtons.addWidget(self.confirmButton, Qt.AlignmentFlag.AlignRight)
		layButtons.addWidget(self.cancelButton, Qt.AlignmentFlag.AlignRight)
		
		layButtons.addWidget(self.confirmButton)
		layButtons.addWidget(self.cancelButton)
		
		layout.addWidget(widButtons)
		
		# Set the layout of the dialog
		self.setLayout(layout)
		
		# Set the size of the dialog
		self.setMinimumSize(720, 512)
#		self.setEnabled(True)
	
	def cmbEncoding_changed(self, currentIdx:int):
		encoding = "utf-8"
		if currentIdx == 0:
			encoding = "utf-8"
		elif currentIdx == 1:
			encoding = "utf-16"
		elif currentIdx == 2:
			encoding = "ascii"
		else:
			encoding = "utf-8"
		self.setTextWithEncoding(encoding)

	def setTextWithEncoding(self, encoding:str):
		try:
			self.txtMultiline.setText(self.fileContent.decode(encoding))
		except Exception as e:
			print(f"Exception: '{e}' while decoding fileContent with encoding '{encoding}'")
			pass
		
	def showHex_changed(self, state):
		self.splitter.widget(1).setVisible(state)
		
	def cancelAction(self):
		self.inputCallback(False, "", "")
		self.close()
		
	def confirmInput(self):
#		input = self.txtMultiline.toPlainText()
		self.inputCallback(True, self.path_to_open, self.txtMultiline.toPlainText())
		self.close()