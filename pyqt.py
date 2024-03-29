"""PyMobiledevice3GUI is a simple calculator built with Python and PyQt."""

import sys

print(sys.version)

python_helper_dir = "/Volumes/Data/dev/python/helper/ch.kimhauser.python.helper/PyQt6/"
sys.path.append(python_helper_dir)

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
from PyQt6 import uic, QtWidgets

from pyqtDeviceHelper import *

from pyqtGeneral import *
from pyqtAFC import *
#from pyqtDiagnostics import *
from pyqtDiagnosticsNG import *
from pyqtSysLog import *
from pyqtTunnel import *
from pyqtCommunication import *
#from pyqtTabBase import *
from pyqtPCap import *
from helper import *
from pyqtSettings import *
from SettingsDialog import *

DEV_MODE = True
#ERROR_MSG = "ERROR"
WINDOW_SIZE = 620
#DISPLAY_HEIGHT = 35
#BUTTON_SIZE = 40

APP_VERSION = "v0.0.1"

#AFCMAGIC = b'CFA6LPAA'

usbmux_address = '/var/run/usbmuxd' # _mysocket

pymobiledevice3GUIApp = None
pymobiledevice3GUIWindow = None

def create_mux(usbmux_address: Optional[str] = None) -> usbmux.MuxConnection:
    return usbmux.MuxConnection.create(usbmux_address=usbmux_address)

def list_devices(usbmux_address: Optional[str] = None) -> List[usbmux.MuxDevice]:
    try:
        mux = create_mux(usbmux_address=usbmux_address)
        mux.get_device_list(0.1)
        devices = mux.devices
        mux.close()
        return devices
    except Exception as e:
        print(f"Error: {e}")
    return []

