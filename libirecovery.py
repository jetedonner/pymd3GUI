#!/usr/bin/env python3

# Define the header guard
LIBIRECOVERY_H = True

# Include necessary libraries
import ctypes

# Define the irecv_mode enum
class irecv_mode(ctypes.c_int):
	IRECV_K_RECOVERY_MODE_1 = 0x1280
	IRECV_K_RECOVERY_MODE_2 = 0x1281
	IRECV_K_RECOVERY_MODE_3 = 0x1282
	IRECV_K_RECOVERY_MODE_4 = 0x1283
	IRECV_K_WTF_MODE = 0x1222
	IRECV_K_DFU_MODE = 0x1227
	
# Define the irecv_error_t enum
class irecv_error_t(ctypes.c_int):
	IRECV_E_SUCCESS = 0
	IRECV_E_NO_DEVICE = -1
	IRECV_E_OUT_OF_MEMORY = -2
	IRECV_E_UNABLE_TO_CONNECT = -3
	IRECV_E_INVALID_INPUT = -4
	IRECV_E_FILE_NOT_FOUND = -5
	IRECV_E_USB_UPLOAD = -6
	IRECV_E_USB_STATUS = -7
	IRECV_E_USB_INTERFACE = -8
	IRECV_E_USB_CONFIGURATION = -9
	IRECV_E_PIPE = -10
	IRECV_E_TIMEOUT = -11
	IRECV_E_UNSUPPORTED = -254
	IRECV_E_UNKNOWN_ERROR = -255
	
class irecv_event_type:
	IRECV_RECEIVED = 1
	IRECV_PRECOMMAND = 2
	IRECV_POSTCOMMAND = 3
	IRECV_CONNECTED = 4
	IRECV_DISCONNECTED = 5
	IRECV_PROGRESS = 6
	
class irecv_event_t:
	def __init__(self):
		self.size = 0
		self.data = ""
		self.progress = 0.0
		self.type = irecv_event_type()
		
class irecv_device:
	def __init__(self):
		self.product_type = ""
		self.hardware_model = ""
		self.board_id = 0
		self.chip_id = 0
		self.display_name = ""
		
class irecv_device_t:
	def __init__(self):
		self.device = irecv_device()
		
class irecv_device_info:
	def __init__(self):
		self.cpid = 0
		self.cprv = 0
		self.cpfm = 0
		self.scep = 0
		self.bdid = 0
		self.ecid = 0
		self.ibfl = 0
		self.srnm = ""
		self.imei = ""
		self.srtg = ""
		self.serial_string = ""
		self.ap_nonce = bytes()
		self.ap_nonce_size = 0
		self.sep_nonce = bytes()
		self.sep_nonce_size = 0
		
class irecv_device_event_type:
	IRECV_DEVICE_ADD = 1
	IRECV_DEVICE_REMOVE = 2
	
class irecv_device_event_t:
	def __init__(self):
		self.type = irecv_device_event_type()
		self.mode = irecv_mode()
		self.device_info = irecv_device_info()
		
class irecv_client_private:
	pass
	
irecv_client_t = irecv_client_private

def irecv_set_debug_level(level: int) -> None:
	pass
	
def irecv_strerror(error: irecv_error_t) -> str:
	pass
	
def irecv_init() -> None:
	pass
	
def irecv_exit() -> None:
	pass
	
def irecv_open_with_ecid(client: irecv_client_t, ecid: int) -> irecv_error_t:
	pass
	
def irecv_open_with_ecid_and_attempts(pclient: irecv_client_t, ecid: int, attempts: int) -> irecv_error_t:
	pass
	
def irecv_reset(client: irecv_client_t) -> irecv_error_t:
	pass
	
def irecv_close(client: irecv_client_t) -> irecv_error_t:
	pass
	
def irecv_reconnect(client: irecv_client_t, initial_pause: int) -> irecv_client_t:
	pass
	
def irecv_receive(client: irecv_client_t) -> irecv_error_t:
	pass
	
def irecv_execute_script(client: irecv_client_t, script: str) -> irecv_error_t:
	pass
	
def irecv_reset_counters(client: irecv_client_t) -> irecv_error_t:
	pass
	
def irecv_finish_transfer(client: irecv_client_t) -> irecv_error_t:
	pass
	
def irecv_trigger_limera1n_exploit(client: irecv_client_t) -> irecv_error_t:
	pass
	
# usb helpers
def irecv_usb_set_configuration(client, configuration):
	pass
	
def irecv_usb_set_interface(client, usb_interface, usb_alt_interface):
	pass
	
def irecv_usb_control_transfer(client, bm_request_type, b_request, w_value, w_index, data, w_length, timeout):
	pass
	
def irecv_usb_bulk_transfer(client, endpoint, data, length, transferred, timeout):
	pass
	
# events
def irecv_device_event_cb(event, user_data):
	pass
	
def irecv_device_event_subscribe(context, callback, user_data):
	pass
	
def irecv_device_event_unsubscribe(context):
	pass
	
def irecv_event_cb(client, event):
	pass
	
def irecv_event_subscribe(client, type, callback, user_data):
	pass
	
def irecv_event_unsubscribe(client, type):
	pass
	
# I/O
def irecv_send_file(client, filename, dfu_notify_finished):
	pass
	
def irecv_send_command(client, command):
	pass
	
def irecv_send_command_breq(client, command, b_request):
	pass
	
def irecv_send_buffer(client, buffer, length, dfu_notify_finished):
	pass
	
def irecv_recv_buffer(client, buffer, length):
	pass
	
# commands
def irecv_saveenv(client):
	pass
	
def irecv_getenv(client, variable, value):
	pass
	
def irecv_setenv(client, variable, value):
	pass
	
def irecv_setenv_np(client, variable, value):
	pass
	
def irecv_reboot(client):
	pass
	
def irecv_getret(client, value):
	pass
	
# device information
def irecv_get_mode(client, mode):
	pass
	
def irecv_get_device_info(client):
	pass
	
"""
Device database queries
"""
	
def irecv_devices_get_all() -> irecv_device_t:
	"""
	Get all devices
	:return: irecv_device_t
	"""
	pass
	
def irecv_devices_get_device_by_client(client: irecv_client_t, device: irecv_device_t) -> irecv_error_t:
	"""
	Get device by client
	:param client: irecv_client_t
	:param device: irecv_device_t
	:return: irecv_error_t
	"""
	pass
	
def irecv_devices_get_device_by_product_type(product_type: str, device: irecv_device_t) -> irecv_error_t:
	"""
	Get device by product type
	:param product_type: str
	:param device: irecv_device_t
	:return: irecv_error_t
	"""
	pass
	
def irecv_devices_get_device_by_hardware_model(hardware_model: str, device: irecv_device_t) -> irecv_error_t:
	"""
	Get device by hardware model
	:param hardware_model: str
	:param device: irecv_device_t
	:return: irecv_error_t
	"""
	pass
	