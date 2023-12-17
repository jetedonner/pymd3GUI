"""PyMobiledevice3GUI is a simple calculator built with Python and PyQt."""

import sys
import os

from threading import Timer
from functools import partial

from pygnuutils.ls import Ls
from pygnuutils.cli.ls import ls as ls_cli
from pymobiledevice3.cli.cli_common import Command, print_json, default_json_encoder

import posixpath

from pymobiledevice3 import usbmux
from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.service_connection import LockdownServiceConnection
from pymobiledevice3.lockdown import UsbmuxLockdownClient
from typing import List, Mapping, Optional

from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3.lockdown_service_provider import LockdownServiceProvider

import time
import json

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

from pyqtGeneral import *
from pyqtAFC import *
from pyqtDiagnostics import *
from pyqtSysLog import *
from pyqtTunnel import *

from helper import *
#from helper import pyqtDialog

ERROR_MSG = "ERROR"
WINDOW_SIZE = 620
DISPLAY_HEIGHT = 35
BUTTON_SIZE = 40

AFCMAGIC = b'CFA6LPAA'

usbmux_address = None

pymobiledevice3GUIWindow = None

def create_mux(usbmux_address: Optional[str] = None) -> usbmux.MuxConnection:
    return usbmux.MuxConnection.create(usbmux_address=usbmux_address)

def list_devices(usbmux_address: Optional[str] = None) -> List[usbmux.MuxDevice]:
    mux = create_mux(usbmux_address=usbmux_address)
    mux.get_device_list(0.1)
    devices = mux.devices
    mux.close()
    return devices

