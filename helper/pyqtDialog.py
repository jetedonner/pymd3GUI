#!/usr/bin/env python3

import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt

class InputDialog(QDialog):
	def __init__(self, promtTitle, promtMsg, callback):
		super().__init__()
		self.inputCallback = callback
		print("Inside init InputDialog")
		# Set the window title to "Enter Sudo Password"
		self.setWindowTitle(f"{promtTitle}")
		
		# Create a label to display the instructions
		instructionsLabel = QLabel(f"{promtMsg}")
#		instructionsLabel.setAlignment(Qt.AlignCenter)
		
		# Create a line edit to enter the password
		txtInput = QLineEdit()
#		txtInput.setEchoMode(QLineEdit.EchoMode.Password)
		
		# Create a button to confirm the password
		confirmButton = QPushButton("Confirm")
		confirmButton.clicked.connect(self.confirmInput)
		
		cancelButton = QPushButton("Cancel")
		cancelButton.clicked.connect(self.cancelAction)
		
		# Create a layout to arrange the widgets
		layout = QVBoxLayout()
		layout.addWidget(instructionsLabel)
		layout.addWidget(txtInput)
		layButtons = QHBoxLayout()
		widButtons = QWidget()
		widButtons.setLayout(layButtons)
		
		layButtons.addWidget(confirmButton)
		layButtons.addWidget(cancelButton)
		
		layout.addWidget(widButtons)
		
		# Set the layout of the dialog
		self.setLayout(layout)
		
		# Set the size of the dialog
		self.setFixedSize(300, 150)
		self.setEnabled(True)
		# Show the dialog
#		self.show()
#		print("After show InputDialog")
	
	def cancelAction(self):
		self.inputCallback(False, "")
		self.close()
		
	def confirmInput(self):
		input = self.findChild(QLineEdit).text()
		self.inputCallback(True, input)
		self.close()