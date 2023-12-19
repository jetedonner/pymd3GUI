#!/usr/bin/env python3

import os

from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path

from PyQt6.QtGui import QIcon #, QPixmap
	
class IconHelper():
	
	iconApp = None
	iconFolder = None
	iconFile = None
	
	@staticmethod
	def initIcons():
		project_root = dirname(realpath(__file__))
#		print(project_root)
		IconHelper.iconApp = QIcon(os.path.join(project_root, '..', 'resources', 'app_icon.png'))
		IconHelper.iconFolder = QIcon(os.path.join(project_root, '..', 'resources', 'folder.png'))
		IconHelper.iconFile = QIcon(os.path.join(project_root, '..', 'resources', 'file.png'))
	
	@staticmethod
	def getAppIcon():
		return IconHelper.iconApp
	
	@staticmethod
	def getFolderIcon():
		return IconHelper.iconFolder
	
	@staticmethod
	def getFileIcon():
		return IconHelper.iconFile