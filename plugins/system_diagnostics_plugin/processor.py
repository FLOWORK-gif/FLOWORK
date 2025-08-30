#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\system_diagnostics_plugin\processor.py
# JUMLAH BARIS : 142
#######################################################################

import ttkbootstrap as ttk
from tkinter import Text, scrolledtext, messagebox
import threading
import time
import queue
import os
import re
import json
import importlib
import inspect
from flowork_kernel.api_contract import BaseUIProvider, BaseModule
from .scanners.base_scanner import BaseScanner
from .diagnostics_page import DiagnosticsPage
class SystemDiagnosticsUIProvider(BaseUIProvider, BaseModule):
    TIER = "free"  # ADDED BY SCANNER: Default tier
    """
    Mendaftarkan halaman Diagnostik ke UI utama Flowork.
    Menjadi koordinator untuk semua jenis scan.
    """
    _BENTENG_BAJA_ID = "0xDIAGNOSTICS_CORE_COMPONENT"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        return payload
    def get_ui_tabs(self):
        """
        Provides the Diagnostics Page as a new main tab to the Kernel.
        """
        self.logger("SystemDiagnosticsPlugin: Providing 'DiagnosticsPage' to the main UI.", "DEBUG")
        return [
            {
                'key': 'system_diagnostics',
                'title': self.loc.get('diagnostics_tab_title', fallback="Diagnostik Sistem"),
                'frame_class': DiagnosticsPage
            }
        ]
    def get_menu_items(self):
        """
        Adds a menu item to open the diagnostics tab.
        """
        return [
            {
                "parent": self.loc.get('menu_help', fallback="Bantuan"),
                "add_separator": True,
                "label": self.loc.get('diagnostics_tab_title', fallback="Diagnostik Sistem"),
                "command": lambda: self.kernel.get_service("tab_manager_service").open_managed_tab('system_diagnostics')
            }
        ]
    def scan_single_component_and_get_status(self, component_path: str) -> (bool, str):
        """
        Runs all relevant scans on a single component directory and returns a simple pass/fail status.
        """
        self.logger(f"DIAGNOSTICS: Performing targeted scan on path: {component_path}", "INFO")
        all_scanners = self._discover_scanners()
        scanners_to_run = all_scanners
        all_findings = []
        def report_handler(message, level, context=None):
            if level in ["CRITICAL", "MAJOR", "MINOR"]:
                all_findings.append({"level": level, "message": message})
        for scanner_class in scanners_to_run:
            try:
                scanner_instance = scanner_class(self.kernel, report_handler)
                if hasattr(scanner_instance, 'set_target_path'):
                    scanner_instance.set_target_path(component_path)
                scanner_instance.run_scan()
            except Exception as e:
                all_findings.append({"level": "CRITICAL", "message": f"Scanner {scanner_class.__name__} failed: {e}"})
        critical_or_major_issues = [f for f in all_findings if f['level'] in ['CRITICAL', 'MAJOR']]
        if not critical_or_major_issues:
            return True, "All critical and major checks passed."
        else:
            report = "\n".join([f"- {f['level']}: {f['message']}" for f in critical_or_major_issues])
            return False, f"Scan failed with the following issues:\n{report}"
    def _discover_scanners(self):
        """Helper to discover all available scanner classes."""
        all_scanners = []
        plugin_path = os.path.dirname(__file__)
        scanners_dir = os.path.join(plugin_path, 'scanners')
        if os.path.isdir(scanners_dir):
            for entry in os.scandir(scanners_dir):
                if entry.name.endswith('.py') and not entry.name.startswith('__'):
                    module_name = f"plugins.system_diagnostics_plugin.scanners.{entry.name[:-3]}"
                    try:
                        module = importlib.import_module(module_name)
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, BaseScanner) and obj is not BaseScanner:
                                all_scanners.append(obj)
                    except Exception:
                        pass
        return all_scanners
    def start_scan_headless(self, scan_id: str, target_scanner_id: str = None) -> dict:
        """
        Runs all or a specific scanner module synchronously and returns a dictionary with the results.
        This is designed to be called by an API endpoint.
        """
        log_target = 'ALL' if not target_scanner_id else target_scanner_id.upper()
        self.logger(f"API-DIAG: Starting Headless Scan for ID: {scan_id} (Target: {log_target})", "INFO")
        report_lines = []
        def headless_report_handler(message, level, context=None): # Added context to match signature
            report_lines.append(f"[{level}] {message}")
        summaries = []
        all_scanners = self._discover_scanners()
        if not all_scanners:
            headless_report_handler("Tidak ada modul scanner yang ditemukan.", "ERROR")
        scanners_to_run = []
        if target_scanner_id:
            found = False
            for scanner_class in all_scanners:
                class_id = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', scanner_class.__name__.replace("Core", "")).lower()
                class_id = class_id.replace("_scan", "")
                if class_id == target_scanner_id:
                    scanners_to_run.append(scanner_class)
                    found = True
                    break
            if not found:
                headless_report_handler(f"Scanner dengan ID '{target_scanner_id}' tidak ditemukan.", "ERROR")
        else:
            scanners_to_run = all_scanners
        for scanner_class in scanners_to_run:
            try:
                scanner_instance = scanner_class(self.kernel, headless_report_handler)
                summary = scanner_instance.run_scan()
                summaries.append(summary)
            except Exception as e:
                summary = f"FATAL ERROR while running {scanner_class.__name__}: {e}"
                summaries.append(summary)
                headless_report_handler(summary, "ERROR")
        full_report_str = "\n".join(report_lines)
        final_summary = "\n".join(summaries)
        result_data = {
            "scan_id": scan_id, "status": "completed", "timestamp": time.time(),
            "summary": final_summary, "full_log": full_report_str
        }
        self.logger(f"API-DIAG: Scan {scan_id} selesai. Mengembalikan hasil.", "SUCCESS")
        return result_data
