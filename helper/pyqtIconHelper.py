#!/usr/bin/env python3
import os
from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path



from PyQt6.QtGui import QIcon

#iconFolder = None # QIcon(os.path.join('resources', 'folder.png'))
#iconFile = None # QIcon(os.path.join('resources', 'file.png'))
#
#def initIcons():
#	global iconFolder
#	global iconFile
#	iconFolder = QIcon(os.path.join('resources', 'folder.png'))
#	iconFile = QIcon(os.path.join('resources', 'file.png'))

	
class IconHelper():
	
	iconFolder = None
	iconFile = None
	
	@staticmethod
	def initIcons():
#		project_root = path.join(getcwd(), '../pyqt.py')
		project_root = dirname(realpath(__file__))
		print(project_root)
		IconHelper.iconFolder = QIcon(os.path.join(project_root, '..', 'resources', 'folder.png'))
		IconHelper.iconFile = QIcon(os.path.join(project_root, '..', 'resources', 'file.png'))
		
	@staticmethod
	def getFolderIcon():
		return IconHelper.iconFolder
	
	@staticmethod
	def getFileIcon():
		return IconHelper.iconFile
#initIcons()