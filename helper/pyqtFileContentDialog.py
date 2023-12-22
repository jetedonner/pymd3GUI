#!/usr/bin/env python3

import sys
import enum
from enum import StrEnum
import charset_normalizer

from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QComboBox, QSizePolicy, QSplitter, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import * # QTextCursor, QColor

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
		self.txtMultiline.textChanged.connect(self.txtMultiline_textchanged)
		self.txtMultiline.selectionChanged.connect(self.txtMultiline_selectionchanged)
		
		self.txtMultilineHex = QTextEdit()
		self.txtMultilineHex.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
#		self.hexData = [format(byte, '02x') for byte in self.fileContent]
#		# Format the hexadecimal data for display
#		self.formattedHexData = ' '.join(self.hexData)
#		self.txtMultilineHex.setText(str.upper(self.formattedHexData))
#		self.setTextWithEncoding("utf-8")
		
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
		self.setTextWithEncoding()
	
	def txtMultiline_selectionchanged(self):
		cursor = self.txtMultiline.textCursor()
		print("Selection start: %d end: %d" % (cursor.selectionStart(), cursor.selectionEnd()))
		
		
#		# Create a text cursor
#		cursorReset = self.txtMultilineHex.textCursor()
#		
#		# Move the cursor to the beginning of the block
#		cursorReset.movePosition(QTextCursor.MoveOperation.Start, QTextCursor.MoveMode.MoveAnchor)
#		
#		# Set the cursor to the beginning of the text
##		cursorReset.moveToBlockStart()
#		
#		# Create a text block format
#		formatReset = QTextCharFormat() # QTextBlockFormat()
#		formatReset.setBackground(QColor(0, 0, 0, 0))  # Transparent background color
#		
#		# Apply the format to the text
##		cursorReset.setBlockFormat(formatReset)
#		cursorReset.setCharFormat(formatReset)
#		
#		# Set the text cursor
#		self.txtMultilineHex.setTextCursor(cursorReset)
#		self.txtMultilineHex.ensureCursorVisible()
		
		c = self.txtMultilineHex.textCursor()
		c.setPosition(cursor.selectionStart())
		c.setPosition((cursor.selectionEnd() * 3), QTextCursor.MoveMode.KeepAnchor)
#		self.txtMultilineHex.setTextCursor(c)
#		self.txtMultilineHex.ensureCursorVisible()
		color = QColor(255, 0, 0)  # Red color
		format = QTextCharFormat()
#		format.setForeground(color)
		format.setBackground(color)
		
		# Apply the format to the text
		c.setCharFormat(format)
#		# Create a new text block format
#		formatReset = QTextBlockFormat()
#		formatReset.setBackground(QColor(0, 0, 0, 0))  # Transparent background color
#		
#		# Set the text block format to the entire text
#		self.txtMultilineHex.setTextFormat(formatReset)
		
		self.txtMultilineHex.setTextCursor(c)
		self.txtMultilineHex.ensureCursorVisible()
		self.txtMultilineHex.setTextCursor(QTextCursor())
		self.txtMultilineHex.ensureCursorVisible()
#		c.setTextColor(color)
#		
#		# Create a text cursor
#		cursor = text_edit.textCursor()
#		
#		# Move the cursor to the beginning of the text
#		cursor.movePosition(QTextCursor.Start)
		
		# Set the text color
#		c.setTextColor(color)
		
#		# Get the cursor position
#		cursor_pos = self.txtMultiline.cursorPosition()
#		
#		print("Cursor position:", cursor_pos)
#		
#		if cursor_pos == 0:
#			print("No text is selected.")
#		else:
#			print("Selected text:", self.txtMultiline.toPlainText()[:cursor_pos])
		
		
		# Get the start and end positions of the selected text
#		start_pos = self.txtMultiline.selectionStart()
#		end_pos = self.txtMultiline.selectionEnd()
#		
#		print("Start position:", start_pos)
#		print("End position:", end_pos)
#		
#		if start_pos == end_pos:
#			print("No text is selected.")
#		else:
#			print("Selected text:", self.txtMultiline.toPlainText()[start_pos:end_pos])
		
	def txtMultiline_textchanged(self):
		self.setTxtHex()
		
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

	def setTxtHex(self):
		self.txtAsString = self.txtMultiline.toPlainText()
		try:
			self.txtInBytes = self.txtAsString.encode("utf-8")
			self.hexData = [format(byte, '02x') for byte in self.txtInBytes] # self.fileContent]
			# Format the hexadecimal data for display
			self.formattedHexData = ' '.join(self.hexData)
			self.txtMultilineHex.setText(str.upper(self.formattedHexData))
		except Exception as e:
			print(f"Exception: '{e}' while converting text '{self.txtAsString}' to HEX string")
			pass
		
	def setTextWithEncoding(self, encoding:str = None):
		encodingToUse = encoding
		if encodingToUse is None:
			result = charset_normalizer.detect(self.fileContent)
			if result['encoding'] is None:
				encodingToUse = "utf-8"
				print(f"No encoding detected! Using default encoding: {encodingToUse}")
			else:
				encodingToUse = str(result['encoding'])
				print(f"Detected encoding: {encodingToUse}")
			
#			if encodingToUse not in [item.text() for item in self.cmbEncoding.items()]:
#				self.cmbEncoding.addItem(encodingToUse)
			self.cmbEncoding.setCurrentText(str(encodingToUse))
		
		print("IN DIALOG ... ")
		try:
			file_content = self.fileContent.decode('utf-8')
		except Exception as e:
			file_content = f'{self.fileContent}'
			
#		print(file_content)
		self.txtMultiline.setText(file_content)
		self.setTxtHex()
		
		return
		
#		hexData = [format(byte, '02x') for byte in self.fileContent]
#		# Format the hexadecimal data for display
#		formattedHexData = ' '.join(hexData)
#		print(formattedHexData)
#		print("END IN DIALOG ... ")
#		
#		try:
#			txtDecoded = self.fileContent.decode(encodingToUse)
#			print(txtDecoded)
#			hexData = [format(byte, '02x') for byte in self.fileContent]
#			# Format the hexadecimal data for display
#			formattedHexData = ' '.join(hexData)
#			print(formattedHexData)
#			
#			self.txtMultiline.setText(txtDecoded)
#		except Exception as e:
#			print(f"Exception: '{e}' while decoding fileContent with encoding '{encoding}'")
#			pass
#		finally:
#			self.setTxtHex()
		
	def showHex_changed(self, state):
		self.splitter.widget(1).setVisible(state)
		
	def cancelAction(self):
		self.inputCallback(False, "", "")
		self.close()
		
	def confirmInput(self):
		self.inputCallback(True, self.path_to_open, self.txtMultiline.toPlainText())
		self.close()