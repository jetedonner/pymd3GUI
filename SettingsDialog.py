#!/usr/bin/env python3

import sys
from PyQt6 import QtWidgets
from pyqtSettings import Ui_pyqtSettings

class SettingsDialog(QtWidgets.QDialog, Ui_pyqtSettings):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setupUi(self)
		
		
#app = QtWidgets.QApplication(sys.argv)
#window = MainWindow()
#window.show()
#app.exec()