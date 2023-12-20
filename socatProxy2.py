#!/usr/bin/env python3

import socket
from threading import Thread

def handle_connection(usbmuxd_socket, usbmuxd_real_socket):
	while True:
		data = usbmuxd_socket.recv(1024)
		if not data:
			break
		else:
			print(f'{data}')
		
		usbmuxd_real_socket.sendall(data)
		
	usbmuxd_socket.close()
	usbmuxd_real_socket.close()
	
	
if __name__ == "__main__":
	usbmuxd_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	usbmuxd_socket.bind("/var/run/usbmuxd")
	usbmuxd_socket.listen(1)
	
	usbmuxd_real_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	usbmuxd_real_socket.connect("/var/run/usbmux_real")
	
	while True:
		usbmuxd_client_socket, _ = usbmuxd_socket.accept()
		
		thread = Thread(target=handle_connection, args=(usbmuxd_client_socket, usbmuxd_real_socket))
		thread.start()
		
		