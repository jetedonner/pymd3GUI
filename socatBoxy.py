import socket
import select

# Create sockets
sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind sockets
sock1.bind('/var/run/usbmuxd')
sock2.bind('/var/run/usbmuxd_real')

# Listen for incoming connections
sock1.listen(1)
sock2.listen(1)

# Set up read and write lists to monitor both sockets
read_list = [sock1, sock2]
write_list = []

while True:
    # Check for incoming data
    ready_to_read, ready_to_write, error_list = select.select(read_list, write_list, [])

    # Handle incoming data from sock1
    for sock in ready_to_read:
        if sock == sock1:
            new_sock, _ = sock1.accept()
            print("Received connection from sock1")

            # Forward data to sock2
            while True:
                data = new_sock.recv(1024)
                if not data:
                    break

                print(f"Forwarding data from sock1 to sock2: {data}")

                if write_list:
                    for dest_sock in write_list:
                        dest_sock.sendall(data)

    # Handle incoming data from sock2
    for sock in ready_to_read:
        if sock == sock2:
            new_sock, _ = sock2.accept()
            print("Received connection from sock2")

            # Forward data to sock1
            while True:
                data = new_sock.recv(1024)
                if not data:
                    break

                print(f"Forwarding data from sock2 to sock1: {data}")

                if write_list:
                    for src_sock in write_list:
                        src_sock.sendall(data)

    # Add new sockets to write list if they're available
    for sock in ready_to_read:
        if sock not in write_list:
            write_list.append(sock)

    # Remove closed sockets from write list
    for sock in write_list:
        if not sock.poll(0):
            write_list.remove(sock)
