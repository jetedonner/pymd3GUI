#!/usr/bin/env python3

import socket

# Create a socket for listening on the forwarding socket
sock_listen = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock_listen.bind('/var/run/usbmuxd')
sock_listen.listen(1)

# Create a socket for connecting to the real socket
sock_connect = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock_connect.connect('/var/run/usbmux_real')

# Accept incoming connections on the forwarding socket
while True:
	conn, _ = sock_listen.accept()
	
	# Forward all data from the incoming connection to the real socket
	while True:
		data = conn.recv(1024)
		if not data:
			break
		print(f'{data}')
		sock_connect.sendall(data)
		
	# Close the connection and start a new one for the next client
	conn.close()