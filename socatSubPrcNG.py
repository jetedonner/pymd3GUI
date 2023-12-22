#!/usr/bin/env python3

import subprocess
import threading
import time

# Define the socat command
mv_command = [
	"sudo", "mv",
	"/var/run/usbmux_real2", "/var/run/usbmux_real3" #, # "-x",
#	"UNIX-LISTEN:/var/run/usbmuxd,mode=777,reuseaddr,fork",
#	"UNIX-CONNECT:/var/run/usbmux_real"
]

# Define the socat command
socat_command = [
	"sudo", "socat",
	"-t100", "-v", # "-x",
	"UNIX-LISTEN:/var/run/usbmux_real,mode=777,reuseaddr,fork",
	"UNIX-CONNECT:/var/run/usbmux_real2"
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
#	process = subprocess.run(mv_command, shell=True, check=True, text=True, universal_newlines=True, stdout=subprocess.PIPE)
#	stdout = process.stdout
#	
#	if process.returncode == 0:
#		print(f"Command mv executed successfully: {mv_command}")
#		print(stdout)
#	else:
#		print(f"Command mv execution failed: {mv_command}")
#		print(stdout)
		
	# Start socat as a subprocess with stdout and stderr as pipes
	proc = subprocess.Popen(socat_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
	
	# Start a thread to read and print the subprocess output
	output_thread = threading.Thread(target=read_output, args=(proc,), daemon=True)
	output_thread.start()
	
	# Continue with the main script or wait for user input
	# For example, you can use input() to wait for the user to finish the script
#	input("Press Enter to exit...")
	while True:
		time.sleep(0.1)
	
except Exception as e:
	# Handle exceptions
	print(f"Error: {e}")
	
finally:
	# Terminate the subprocess when the script exits
	if proc.poll() is None:
		proc.terminate()