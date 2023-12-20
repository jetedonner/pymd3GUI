#!/usr/bin/env python3

import socket
import threading

def handle_usbmuxd_client_connection(usbmuxd_client_socket):
#	usbmuxd_real_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#	usbmuxd_real_socket.connect("/var/run/usbmuxd_real")
	while True:
		data = usbmuxd_client_socket.recv(1024)
		
		# Check if there's any more data to receive
		if not data:
			break
		
		# Forward the data to usbmuxd_real socket
		usbmuxd_real_socket.sendall(data)
		
	usbmuxd_client_socket.close()
	
def handle_usbmuxd_real_connection(usbmuxd_real_socket):
	while True:
		data = usbmuxd_real_socket.recv(1024)
		
		# Check if there's any more data to receive
		if not data:
			break
		
		# Forward the data to usbmuxd client socket
		usbmuxd_client_socket.sendall(data)
		
	usbmuxd_real_socket.close()
	
	
# Establish connections to the target sockets
usbmuxd_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
usbmuxd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
usbmuxd_socket.bind("/var/run/usbmuxd")
usbmuxd_socket.listen(1)

usbmuxd_real_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
usbmuxd_real_socket.connect("/var/run/usbmuxd_real")


# Create threads for handling incoming connections
usbmuxd_client_socket, _ = usbmuxd_socket.accept()
thread = threading.Thread(target=handle_usbmuxd_client_connection, args=(usbmuxd_client_socket,))
thread.start()

usbmuxd_real_socket, _ = usbmuxd_socket.accept()
thread_real = threading.Thread(target=handle_usbmuxd_real_connection, args=(usbmuxd_real_socket,))
thread_real.start()


# Run the main loop
while True:
	pass