class Pymobiledevice3GUIWindow(QMainWindow):
    """PyMobiledevice3GUI's main window (GUI or view)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pymd3GUI - GUI for pymobiledevice3")
        self.setFixedSize(WINDOW_SIZE * 2, WINDOW_SIZE)
        
        self.inputDialog = InputDialog("Enter folder name", "Please enter a name for the new folder", self.inputCallback)
        self.mlDialog = MultilineTextDialog("File content", "", "", "", self.inputCallback)
        self.fileContentDialog = FileContentDialog("File content", "", bytes(0), "", self.inputCallback)
        
#       self.showEvent(<#a0#>) .connect(self, Qt.SIGNAL('showEvent(QShowEvent*)'), self.onWindowShown)
#       self.connect(self, Qt.SIGNAL('loadFinished(bool)'), self.onLoadFinished)
        
         # Create the menu bar
#       menubar = QMenuBar(self)
#       # self.setMenuBar(menubar)
#
#       # Create the main menu
#       fileMenu = QMenu("pymobiledevice3 - GUI", menubar)
#       menubar.addAction(fileMenu.menuAction())
#
#       # Create menu items inside the main menu
#       newAction = QAction("New", fileMenu)
#       newAction.setShortcut("Ctrl+N")
#       fileMenu.addAction(newAction)
#
#       exitAction = QAction("Exit", fileMenu)
#       # exitAction.setShortcut("Ctrl+Q")
#       # exitAction.triggered.connect(self.close)
#       fileMenu.addAction(exitAction)
        
        self.tabWidget = QTabWidget()
        # tabWidget
        self.combobox = QComboBox()
        mux = usbmux.MuxConnection.create()
        mux.get_device_list(0.1)
        devices = mux.devices
        for device in devices:
            self.combobox.addItem(device.serial)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.topLayout = QHBoxLayout()
        self.combobox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        self.gbDevices = QGroupBox("Devices")
        self.gbDevices.setLayout(QHBoxLayout())
        self.gbDevices.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        self.gbDevices.layout().addWidget(self.combobox)
        
        self.optUSB = QRadioButton("USB")
        self.optUSB.setChecked(True)
        self.optUSB.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.gbDevices.layout().addWidget(self.optUSB)
        
        self.optNet = QRadioButton("Network")
        self.optNet.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.gbDevices.layout().addWidget(self.optNet)
        
        self.generalLayout = QVBoxLayout()
        self.buttonMap = QPushButton("TeSet")
        
        self.tabGeneral = TabGeneral()
        self.tabWidget.addTab(self.tabGeneral, "General")
        
        self.tabDiagnostics = TabDiagnostics()
        self.tabWidget.addTab(self.tabDiagnostics, "Diagnostics")

        self.tabAFC = TabAFC()
        self.tabWidget.addTab(self.tabAFC, "AFC")

        self.tabSysLog = TabSysLog()
        self.tabWidget.addTab(self.tabSysLog, "SysLog")
        
        self.tabTunnel = TabTunnel()
        self.tabWidget.addTab(self.tabTunnel, "Tunnel")
        
        self.topLayout.addWidget(self.gbDevices)

        self.topWidget = QWidget(self)
        self.topWidget.setLayout(self.topLayout)

        self.generalLayout.addWidget(self.topWidget)
        self.generalLayout.addWidget(self.tabWidget)

        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        
        self.progressbar = QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(100)
        self.progressbar.setValue(0)
        self.progressbar.setFixedWidth(100)
        # Add the progress bar to the status bar
        self.statusBar.addPermanentWidget(self.progressbar)

        self.setCentralWidget(centralWidget)

        self.sysLog_receiver = SysLogReceiver()
        self.afc_receiver = AFCReceiver()

        self.threadpool = QThreadPool()
        
        self.start_workerAFC()
        
        self.updateStatusBar("Ready...")
    
    def inputCallback(self, success, result):
        print(f'In inputCallback => success: {success} / result: {result}')
#   def showEvent(self, event):
#       print('in showEvent')
#       # Set image on QGraphicsView here, or something else that has to be done in showEvent
#       
#       # Which of these is correct ??
##       super(MainForm, self).showEvent(event)
#       super().showEvent(event)
#       self.tabGeneral.refreshInfos()
#       self.update()
#       
#   def loadFinished(self, successful):
#       print('in loadFinished')
#       # Set image on QGraphicsView here, or something else that has to be done in showEvent
#       
#       # Which of these is correct ??
##       super(MainForm, self).showEvent(event)
#       super().loadFinished(successful)
#   # Set the window title
##   self.setWindowTitle("Window Loading Example")
    
#   def onWindowShown(self, event):
#       # Perform some action when the window is shown
#       print("Window has been shown")
#       
#   def onLoadFinished(self, successful):
#       # Perform some action when the window has finished loading
#       if successful:
#           print("Window has finished loading")
#       else:
#           print("Window failed to load")
        
    def start_worker(self):
        worker = SysLogWorker(self.sysLog_receiver)
        worker.signals.finished.connect(self.handle_finished)
        worker.signals.sendSysLog.connect(self.handle_sendSysLog)
#       worker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
        
#       workerAFC = AFCWorker(self.afc_receiver, self.tabAFC.root_item)
#       workerAFC.signals.finished.connect(self.handle_finished)
#       workerAFC.signals.sendSysLog.connect(self.handle_sendSysLog)

        # Execute the worker in a separate thread
        self.threadpool.start(worker)
#       self.threadpool.start(workerAFC)

        QCoreApplication.processEvents()
    
    def start_workerAFC(self):
        workerAFC = AFCWorker(self.afc_receiver, self.tabAFC.root_item)
        workerAFC.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
        workerAFC.signals.finished.connect(self.handle_progressFinished)
        self.threadpool.start(workerAFC)
        
        QCoreApplication.processEvents()

    def handle_result(self, result):
        print(f"Received result in the main thread: {result}")
    
    def handle_progressFinished(self):
        t = Timer(1.0, self.resetProgress)
        t.start() # after 30 seconds, "hello, world" will be printed
    
    def updateProgress(self, newValue):
#       print(f"newValue: {newValue}")
        self.progressbar.setValue(int(newValue))
#       self.progressbar.repaint()
        
    def resetProgress(self):
        self.updateProgress(0)
        
    def handle_progressUpdate(self, newProgress:int):
        self.updateProgress(newProgress)
        
    def handle_finished(self):
        print("Worker finished")
        
    def handle_sendSysLog(self, text, color):
        self.tabSysLog.textLog.append(text, color)

    def updateStatusBar(self, msg):
        self.statusBar.showMessage(msg)
        self.statusBar.repaint()


class PyMobiledevice3GUI:
    """PyMobiledevice3GUI's controller class."""

    def __init__(self, view): # model, 
        # self._evaluate = model
        self._view = view

def main():
    """PyMobiledevice3GUI's main function."""
    pymobiledevice3GUIApp = QApplication([])

    # Load the icon file
    icon_path = os.path.join('resources', 'app_icon.png')
    icon = QPixmap(icon_path)
    IconHelper.initIcons()
    # Set the app icon
    pymobiledevice3GUIApp.setWindowIcon(QIcon(icon))

    pymobiledevice3GUIWindow = Pymobiledevice3GUIWindow()
    pymobiledevice3GUIWindow.show()
#   pymobiledevice3GUIWindow.tabGeneral.resizeGroupBox()
    PyMobiledevice3GUI(view=pymobiledevice3GUIWindow)

    sys.exit(pymobiledevice3GUIApp.exec())


if __name__ == "__main__":
    main()
    