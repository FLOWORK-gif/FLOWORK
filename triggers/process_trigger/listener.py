#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\triggers\process_trigger\listener.py
# JUMLAH BARIS : 71
#######################################################################

import time
import threading
import psutil
from flowork_kernel.api_contract import BaseTriggerListener
class ProcessListener(BaseTriggerListener):
    """
    Listener that monitors for a specific process starting or stopping.
    """
    def __init__(self, trigger_id: str, config: dict, services: dict, **kwargs):
        super().__init__(trigger_id, config, services, **kwargs)
        self.logger(f"ProcessListener instance created for rule_id: {self.rule_id}", "DEBUG") # English Log
        self.process_name = self.config.get("process_name")
        self.on_start = self.config.get("on_start", True)
        self.on_stop = self.config.get("on_stop", True)
        self.poll_interval = 5 # (COMMENT) Check every 5 seconds
        self.known_pids = set()
        self.thread = None
    def _find_pids_by_name(self):
        """Finds all PIDs for a given process name."""
        return {p.pid for p in psutil.process_iter(['name']) if p.info['name'].lower() == self.process_name.lower()}
    def start(self):
        """Starts the process monitoring thread."""
        if not self.process_name:
            self.logger(f"Process Trigger '{self.rule_id}': Process name is not configured. Trigger will not start.", "ERROR") # English Log
            return
        self.is_running = True
        self.known_pids = self._find_pids_by_name()
        self.logger(f"Process Trigger '{self.rule_id}': Initial scan found PIDs {self.known_pids} for '{self.process_name}'.", "INFO") # English Log
        self.thread = threading.Thread(target=self._monitor_process, daemon=True)
        self.thread.start()
        self.logger(f"Process Trigger '{self.rule_id}': Started monitoring for process '{self.process_name}'.", "SUCCESS") # English Log
    def _monitor_process(self):
        """The core monitoring loop that runs in a background thread."""
        while self.is_running:
            current_pids = self._find_pids_by_name()
            newly_started_pids = current_pids - self.known_pids
            if self.on_start and newly_started_pids:
                for pid in newly_started_pids:
                    self.logger(f"Process '{self.process_name}' (PID: {pid}) detected as STARTED.", "INFO") # English Log
                    event_data = {
                        "event_type": "process_started",
                        "process_name": self.process_name,
                        "pid": pid
                    }
                    self._on_event(event_data)
            stopped_pids = self.known_pids - current_pids
            if self.on_stop and stopped_pids:
                for pid in stopped_pids:
                    self.logger(f"Process '{self.process_name}' (PID: {pid}) detected as STOPPED.", "INFO") # English Log
                    event_data = {
                        "event_type": "process_stopped",
                        "process_name": self.process_name,
                        "pid": pid
                    }
                    self._on_event(event_data)
            self.known_pids = current_pids
            time.sleep(self.poll_interval)
    def stop(self):
        """Stops the monitoring thread."""
        if self.is_running:
            self.is_running = False
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2)
            self.logger(f"Process Trigger '{self.rule_id}': Monitoring stopped.", "INFO") # English Log
