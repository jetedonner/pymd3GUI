#!/usr/bin/env python3
import os
from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path



from PyQt6.QtGui import QIcon, QPixmap

#iconFolder = None # QIcon(os.path.join('resources', 'folder.png'))
#iconFile = None # QIcon(os.path.join('resources', 'file.png'))
#
#def initIcons():
#	global iconFolder
#	global iconFile
#	iconFolder = QIcon(os.path.join('resources', 'folder.png'))
#	iconFile = QIcon(os.path.join('resources', 'file.png'))

	
class IconHelper():
	
	iconApp = None
	iconFolder = None
	iconFile = None
	
	@staticmethod
	def initIcons():
		project_root = dirname(realpath(__file__))
#		print(project_root)
		IconHelper.iconApp = QIcon(QPixmap(os.path.join(project_root, '..', 'resources', 'app_icon.png')))
		IconHelper.iconFolder = QIcon(os.path.join(project_root, '..', 'resources', 'folder.png'))
		IconHelper.iconFile = QIcon(os.path.join(project_root, '..', 'resources', 'file.png'))
#		iconApp = QPixmap(icon_path)
	
	@staticmethod
	def getAppIcon():
		return IconHelper.iconApp
	
	@staticmethod
	def getFolderIcon():
		return IconHelper.iconFolder
	
	@staticmethod
	def getFileIcon():
		return IconHelper.iconFile
#initIcons()