class Pymobiledevice3GUIWindow(QMainWindow):
    """PyMobiledevice3GUI's main window (GUI or view)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME + " " + APP_VERSION)
        self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
#       self.setBaseSize(<#s#>)

        self.initUI()
#       # Create the menu
#       self.menubar = QtWidgets.QMenuBar()
#       self.setMenuBar(self.menubar)
#       
#       # Create the file menu
#       self.file_menu = QtWidgets.QMenu('File', self.menubar)
#       self.menubar.addMenu(self.file_menu)
#       
#       # Create the exit action
#       self.exit_action = QAction('Exit', self)
##       self.exit_action.setShortcut('Ctrl+Q')
#       self.exit_action.triggered.connect(self.quit)
#       
#       # Add the exit action to the file menu
#       self.file_menu.addAction(self.exit_action)
        
#       self._createMenuBar()
#       self._createToolBars()
        
        self.inputDialog = None # InputDialog("Enter folder name", "Please enter a name for the new folder", self.inputCallback)
        self.mlDialog = None # MultilineTextDialog("File content", "", "", "", self.inputCallback)
        self.fileContentDialog = None # FileContentDialog("File content", "", bytes(0), "", self.inputCallback)
        self.settingsDialog = None
        
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
        self.cmbDevices = QComboBox()
#       self.loadDevices()
#       mux = usbmux.MuxConnection.create()
#       mux.get_device_list(0.1)
#       devices = mux.devices
#       if len(devices) >= 1:
#           for device in devices:
#               self.cmbDevices.addItem(device.serial)
#       else:
#           self.cmbDevices.addItem("<No device connected>")

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.topLayout = QHBoxLayout()
        self.cmbDevices.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        self.lblAddress = QLabel("Usbmuxd Address:")
        self.lblAddress.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.txtAddress = QLineEdit("/var/run/usbmuxd") # _mysocket
        self.txtAddress.setReadOnly(True)
        self.txtAddress.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)
        self.txtAddress.setToolTip("Specify a usbmuxd address")
        self.txtAddress.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.cmdRefresh = QPushButton()
        self.cmdRefresh.setIcon(IconHelper.getRefreshIcon())
        self.cmdRefresh.setIconSize(QSize(16, 16))
        self.cmdRefresh.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.cmdRefresh.clicked.connect(self.refresh_clicked)
        
        self.gbDevices = QGroupBox("Devices")
        self.gbDevices.setLayout(QHBoxLayout())
        self.gbDevices.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        self.gbDevices.layout().addWidget(self.cmbDevices)
        self.gbDevices.layout().addWidget(self.cmdRefresh)
        self.gbDevices.layout().addWidget(self.lblAddress)
        self.gbDevices.layout().addWidget(self.txtAddress)
        
        self.optUSB = QRadioButton("USB")
        self.optUSB.setChecked(True)
        self.optUSB.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.gbDevices.layout().addWidget(self.optUSB)
        
        self.optNet = QRadioButton("Network")
        self.optNet.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.gbDevices.layout().addWidget(self.optNet)
        
        self.generalLayout = QVBoxLayout()
        self.buttonMap = QPushButton("Settings")
        self.buttonMap.clicked.connect(self.dialog)
        self.gbDevices.layout().addWidget(self.buttonMap)
        
        self.tabGeneral = TabGeneral()
        self.tabWidget.addTab(self.tabGeneral, "General")
        
        self.tabDiagnostics = TabDiagnosticsNG()
        self.tabWidget.addTab(self.tabDiagnostics, "Diagnostics")

        self.tabAFC = TabAFC()
        self.tabWidget.addTab(self.tabAFC, "AFC")

        self.tabSysLog = TabSysLog()
        self.tabWidget.addTab(self.tabSysLog, "SysLog")
        
        self.tabTunnel = TabTunnel()
        self.tabWidget.addTab(self.tabTunnel, "Tunnel")
        
        self.tabCommunication = TabCommunication()
        self.tabWidget.addTab(self.tabCommunication, "Communication")
        
        self.tabPcap = TabPCap()
        self.tabWidget.addTab(self.tabPcap, "PCap")
        
#       def clear_clicked(self):
#           self.txtConsole.clear()
#           super(TimestampLogger, self).log(message)
        
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
        self.general_receiver = GeneralReceiver()
        self.comm_receiver = CommReceiver()
        self.pcap_receiver = PCapReceiver()
        
        self.threadpool = QThreadPool()
        
        self.loadDevices()
        
#       self.start_workerAFC()
        
        self.updateStatusBar("Ready ...")
    
    def initUI(self):
        menubar = self.menuBar()
        
        menubar.setNativeMenuBar(True)
        # File menu
        fileMenu = menubar.addMenu('File')
        
        newAction = QAction('New', self)
        fileMenu.addAction(newAction)
        
        fileMenu.addSeparator()
        fileMenu.addAction(QAction("Settings ...", self))
        settingsMenu = fileMenu.addMenu(IconHelper.getRefreshIcon(), "Add Menu")
        settingsAction = QAction("Settings ...", self)
        settingsAction.triggered.connect(self.dialog)
        settingsMenu.addAction(settingsAction)
        settingsAction = QAction('Settings', self)
        settingsAction.triggered.connect(self.close)
        fileMenu.addAction(settingsAction)
        
        fileMenu.addSeparator()
        
        openAction = QAction('Open', self)
        fileMenu.addAction(openAction)
        
        fileMenu.addSeparator()
        
        saveAction = QAction('Save', self)
        fileMenu.addAction(saveAction)
        
        fileMenu.addSeparator()
        
#       settingsAction = QAction('Settings', self)
#       settingsAction.triggered.connect(self.close)
#       fileMenu.addAction(settingsAction)
#       
#       fileMenu.addSeparator()
        
        
        exitAction = QAction('Exit', self)
        exitAction.triggered.connect(close_application)
        fileMenu.addAction(exitAction)
        
#       fileMenu.addAction(exitAction)
#       exitAction.setMenu(fileMenu)
#       fileMenu.act
        
        # Edit menu
        editMenu = menubar.addMenu('Edit')
        
        cutAction = QAction('Cut', self)
        editMenu.addAction(cutAction)
        
        copyAction = QAction('Copy', self)
        editMenu.addAction(copyAction)
        
        pasteAction = QAction('Paste', self)
        editMenu.addAction(pasteAction)
        
    def quit(self):
        pass
        
    def loadDevices(self):
        self.updateStatusBar("Reloading devices ...")
        self.cmbDevices.clear()
        
        self.tabSysLog.sysLogActive.setChecked(False)
        self.tabSysLog.interruptSysLogThread()
        
#       self.mux = usbmux.MuxConnection.create()
#       self.mux.get_device_list(0.1)
#       self.devices = self.mux.devices
        self.devices = list_devices()
        if len(self.devices) >= 1:
            for device in self.devices:
#               print(f'{device}')
                self.cmbDevices.addItem(f'{device.serial} ({device.connection_type})')
                
            self.tabGeneral.loadData()
#           self.tabAFC.tree_widget.setEnabled(False)
            self.start_workerAFC()
        else:
            self.cmbDevices.addItem("<No device connected>")
    
    def refresh_clicked(self):
        self.updateProgress(20)
        self.updateStatusBar("Refreshing devices and infos ...")
        self.loadDevices()
        self.updateProgress(100, True)
        
    # Snip...
    def _createMenuBar(self):
        
#       #   Create the menu
#       self.menubar = QMenuBar()
#       self.setMenuBar(self.menubar)
#   
#       # Create the file menu
#       self.file_menu = QtWidgets.QMenu('File', self.menubar)
#       self.menubar.addMenu(self.file_menu)
            
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        helpMenu = menuBar.addMenu("&Help")
        
    # Snip...
    def _createToolBars(self):
        # Using a title
        fileToolBar = self.addToolBar("File")
        # Using a QToolBar object
        editToolBar = QToolBar("Edit", self)
        self.addToolBar(editToolBar)
        # Using a QToolBar object and a toolbar area
        helpToolBar = QToolBar("Help", self)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, helpToolBar)
    
    def inputCallback(self, success, result):
        print(f'In inputCallback => success: {success} / result: {result}')
        
    def start_worker(self):
        worker = SysLogWorker(self.sysLog_receiver)
        worker.signals.finished.connect(self.handle_finished)
        worker.signals.sendSysLog.connect(self.handle_sendSysLog)
        
        # Execute the worker in a separate thread
        self.threadpool.start(worker)
        QCoreApplication.processEvents()
    
    def start_workerAFC(self):
        self.updateStatusBar("Reloading filesystem ...")
        workerAFC = AFCWorker(self.afc_receiver, self.tabAFC.root_item, self.tabAFC.tree_widget)
#       workerAFC.treeWidget = self.tree_widget
        workerAFC.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
        workerAFC.signals.finished.connect(self.handle_progressFinished)
        self.threadpool.start(workerAFC)
        
        QCoreApplication.processEvents()
        
    def start_workerGeneral(self, lockdownClientExt):
        self.updateStatusBar("Reloading device infos ...")
        workerGeneral = GeneralWorker(self.general_receiver, lockdownClientExt)
        workerGeneral.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
        workerGeneral.signals.finished.connect(self.handle_finishedGeneral)
        self.threadpool.start(workerGeneral)
        
        QCoreApplication.processEvents()
        
    def start_workerComm(self):
        self.updateStatusBar("Starting communication listener ...")
        commWorker = CommWorker(self.comm_receiver)
        commWorker.signals.sendComm.connect(self.handle_sendComm)
        self.threadpool.start(commWorker)
        
        QCoreApplication.processEvents()
        
    def start_workerPCap(self):
        self.updateStatusBar("Starting pcap capturing ...")
        workerPCap = PCapWorker(self.pcap_receiver)
        workerPCap.signals.sendPCap.connect(self.handle_sendPcapLog)
#       workerAFC.treeWidget = self.tree_widget
#       workerPCap.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
#       workerPCap.signals.finished.connect(self.handle_progressFinished)
        self.threadpool.start(workerPCap)
        
        QCoreApplication.processEvents()
        
    def handle_sendComm(self, text):
        if text[0] == "<":
            self.tabCommunication.txtConsole.setTextColor(QColor("green"))
        elif text[0] == ">":
            self.tabCommunication.txtConsole.setTextColor(QColor("red"))
        else:
            self.tabCommunication.txtConsole.setTextColor(QColor("white"))
        self.tabCommunication.txtConsole.insertPlainText(text) #.append(text, color)
        if self.tabCommunication.doAutoScroll:
            self.tabCommunication.sb = self.tabCommunication.txtConsole.verticalScrollBar()
            self.tabCommunication.sb.setValue(self.tabCommunication.sb.maximum())
            

    def handle_result(self, result):
        print(f"Received result in the main thread: {result}")
    
    def handle_progressFinished(self):
        t = Timer(1.0, self.resetProgress)
        t.start() # after 30 seconds, "hello, world" will be printed
    
    def updateProgress(self, newValue, finished = False):
#       print(f"newValue: {newValue}")
        self.progressbar.setValue(int(newValue))
        if finished:
            self.handle_progressFinished()
#       self.progressbar.repaint()
        
    def resetProgress(self):
#       self.updateStatusBar("Ready ...")
        self.updateProgress(0)
        
    def handle_progressUpdate(self, newProgress:int):
        self.updateProgress(newProgress)
        
    def handle_finished(self):
        print("Worker finished")
        
    def handle_finishedGeneral(self, my_dict):
        self.tabGeneral.tblBasicInfos.loadExtendedInfoFromLockdownClient(my_dict)
        self.handle_progressFinished()
        
    def handle_sendSysLog(self, text, color):
        self.tabSysLog.textLog.append(text, color)
        
    def handle_sendPcapLog(self, text, color):
        self.tabPcap.txtConsole.append(text, color)

    def updateStatusBar(self, msg):
        self.statusBar.showMessage(msg)
#       self.statusBar.repaint()
        
    def getDeviceAddress(self) -> str:
        return self.cmbDevices.currentText()
    
#   self.btn_close.clicked.connect(self.dialog)
    
    def dialog(self):
        dialog = QDialogClass()
        dialog.exec()
            
    def pref_clicked(self):
        self.window().window = uic.loadUi("pyqtSettings.ui")
        self.window().window.show()
        
#       self.window().settingsDialog = SettingsDialog()
#       
#       self.window().settingsDialog.setModal(True)
#       self.window().settingsDialog.show()
##       ui_file = QFile("pyqtSettings.ui")
##       ui_file.open(QFile.ReadOnly)
##       
##       loader = QUiLoader()
##       window = loader.load(ui_file)
##       window.show()
        pass

TestQDialog = uic.loadUiType("pyqtSettings.ui")[0]

class QDialogClass(QtWidgets.QDialog, TestQDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        
class PyMobiledevice3GUI:
    """PyMobiledevice3GUI's controller class."""

    def __init__(self, view): # model, 
        # self._evaluate = model
        self._view = view

