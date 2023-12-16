#!/usr/bin/env python3

import json

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3.cli.cli_common import Command, print_json, default_json_encoder
from pymobiledevice3.services.diagnostics import DiagnosticsService

from PyQt6.QtWidgets import *

usbmux_address = None

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

class TabDiagnostics(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.setLayout(QVBoxLayout())
		
		self.ModeGP = QGroupBox("Device Mode Control")
		self.ModeGP.setLayout(QHBoxLayout())
		
		self.cmdRestartDevice = QPushButton("Restart Device")
		
		def restartClickedHandler():
			# usbmux_address = None
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				diagnostics_restart(create_using_usbmux(usbmux_address=usbmux_address))
				# print("Device is restarting ...")
				self.window().updateStatusBar("Device is restarting ...")
				
		self.cmdRestartDevice.clicked.connect(restartClickedHandler)
		self.ModeGP.layout().addWidget(self.cmdRestartDevice)
		
		self.cmdShutdownDevice = QPushButton("Shutdown Device")
		
		def shutdownClickedHandler():
			# usbmux_address = None
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				diagnostics_shutdown(create_using_usbmux(usbmux_address=usbmux_address))
				# print("Device is shutting down ...")
				self.window().updateStatusBar("Device is shutting down ...")
				
		self.cmdShutdownDevice.clicked.connect(shutdownClickedHandler)
		self.ModeGP.layout().addWidget(self.cmdShutdownDevice)
		
		self.cmdSleepDevice = QPushButton("Sleep Device")
		
		def sleepClickedHandler():
			# usbmux_address = None
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				diagnostics_sleep(create_using_usbmux(usbmux_address=usbmux_address))
				# print("Device is shutting down ...")
				self.window().updateStatusBar("Device is going to sleep ...")
				
		self.cmdSleepDevice.clicked.connect(sleepClickedHandler)
		self.ModeGP.layout().addWidget(self.cmdSleepDevice)
		
		self.layout().addWidget(self.ModeGP)
		
		self.InfoGP = QGroupBox("Infos")
		self.InfoGP.setLayout(QVBoxLayout())
		self.cmdGetInfos = QPushButton("Infos")
		
		def getInfosClickedHandler():
			# usbmux_address = None
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				my_dict = diagnostics_info(create_using_usbmux(usbmux_address=usbmux_address), True)
				self.textInfos.setPlainText(json.dumps(my_dict, indent=2))
				
		self.cmdGetInfos.clicked.connect(getInfosClickedHandler)
		self.hInfoButtonsLayout = QHBoxLayout()
		self.hInfoButtonsLayout.addWidget(self.cmdGetInfos)
		
		self.cmdGetBaterry = QPushButton("Battery")
		
		def getBatteryClickedHandler():
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				my_dict = diagnostics_battery_single(create_using_usbmux(usbmux_address=usbmux_address), True)
				self.textInfos.setPlainText(json.dumps(my_dict, indent=2, default=default_json_encoder))
				
		self.cmdGetBaterry.clicked.connect(getBatteryClickedHandler)
		
		self.hInfoButtonsLayout.addWidget(self.cmdGetBaterry)
		
		self.cmdGetMG = QPushButton("Mobile-Gestalt")
		
		def getMGClickedHandler():
			# usbmux_address = None
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				my_dict = diagnostics_mg(create_using_usbmux(usbmux_address=usbmux_address), None)
				# decoded_dict = {(key.decode() if isinstance(key, bytes) else key): ((value.decode() if isinstance(value, bytes) else value) if value != None else "") for key, value in my_dict.items()}
				self.textInfos.setPlainText(json.dumps(my_dict, skipkeys=True, indent=2, default=default_json_encoder))
				
		self.cmdGetMG.clicked.connect(getMGClickedHandler)
		self.hInfoButtonsLayout.addWidget(self.cmdGetMG)
		
		self.cmdGetIO = QPushButton("IO-Registry")
		
		def getIOClickedHandler():
			devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
			if len(devices) <= 1:
				my_dict = diagnostics_ioregistry(create_using_usbmux(usbmux_address=usbmux_address))
				# decoded_dict = {(key.decode() if isinstance(key, bytes) else key): ((value.decode() if isinstance(value, bytes) else value) if value != None else "") for key, value in my_dict.items()}
				self.textInfos.setPlainText(json.dumps(my_dict, skipkeys=True, indent=2, default=default_json_encoder))
				# self.textInfos.setPlainText(json.dumps(my_dict, indent=2))
				
		self.cmdGetIO.clicked.connect(getIOClickedHandler)
		self.hInfoButtonsLayout.addWidget(self.cmdGetIO)
		
		self.hInfoButtonsWidget = QWidget()
		self.hInfoButtonsWidget.setLayout(self.hInfoButtonsLayout)
		self.InfoGP.layout().addWidget(self.hInfoButtonsWidget)
		
		self.textInfos = QTextEdit()
		self.textInfos.setReadOnly(True)
		self.InfoGP.layout().addWidget(self.textInfos)
		
		self.layout().addWidget(self.InfoGP)