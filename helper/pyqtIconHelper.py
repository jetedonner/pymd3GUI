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
	iconRefresh = None
	
	@staticmethod
	def initIcons():
		project_root = dirname(realpath(__file__))
		resources_root = os.path.join(project_root, '..', 'resources')
#		print(project_root)
		IconHelper.iconApp = QIcon(os.path.join(resources_root, 'app_icon.png'))
		IconHelper.iconFolder = QIcon(os.path.join(resources_root, 'folder.png'))
		IconHelper.iconFile = QIcon(os.path.join(resources_root, 'file.png'))
		IconHelper.iconRefresh = QIcon(os.path.join(resources_root, 'refresh.png'))
	
	@staticmethod
	def getAppIcon():
		return IconHelper.iconApp
	
	@staticmethod
	def getFolderIcon():
		return IconHelper.iconFolder
	
	@staticmethod
	def getFileIcon():
		return IconHelper.iconFile
	
	@staticmethod
	def getRefreshIcon():
		return IconHelper.iconRefresh