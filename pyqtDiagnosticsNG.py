#!/usr/bin/env python3

import json

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3.cli.cli_common import Command, print_json, default_json_encoder
from pymobiledevice3.services.diagnostics import DiagnosticsService

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from pyqtDeviceHelper import *

from pyqtTabBase import TabLogBase

#usbmux_address = None

def diagnostics_restart(service_provider: LockdownClient):
	""" restart device """
	DiagnosticsService(lockdown=service_provider).restart()
	
def diagnostics_shutdown(service_provider: LockdownClient):
	""" restart device """
	DiagnosticsService(lockdown=service_provider).shutdown()
	
def diagnostics_sleep(service_provider: LockdownClient):
	""" restart device """
	DiagnosticsService(lockdown=service_provider).sleep()
	
def diagnostics_info(service_provider: LockdownClient, color) -> str:
	""" get diagnostics info """
	print_json(DiagnosticsService(lockdown=service_provider).info(), colored=color)
	return DiagnosticsService(lockdown=service_provider).info()

def diagnostics_battery_single(service_provider: LockdownClient, color)-> str:
	""" get single snapshot of battery data """
	raw_info = DiagnosticsService(lockdown=service_provider).get_battery()
	print_json(raw_info, colored=color)
	return raw_info

def diagnostics_mg(service_provider: LockdownClient, keys = None, color = True) :#-> str:
	""" get MobileGestalt key values from given list. If empty, return all known. """
	print_json(DiagnosticsService(lockdown=service_provider).mobilegestalt(keys=keys), colored=color)
	return DiagnosticsService(lockdown=service_provider).mobilegestalt(keys=keys) #, colored=color

def diagnostics_ioregistry(service_provider: LockdownClient, plane = "", name = "", ioclass = "", color = True):
	""" get ioregistry info """
	print_json(DiagnosticsService(lockdown=service_provider).ioregistry(plane=plane, name=name, ioclass=ioclass),
				colored=color)
	return DiagnosticsService(lockdown=service_provider).ioregistry(plane=plane, name=name, ioclass=ioclass)

class TabDiagnosticsNG(TabLogBase):
	def __init__(self, parent=None):
		super().__init__(False, False, False, parent)
		
#		self.setLayout(QVBoxLayout())
		
		self.gbConsole.setTitle("Output")
		
		
		self.gbCtrl.setTitle("Device Mode Control")
#		self.ModeGP = QGroupBox("Device Mode Control")
#		self.ModeGP.setLayout(QHBoxLayout())
		
		
		self.cmdRestartDevice = QPushButton("Restart Device")
		self.cmdRestartDevice.setToolTip("Restart the current device in normal mode")
		
		def restartClickedHandler():
			result, lockdown = lockdownForFirstDevice()
			if result:
				diagnostics_restart(lockdown)
				self.window().updateStatusBar("Device is restarting ...")
				
		self.cmdRestartDevice.clicked.connect(restartClickedHandler)
		self.gbCtrl.layout().addWidget(self.cmdRestartDevice)
		
		self.cmdShutdownDevice = QPushButton("Shutdown Device")
		self.cmdShutdownDevice.setToolTip("Shutdown the current device (Power OFF)")
		
		def shutdownClickedHandler():
			result, lockdown = lockdownForFirstDevice()
			if result:
				diagnostics_shutdown(lockdown)
				self.window().updateStatusBar("Device is shutting down ...")
				
		self.cmdShutdownDevice.clicked.connect(shutdownClickedHandler)
		self.gbCtrl.layout().addWidget(self.cmdShutdownDevice)
		
		self.cmdSleepDevice = QPushButton("Sleep Device")
		self.cmdSleepDevice.setToolTip("Put the current device into sleep mode")
		
		def sleepClickedHandler():
			result, lockdown = lockdownForFirstDevice()
			if result:
				diagnostics_sleep(lockdown)
				self.window().updateStatusBar("Device is going to sleep ...")
				
		self.cmdSleepDevice.clicked.connect(sleepClickedHandler)
		self.gbCtrl.layout().addWidget(self.cmdSleepDevice)
		
		self.cmdEnterRecovery = QPushButton("Enter Recovery")
		
		self.cmdEnterRecovery.setToolTip("Restart the current device into recovery mode (also DFU)")
		
		def enterRecoveryClickedHandler():
			result, lockdown = lockdownForFirstDevice()
			if result:
				lockdown.enter_recovery()
				self.window().updateStatusBar("Device is going to enter recovery ...")
				
		self.cmdEnterRecovery.clicked.connect(enterRecoveryClickedHandler)
		self.gbCtrl.layout().addWidget(self.cmdEnterRecovery)
		
	def addWidgetAfterCtrl(self):
