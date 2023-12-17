#!/usr/bin/env python3
from pymobiledevice3.usbmux import select_devices_by_connection_type
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux
from pymobiledevice3.services.syslog import SyslogService
from pymobiledevice3.services.os_trace import OsTraceService, SyslogLogLevel
#'from pymobiledevice3.services.os_trace import OsTraceService'

from PyQt6.QtCore import *
from PyQt6.QtGui import QIntValidator, QColor
from PyQt6.QtWidgets import *

usbmux_address = None

autoScrollSysLog = True

def processes_ps(service_provider: LockdownClient):
	""" show process list """
	return OsTraceService(lockdown=service_provider).get_pid_list().get('Payload')
	
class SysLogReceiver(QObject):
#	data_received = pyqtSignal(str)
	interruptSysLog = pyqtSignal()
	
class SysLogWorkerSignals(QObject):
	finished = pyqtSignal()
#	result = pyqtSignal(str)
	sendSysLog = pyqtSignal(str, str)
	
class SysLogWorker(QRunnable):
	def __init__(self, data_receiver):
		super(SysLogWorker, self).__init__()
		self.isSysLogActive = False
		self.data_receiver = data_receiver
		self.signals = SysLogWorkerSignals()
		
	def run(self):
		self.data_receiver.interruptSysLog.connect(self.handle_interruptSysLog)
		QCoreApplication.processEvents()		
		self.runSysLog()
		
	def runSysLog(self):
		self.isSysLogActive = True
		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
		if len(devices) <= 1:
			for syslog_entry in OsTraceService(lockdown=create_using_usbmux(usbmux_address=usbmux_address)).syslog(pid=-1):
#				print(syslog_entry.timestamp)
				self.signals.sendSysLog.emit(str(syslog_entry.timestamp), "green")
				self.signals.sendSysLog.emit(str(syslog_entry.message), "white")
				self.signals.sendSysLog.emit(str("\n"), "white")
				QCoreApplication.processEvents()
				if self.isSysLogActive is False:
					break
				
		self.signals.finished.emit()
		
	def handle_interruptSysLog(self):
#		print(f"Received interrupt in the sysLog worker thread")
		self.isSysLogActive = False
		
class LogginOutput(QTextEdit):
	
	def __init__(self, parent=None):
		super(LogginOutput, self).__init__(parent)
		self.setReadOnly(True)
		# self.setLineWrapMode(self.NoWrap)
		self.insertPlainText("")
		self.doAutoScroll = True
		self.sb = self.verticalScrollBar()
		
	@pyqtSlot(bool)
	def updateAutoScroll(self, doAutoScroll):
		self.doAutoScroll = doAutoScroll
		
	@pyqtSlot(str, str)
	def append(self, text, color):
		self.setTextColor(QColor(color))
		self.insertPlainText(text)
		if self.doAutoScroll:
			self.sb.setValue(self.sb.maximum())
			
class TabSysLog(QWidget):
	
	def sysLogActive_changed(self, state):
		interruptSysLogRunnable = (state == 2)
		if not interruptSysLogRunnable:
			QCoreApplication.processEvents()    
			self.window().sysLog_receiver.interruptSysLog.emit()
			QCoreApplication.processEvents()
		else:
			self.changeLabel(self.textLog)
			
	def sysLogAutoScroll_changed(self, state):
		autoScrollSysLog = (state == 2)
		
		QMetaObject.invokeMethod(self.textLog,
				"updateAutoScroll", Qt.ConnectionType.QueuedConnection, 
				Q_ARG(bool, autoScrollSysLog))
		
	def changeLabel(self, box):
		interruptSysLogRunnable = False
		self.window().start_worker()
		
	def __init__(self, parent=None):
		super().__init__(parent)
		
		validator = QIntValidator(-1, 1000000)
		
		self.gbFilter = QGroupBox("Filter")
		self.gbFilter.setLayout(QVBoxLayout())
		
		self.lblPidFiler = QLabel("PID Filter (-1 = No Filter):")
		self.txtPidFilter = QLineEdit("-1")
		self.txtPidFilter.setValidator(validator)
		
		self.cmbPid = QComboBox()
		self.cmbPid.setEditable(True)
		
		self.my_processes = {str("-1"): "(No Filter)"}
		self.cmbPid.addItem("-1 (NO Filter)")
#		self.my_processes.update({str("-1"): "(No Filter)"})
		
		devices = select_devices_by_connection_type(connection_type='USB', usbmux_address=usbmux_address)
		if len(devices) <= 1:
#			print(OsTraceService(lockdown=create_using_usbmux(usbmux_address=usbmux_address)).get_pid_list())
			processes_list = OsTraceService(lockdown=create_using_usbmux(usbmux_address=usbmux_address)).get_pid_list().get('Payload')
			for pid, process_info in processes_list.items():
				process_name = process_info.get('ProcessName')
				print(f'{pid} ({process_name})')
				self.cmbPid.addItem(f'{pid} ({process_name})')
				self.my_processes.update({str(pid): process_name})
#			for processes_id in OsTraceService(lockdown=create_using_usbmux(usbmux_address=usbmux_address)).get_pid_list().get('Payload'):
#				print(processes_id.values())
#				print(processes_id)
##				self.cmbPid.addItem(f'{processes_lid} ({processes_name})')
##				self.cmbPid.addItem("100 (usermanagerd)")
		
		self.textLog = LogginOutput(parent)
		self.setLayout(QVBoxLayout())
		self.gbFilter.layout().addWidget(self.lblPidFiler)
#		self.gbFilter.layout().addWidget(self.txtPidFilter)
		self.gbFilter.layout().addWidget(self.cmbPid)
		self.layout().addWidget(self.gbFilter)
		
		self.gbLog = QGroupBox("SysLog")
		self.gbLog.setLayout(QVBoxLayout())
		
#		self.layout().addWidget(self.textLog)
		self.gbLog.layout().addWidget(self.textLog)
		
		
		self.layCtrl = QHBoxLayout()
		self.widCtrl = QWidget()
		self.widCtrl.setLayout(self.layCtrl)
		
		self.sysLogActive = QCheckBox("SysLog active")
		self.sysLogActive.stateChanged.connect(self.sysLogActive_changed)
		self.layCtrl.addWidget(self.sysLogActive)
		
		self.autoScroll = QCheckBox("Autoscroll")
		self.autoScroll.setChecked(True)
		self.autoScroll.stateChanged.connect(self.sysLogAutoScroll_changed)
		self.layCtrl.addWidget(self.autoScroll)
#		self.layout().addWidget(self.widCtrl)
		self.gbLog.layout().addWidget(self.widCtrl)
		self.layout().addWidget(self.gbLog)
		self.widCtrl.adjustSize()