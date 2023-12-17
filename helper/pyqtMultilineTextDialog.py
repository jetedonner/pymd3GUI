#!/usr/bin/env python3

import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit
from PyQt6.QtCore import Qt

class MultilineTextDialog(QDialog):
	def __init__(self, promtTitle, promtMsg, content, path_to_open, callback):
		super().__init__()
		self.inputCallback = callback
		self.path_to_open = path_to_open
#		print("Inside init MultilineTextDialog")
		# Set the window title to "Enter Sudo Password"
		self.setWindowTitle(f"{promtTitle}")
		self.setSizeGripEnabled(True)
		# Create a label to display the instructions
		instructionsLabel = QLabel(f"{promtMsg}")
#		instructionsLabel.setAlignment(Qt.AlignCenter)
		
		# Create a line edit to enter the password
		self.txtMultiline = QTextEdit()
		self.txtMultiline.setReadOnly(False)
		self.txtMultiline.setText(content)
#		self.InfoGP.layout().addWidget(self.textInfos)
		
#		txtInput = QLineEdit()
#		txtInput.setEchoMode(QLineEdit.EchoMode.Password)
		
		# Create a button to confirm the password
		confirmButton = QPushButton("Save")
		confirmButton.clicked.connect(self.confirmInput)
		
		cancelButton = QPushButton("Close")
		cancelButton.clicked.connect(self.cancelAction)
		
		# Create a layout to arrange the widgets
		layout = QVBoxLayout()
		layout.addWidget(instructionsLabel)
		layout.addWidget(self.txtMultiline)
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
	
	def cancelAction(self):
		self.inputCallback(False, "", "")
		self.close()
		
	def confirmInput(self):
		input = self.findChild(QTextEdit).toPlainText()
		self.inputCallback(True, self.path_to_open, input)
		self.close()