#!/usr/bin/env python3

from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux

APP_NAME = "pymd3GUI - GUI for pymobiledevice3"

def lockdownForFirstDevice(connectionType='USB', usbmuxAddress='/var/run/usbmuxd'): # _mysocket
	try:
		devices = select_devices_by_connection_type(connection_type=connectionType, usbmux_address=usbmuxAddress)
#			print(devices)
		if len(devices) >= 1:
			return True, create_using_usbmux(usbmux_address=usbmuxAddress)
	except Exception as e:
		print(f"Exception while getting lockdown to first device! Exception: {e}")
	return False, None
