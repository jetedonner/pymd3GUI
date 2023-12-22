#!/usr/bin/env python3

import subprocess
import threading

# Define the socat command
socat_command = [
	"sudo", "socat",
	"-t100", "-v", # "-x",
	"UNIX-LISTEN:/var/run/usbmuxd,mode=777,reuseaddr,fork",
	"UNIX-CONNECT:/var/run/usbmux_real"
]

# Function to read and print subprocess output
def read_output(proc):
	while True:
		line = proc.stdout.readline()
		if not line:
			break
		# print(line.decode('utf-8').strip())
		print(f'{line}')
		
try:
	# Start socat as a subprocess with stdout and stderr as pipes
	proc = subprocess.Popen(socat_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
	
	# Start a thread to read and print the subprocess output
	output_thread = threading.Thread(target=read_output, args=(proc,), daemon=True)
	output_thread.start()
	
	# Continue with the main script or wait for user input
	# For example, you can use input() to wait for the user to finish the script
	input("Press Enter to exit...")
	
except Exception as e:
	# Handle exceptions
	print(f"Error: {e}")
	
finally:
	# Terminate the subprocess when the script exits
	if proc.poll() is None:
		proc.terminate()