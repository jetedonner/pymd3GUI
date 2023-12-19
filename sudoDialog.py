#!/usr/bin/env python3

import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt

import socket
import threading
import time
import logging
import xml.etree.ElementTree as ET
import re

def printPrettified(text, request = False, callback = None):
	sRet = extractXML(text, request)
	if callback != None:
		callback(sRet)
		
	pass
	
def extractXML(text, request = True):
	
#   text = b'\x04\x02\x00\x00\x01\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n\t<key>ClientVersionString</key>\n\t<string>qt4i-usbmuxd</string>\n\t<key>DeviceID</key>\n\t<integer>3</integer>\n\t<key>MessageType</key>\n\t<string>Connect</string>\n\t<key>PortNumber</key>\n\t<integer>32498</integer>\n\t<key>ProgName</key>\n\t<string>pymobiledevice3</string>\n\t<key>kLibUSBMuxVersion</key>\n\t<integer>3</integer>\n</dict>\n</plist>\n'
	sRet = ""
	pattern = re.compile(r'<plist version="1.0">(.*?)</plist>', flags=re.DOTALL)
	match = pattern.search(text)
	
	if match:
		plist_data = match.group(1)
		new_text = str(plist_data).replace("\\n", "\n")
		new_text = str(new_text).replace("\\t", "    ")
		
#       print("\n\n\nNew line:")
#       print(f"{new_text}")
#       print("\n\n\nNew line (prettified):")
		if request:
			print("\nREQUEST:")
			sRet += "\nREQUEST:"
		else:
			print("ANSWERE:")
			sRet += "\nANSWERE:"
			
		prtfied = prettify_xml(f'{new_text}').expandtabs(4)
		print(prtfied)
		sRet += prtfied
		
		if not request:
			print("\n\n")
			sRet += "\n\n"
		else:
			print("\n")
			sRet += "\n"
			
	else:
		print("No match found")
		sRet += "No match found"
		
	return sRet

def prettify_xml(xml_string):
	tree = ET.fromstring(xml_string)
	xml_pretty = ET.tostring(tree, encoding='utf-8', method='html') #, pretty_print=True)
	
	def fix_indent(indented_xml):
		lines = ""
		if isinstance(indented_xml, str):
#           lines = indented_xml.split('\n')
			lines = indented_xml.split('\n')
		else:
			lines = indented_xml.decode("utf-8").split('\n')
#           lines = indented_xml.split('\n')
		fixed_lines = []
		
		for line in lines:
			if line.startswith('  '):
				fixed_lines.append('\t' + line[3:])
			else:
				fixed_lines.append(line)
				
		fixed_indented_xml = '\n'.join(fixed_lines)
		return fixed_indented_xml
	
	indent_xml = fix_indent(xml_pretty)
	return indent_xml

class USBMuxdProxyListener:
	def __init__(self, callback):
		self.callback = callback
		self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind("/var/run/usbmuxd")
		self.server.listen(1)
		
		self.client = None
		self.client_thread = None
		
		self.real_usbmuxd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.real_usbmuxd.connect("/var/run/usbmux_real")
		
		self.read_thread = threading.Thread(target=self.read_real_usbmuxd_data)
#       self.read_thread.start()
		
	def accept(self):
		client, address = self.server.accept()
		self.client = client
		self.client_thread = threading.Thread(target=self.handle_client)
		self.client_thread.start()
		
	def handle_client(self):
		while True:
			try:
				data = self.client.recv(1024)
				
				if data != b'':
					log.info(f"Data (handle_client): {data}")
	#               prettify_xml(f'{data}')
					extractXML(f'{data}', True, self.callback)
	#               extractXML(data)
					
				if not data:
					time.sleep(0.01)
					continue
				
				self.real_usbmuxd.sendall(data)
			except Exception as e:
				log.error("Failed to read data from real USBMuxd daemon (handle_client):", e)
				continue
			
		log.info("Client disconnected")
		self.client.close()
		self.client = None
		self.client_thread = None
		
	def read_real_usbmuxd_data(self):
		while True:
			try:
				data = self.real_usbmuxd.recv(1024)
				
				if data != b'':
#                   log.info(f"Data (read_real_usbmuxd_data): {data}")
#                   prettify_xml(f'{data}')
					extractXML(f'{data}', False, self.callback)
#                   extractXML(data)
					
				if not data:
					time.sleep(0.01)
					continue
				
				self.client.sendall(data)
			except Exception as e:
				log.error("Failed to read data from real USBMuxd daemon (read_real_usbmuxd_data):", e)
				continue
			
#   def start(self):
#       if self.read_thread is not None:
#           raise RuntimeError("read_thread already running")
#           
#       self.read_thread = threading.Thread(target=self.read_real_usbmuxd_data)
#       self.read_thread.daemon = True
#       self.read_thread.start()
			
	def start(self):
		self.read_thread.start()
		
		while True:
			log.info("Waiting for client connection")
			self.accept()
			
			time.sleep(0.01)
			
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
		
		self.txtLog = QTextEdit()
		
		# Create a button to confirm the password
		confirmButton = QPushButton("Confirm")
		confirmButton.clicked.connect(self.confirmPassword)
		
		# Create a layout to arrange the widgets
		layout = QVBoxLayout()
		layout.addWidget(instructionsLabel)
		layout.addWidget(passwordEdit)
		layout.addWidget(self.txtLog)
		
		layout.addWidget(confirmButton)
		
		# Set the layout of the dialog
		self.setLayout(layout)
		
		# Set the size of the dialog
		self.setFixedSize(600, 400)
		
		# Show the dialog
		self.show()
		
	def logTxt(self, txt):
		self.txtLog.insertPlainText(txt)
		
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