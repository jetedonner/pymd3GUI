#!/usr/bin/env python3

import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QComboBox, QSizePolicy, QSplitter, QCheckBox
from PyQt6.QtCore import Qt

class FileContentDialog(QDialog):
	
	fileContent:bytes = None
	
	def __init__(self, promtTitle, promtMsg, content:bytes, path_to_open, callback):
		super().__init__()
		self.inputCallback = callback
		self.path_to_open = path_to_open
		self.fileContent = content
#		print("Inside init MultilineTextDialog")
		# Set the window title to "Enter Sudo Password"
		self.setWindowTitle(f"{promtTitle}")
		self.setSizeGripEnabled(True)
		# Create a label to display the instructions
		instructionsLabel = QLabel(f"{promtMsg}")
#		instructionsLabel.setAlignment(Qt.AlignCenter)
		
		# Create a line edit to enter the password
		self.splitter = QSplitter()
		self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		
		self.txtMultiline = QTextEdit()
		self.txtMultiline.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtMultilineHex = QTextEdit()
		self.txtMultilineHex.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		hexData = [format(byte, '02x') for byte in self.fileContent]
		# Format the hexadecimal data for display
		formattedHexData = ' '.join(hexData)
		self.txtMultilineHex.setText(str.upper(formattedHexData))
		self.txtMultiline.setText(content.decode("utf-8"))
#		self.InfoGP.layout().addWidget(self.textInfos)
		
#		txtInput = QLineEdit()
#		txtInput.setEchoMode(QLineEdit.EchoMode.Password)
		
		# Create a button to confirm the password
		confirmButton = QPushButton("Save")
		confirmButton.clicked.connect(self.confirmInput)
		
		cancelButton = QPushButton("Close")
		cancelButton.clicked.connect(self.cancelAction)
		
		self.showHex = QCheckBox("HEX View")
		self.showHex.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.showHex.setChecked(True)
		self.showHex.stateChanged.connect(self.showHex_changed)
#		self.layCtrl.addWidget(self.sysLogActive)
		
		self.cmbEncoding = QComboBox()
		self.cmbEncoding.addItem("utf-8")
		self.cmbEncoding.addItem("utf-16")
		self.cmbEncoding.addItem("ascii")
#		self.cmbEncoding.addItem("hex")
		self.cmbEncoding.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
#		mux = usbmux.MuxConnection.create()
#		mux.get_device_list(0.1)
#		devices = mux.devices
#		for device in devices:
#			self.combobox.addItem(device.serial)
			
		# Create a layout to arrange the widgets
		
		encodingLabel = QLabel(f"Encoding:")
		encodingLabel.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		layoutTop = QHBoxLayout()
		widTop = QWidget()
		widTop.setLayout(layoutTop)
		
		
		layoutTop.addWidget(instructionsLabel)
		layoutTop.addWidget(self.showHex)
		layoutTop.addWidget(encodingLabel)
		layoutTop.addWidget(self.cmbEncoding)
		layout = QVBoxLayout()
		layout.addWidget(widTop)
		self.splitter.addWidget(self.txtMultiline)
		self.splitter.addWidget(self.txtMultilineHex)
		layout.addWidget(self.splitter)
		layButtons = QHBoxLayout()
		widButtons = QWidget()
		widButtons.setLayout(layButtons)
		
		layButtons.addWidget(confirmButton)
		layButtons.addWidget(cancelButton)
		
		layout.addWidget(widButtons)
		
		# Set the layout of the dialog
		self.setLayout(layout)
		
		# Set the size of the dialog
		self.setFixedSize(720, 512)
		self.setEnabled(True)
		# Show the dialog
#		self.show()
#		print("After show InputDialog")
	
	def showHex_changed(self, state):
		self.splitter.widget(1).setVisible(state)
		
	def cancelAction(self):
		self.inputCallback(False, "", "")
		self.close()
		
	def confirmInput(self):
		input = self.findChild(QTextEdit).toPlainText()
		self.inputCallback(True, self.path_to_open, input)
		self.close()