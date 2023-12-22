import socket
import threading
import time
import logging
import xml.etree.ElementTree as ET
import re


def logData(data, request = True):
    try:
        last_character = data[-1]
        print(f'last_character: {last_character}')
        if data != b'':
            log.info(f"Data received (Request: {request}): {data}")
            extractXML(f'{data}', request)
            
    except Exception as e:
        log.error("Failed to log data!", e)
#       pass
    
def extractXML(text, request = True):
    
#   text = b'\x04\x02\x00\x00\x01\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n\t<key>ClientVersionString</key>\n\t<string>qt4i-usbmuxd</string>\n\t<key>DeviceID</key>\n\t<integer>3</integer>\n\t<key>MessageType</key>\n\t<string>Connect</string>\n\t<key>PortNumber</key>\n\t<integer>32498</integer>\n\t<key>ProgName</key>\n\t<string>pymobiledevice3</string>\n\t<key>kLibUSBMuxVersion</key>\n\t<integer>3</integer>\n</dict>\n</plist>\n'
    
    pattern = re.compile(r'<plist version="1.0">(.*?)</plist>', flags=re.DOTALL)
    match = pattern.search(text)
    
    if match:
        plist_data = match.group(1)
        new_text = str(plist_data).replace("\\n", "\n")
        new_text = str(new_text).replace("\\t", "    ")

        if request:
            print("\nREQUEST:")
        else:
            print("ANSWERE:")
            
        print(prettify_xml(f'{new_text}').expandtabs(4))
        
        if not request:
            print("\n\n")
        else:
            print("\n")
            
    else:
        print("No match found")

def prettify_xml(xml_string):
    tree = ET.fromstring(xml_string)
    xml_pretty = ET.tostring(tree, encoding='utf-8', method='html') #, pretty_print=True)
    
    def fix_indent(indented_xml):
        lines = ""
        if isinstance(indented_xml, str):
#           lines = indented_xml.split('\n')
            lines = indented_xml.split('\n')
        else:
            lines = indented_xml.decode("utf-8").split('\n')
#           lines = indented_xml.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.startswith('  '):
                fixed_lines.append('\t' + line[3:])
            else:
                fixed_lines.append(line)
                
        fixed_indented_xml = '\n'.join(fixed_lines)
        return fixed_indented_xml
    
    indent_xml = fix_indent(xml_pretty)
    return indent_xml

class USBMuxdProxy:
    def __init__(self):
        self.accepted = False
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind("/var/run/usbmuxd")
        self.server.listen(10)
        
        self.client = None
        self.client_thread = None
        
        self.real_usbmuxd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.real_usbmuxd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.real_usbmuxd.connect("/var/run/usbmux_real")
        
        self.read_thread = threading.Thread(target=self.read_real_usbmuxd_data)
#       self.read_thread.start()
        
    def accept(self):
#       if self.client == None:  
        client, address = self.server.accept()
        self.client = client
        self.client_thread = threading.Thread(target=self.handle_client)
        self.client_thread.start()
        
    def handle_client(self):
#       self.real_usbmuxd.accept()
        while True:
            try:
                data = self.client.recv(65536)
                
                if data != b'':
                    logData(data)
#                   log.info(f"Data (handle_client): {data}")
#   #               prettify_xml(f'{data}')
#                   extractXML(f'{data}')
#   #               extractXML(data)
                    
                if not data:
                    time.sleep(0.1)
                    continue
                
                self.real_usbmuxd.send(data)
            except Exception as e:
                log.error("Failed to read data from real USBMuxd daemon (handle_client):", e)
                continue
            
#       log.info("Client disconnected")
#       self.client.close()
#       self.client = None
#       self.client_thread = None
        
    def read_real_usbmuxd_data(self):
        while True:
            try:
                data = self.real_usbmuxd.recv(65536)
                
                if data != b'':
                    logData(data, False)
#                   log.info(f"Data (read_real_usbmuxd_data): {data}")
##                   prettify_xml(f'{data}')
#                   extractXML(f'{data}', False)
##                   extractXML(data)
                    
                if not data:
                    time.sleep(0.1)
                    continue
                
                self.client.send(data)
            except Exception as e:
                log.error("Failed to read data from real USBMuxd daemon (read_real_usbmuxd_data):", e)
                continue
    
#   def start(self):
#       if self.read_thread is not None:
#           raise RuntimeError("read_thread already running")
#           
#       self.read_thread = threading.Thread(target=self.read_real_usbmuxd_data)
#       self.read_thread.daemon = True
#       self.read_thread.start()
        
    def start(self):
        self.read_thread.start()
        
        while True:
            if not self.accepted:
                log.info("Waiting for client connection")
                self.accept()
#               self.accepted = True
#           time.sleep(0.01)
            
if __name__ == "__main__":
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    log.addHandler(handler)
    
    proxy = USBMuxdProxy()
    proxy.start()
    
    while True:
        time.sleep(1)
        
        
#import socket
#import time
#import threading
#import logging
#
#class USBMuxdProxy:
#   def __init__(self):
#       self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#       self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#       self.server.bind("/var/run/usbmuxd")
#       self.server.listen(1)
#
#       self.client = None
#       self.client_thread = None
#
#   def accept(self):
#       client, address = self.server.accept()
#       self.client = client
#       self.client_thread = threading.Thread(target=self.handle_client)
#       self.client_thread.start()
#
#   def handle_client(self):
#       while True:
#           data = self.client.recv(1024)
#           log.info(f"Data: {data}")
#           if not data:
#               time.sleep(0.01)
#               continue
#           
#           self.real_usbmuxd.sendall(data)
#
#       log.info("Client disconnected")
#       self.client.close()
#       self.client = None
#       self.client_thread = None
#
#   def start(self):
#       self.real_usbmuxd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#       self.real_usbmuxd.connect("/var/run/usbmux_real")
#
#       while True:
#           log.info("Waiting for client connection")
#           self.accept()
#           
#           time.sleep(0.01)
#
#if __name__ == "__main__":
#   log = logging.getLogger(__name__)
#   log.setLevel(logging.INFO)
#
#   handler = logging.StreamHandler()
#   handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#   log.addHandler(handler)
#
#   proxy = USBMuxdProxy()
#   proxy.start()
#
#   while True:
#       time.sleep(1)