def close_application():
    # Stop all running tasks in the thread pool
    global pymobiledevice3GUIApp
    pymobiledevice3GUIApp.quit()

def main():
    """PyMobiledevice3GUI's main function."""
    global pymobiledevice3GUIApp
    pymobiledevice3GUIApp = QApplication([])
    pymobiledevice3GUIApp.aboutToQuit.connect(close_application)
    
    IconHelper.initIcons()
    
    # Set the app icon
    pymobiledevice3GUIApp.setWindowIcon(IconHelper.iconApp) #QIcon(icon))

    pymobiledevice3GUIWindow = Pymobiledevice3GUIWindow()
    pymobiledevice3GUIWindow.show()
    PyMobiledevice3GUI(view=pymobiledevice3GUIWindow)
    pymobiledevice3GUIApp.setQuitOnLastWindowClosed(True)
    
    # Create the icon
#   icon = QIcon("icon.png")
    
#   # Create the tray
#   tray = QSystemTrayIcon()
#   tray.setIcon(IconHelper.iconApp)
#   tray.setVisible(True)
#   
#   # Create the menu
#   menu = QMenu()
#   action = QAction("A menu item")
#   menu.addAction(action)
#   
#   # Add a Quit option to the menu.
#   quit = QAction("Quit")
#   quit.triggered.connect(pymobiledevice3GUIApp.quit)
#   menu.addAction(quit)
#   
#   # Add the menu to the tray
#   tray.setContextMenu(menu)
#   
#   menubar = QMenuBar()
#   pymobiledevice3GUIWindow.setMenuBar(menubar)
#   
#   # Create the file menu
#   file_menu = QtWidgets.QMenu('File', menubar)
#   menubar.addMenu(file_menu)
    
    sys.exit(pymobiledevice3GUIApp.exec())


if __name__ == "__main__":
    main()
    