#		print("IN addWidgetAfterCtrl SubClass")
		super().addWidgetAfterCtrl()
		self.gpInfo = QGroupBox("Infos")
		self.gpInfo.setLayout(QVBoxLayout())
		
		
		def getInfosClickedHandler():
			result, lockdown = lockdownForFirstDevice()
			if result:
				my_dict = diagnostics_info(lockdown, True)
				self.txtConsole.setPlainText(json.dumps(my_dict, indent=2))
				
		self.hInfoButtonsLayout = QHBoxLayout()
		self.hInfoButtonsLayout.addStretch()
		
		self.lblQueryDevice = QLabel("Query Device:")
		self.lblQueryDevice.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.hInfoButtonsLayout.addWidget(self.lblQueryDevice, Qt.AlignmentFlag.AlignRight)
		
		self.cmdGetInfos = QPushButton("Infos")
		self.cmdGetInfos.clicked.connect(getInfosClickedHandler)
		self.cmdGetInfos.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.hInfoButtonsLayout.addWidget(self.cmdGetInfos, Qt.AlignmentFlag.AlignRight)
		
		self.cmdGetBaterry = QPushButton("Battery")
		
		def getBatteryClickedHandler():
			result, lockdown = lockdownForFirstDevice()
			if result:
				my_dict = diagnostics_battery_single(lockdown, True)
				self.txtConsole.setPlainText(json.dumps(my_dict, indent=2, default=default_json_encoder))
				
		self.cmdGetBaterry.clicked.connect(getBatteryClickedHandler)
		self.cmdGetBaterry.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.hInfoButtonsLayout.addWidget(self.cmdGetBaterry, Qt.AlignmentFlag.AlignRight)
		
		self.cmdGetMG = QPushButton("Mobile-Gestalt")
		
		def getMGClickedHandler():
			result, lockdown = lockdownForFirstDevice()
			if result:
				my_dict = diagnostics_mg(lockdown, None)
				# decoded_dict = {(key.decode() if isinstance(key, bytes) else key): ((value.decode() if isinstance(value, bytes) else value) if value != None else "") for key, value in my_dict.items()}
				self.txtConsole.setPlainText(json.dumps(my_dict, skipkeys=True, indent=2, default=default_json_encoder))
				
		self.cmdGetMG.clicked.connect(getMGClickedHandler)
		self.cmdGetMG.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.hInfoButtonsLayout.addWidget(self.cmdGetMG, Qt.AlignmentFlag.AlignRight)
		
		self.cmdGetIO = QPushButton("IO-Registry")
		
		def getIOClickedHandler():
			result, lockdown = lockdownForFirstDevice()
			if result:
				my_dict = diagnostics_ioregistry(lockdown)
				self.txtConsole.setPlainText(json.dumps(my_dict, skipkeys=True, indent=2, default=default_json_encoder))
				
		self.cmdGetIO.clicked.connect(getIOClickedHandler)
		self.cmdGetIO.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.hInfoButtonsLayout.addWidget(self.cmdGetIO, Qt.AlignmentFlag.AlignRight)
		
		self.hInfoButtonsWidget = QWidget()
		self.hInfoButtonsWidget.setLayout(self.hInfoButtonsLayout)
		self.gpInfo.layout().addWidget(self.hInfoButtonsWidget)
		self.layout().addWidget(self.gpInfo)
		pass