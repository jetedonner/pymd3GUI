#!/usr/bin/env python3

import subprocess

def run_sudo_command(command):
	process = subprocess.run(command, shell=True, check=True, text=True, universal_newlines=True, stdout=subprocess.PIPE)
	stdout = process.stdout
	
	if process.returncode == 0:
		print(f"Command executed successfully: {command}")
		print(stdout)
	else:
		print(f"Command execution failed: {command}")
		print(stdout)
		
if __name__ == "__main__":
	# Replace "command_to_run" with the actual command you want to run with sudo
	sudo_command = "sudo python3 /Volumes/Data/dev/apple/iOS/tools/pymd3GUI/socatMy.py"
	
	run_sudo_command(sudo_command)