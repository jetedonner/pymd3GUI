#!/usr/bin/env python3
import sys
import enum
from enum import StrEnum
import charset_normalizer

from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QComboBox, QSizePolicy, QSplitter, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import * # QTextCursor, QColor

class pyQtHEXAnTexView(QWidget):
	
	def __init__(self):
		super().__init__()
		pass