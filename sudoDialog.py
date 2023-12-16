#!/usr/bin/env python3

import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class PasswordDialog(QDialog):
	def __init__(self):
		super().__init__()
		
		# Set the window title to "Enter Sudo Password"
		self.setWindowTitle("Enter Sudo Password")
		
		# Create a label to display the instructions
		instructionsLabel = QLabel("Please enter your sudo password:")
#		instructionsLabel.setAlignment(Qt.AlignCenter)
		
		# Create a line edit to enter the password
		passwordEdit = QLineEdit()
		passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
		
		# Create a button to confirm the password
		confirmButton = QPushButton("Confirm")
		confirmButton.clicked.connect(self.confirmPassword)
		
		# Create a layout to arrange the widgets
		layout = QVBoxLayout()
		layout.addWidget(instructionsLabel)
		layout.addWidget(passwordEdit)
		layout.addWidget(confirmButton)
		
		# Set the layout of the dialog
		self.setLayout(layout)
		
		# Set the size of the dialog
		self.setFixedSize(300, 100)
		
		# Show the dialog
		self.show()
		
	def confirmPassword(self):
		password = self.findChild(QLineEdit).text()
		
#		password = password.encode('utf-8')
		# Use the "subprocess" module to run the "sudo" command with the entered password
		process = subprocess.Popen(
			["sudo", "-S", "echo", "Hello from root"],
			universal_newlines=True,
			stdout=subprocess.PIPE,
			stdin=subprocess.PIPE,
			stderr=subprocess.PIPE
		)
		
		# Get the output and error messages from the "sudo" command
		output, error = process.communicate(password)
		returncode = process.poll()
		
		if returncode == 0:
			self.accept()
			print(f"All OK: {output}")
		else:
			print(f"NOT OK!!!\n{error}\n{output}")
#			output, error = process.communicate(password)
#			if returncode == 0:
#				self.accept()
#				print(f"All OK: {output}")
#			else:
#				print(f"NOT OK!!! {error}")
			self.reject()
			
if __name__ == "__main__":
	# Create the application
	app = QApplication(sys.argv)
	
	# Create the dialog
	dialog = PasswordDialog()
	
	# Run the application
	sys.exit(app.exec())