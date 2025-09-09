import ttkbootstrap as ttk
from tkinter import scrolledtext, BooleanVar, messagebox
import os
import re
import importlib
import inspect
import threading
import time
import json
import sys
# from flowork_kernel.ui_shell.custom_widgets.scrolled_frame import ScrolledFrame
# COMMENT: Patched import path to adhere to GUI/Kernel separation rule.
# Scanners are part of the UI/Client layer and must not import from the kernel directly.
from views.custom_widgets.scrolled_frame import ScrolledFrame
from api_client.client import ApiClient
class DiagnosticsPage(ttk.Frame):
    """
    The main UI frame for the System Diagnostics tab.
    This is the GUI-side representation.
    """
    def __init__(self, parent_notebook, api_client, loc_service, tab_id=None, is_new_tab=False):
        super().__init__(parent_notebook, padding=0)
        self.api_client = api_client
        self.loc = loc_service
        self.scanner_vars = {}
        self.animation_labels = {}
        self.animation_jobs = {}
        self.animation_frames = ['|', '/', '-', '\\']
        self._all_report_entries = []
        self.filter_vars = {
            'CRITICAL': BooleanVar(value=True),
            'MAJOR': BooleanVar(value=True),
            'MINOR': BooleanVar(value=True),
            'INFO': BooleanVar(value=True),
            'SCAN': BooleanVar(value=True),
            'OK': BooleanVar(value=True)
        }
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self._build_ui()
        self._populate_guide()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _populate_guide(self):
        guide_content = self.loc.get("diagnostics_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _build_ui(self):
        main_content_frame = ttk.Frame(self, padding=15)
        main_content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        ttk.Label(main_content_frame, text="Diagnostics Page", font=("Helvetica", 16, "bold")).pack(pady=10) # English Hardcode
        ttk.Label(main_content_frame, text="This feature is being re-integrated.", wraplength=400).pack(pady=10) # English Hardcode
        self.run_all_button = ttk.Button(main_content_frame, text=self.loc.get('diagnostics_run_all_button', fallback="Run All Scanners"), command=self._start_scan_thread, bootstyle="success")
        self.run_all_button.pack(pady=20, ipady=10)
        self.report_text = scrolledtext.ScrolledText(main_content_frame, wrap='word', state='disabled', font=("Consolas", 9))
        self.report_text.pack(fill='both', expand=True, padx=10, pady=(0,10))
    def _start_scan_thread(self):
        self.run_all_button.config(state="disabled")
        self.report_text.config(state='normal')
        self.report_text.delete('1.0', 'end')
        self.report_text.insert('1.0', "Sending scan request to the server...\n") # English Hardcode
        self.report_text.config(state='disabled')
        threading.Thread(target=self._scan_worker, daemon=True).start()
    def _scan_worker(self):
        success, response = self.api_client.trigger_scan_by_api()
        if success:
            job_id = response.get('job_id')
            self.after(0, self._add_report_line, f"Scan job started with ID: {job_id}\nChecking status periodically...\n", "INFO") # English Hardcode
            self.after(2000, self._check_scan_status, job_id)
        else:
            self.after(0, self._add_report_line, f"Failed to start scan: {response}", "ERROR") # English Hardcode
            self.after(0, lambda: self.run_all_button.config(state="normal"))
    def _check_scan_status(self, job_id):
        success, response = self.api_client.get_job_status(job_id)
        if success:
            status = response.get('status')
            if status in ["QUEUED", "RUNNING"]:
                self.after(5000, self._check_scan_status, job_id) # Check again in 5 seconds
            elif status == "COMPLETED":
                result = response.get('result', {})
                summary = result.get('summary', 'No summary.')
                full_log = result.get('full_log', 'No full log.')
                report = f"--- SCAN COMPLETE ---\n\nSUMMARY:\n{summary}\n\nFULL LOG:\n{full_log}" # English Hardcode
                self.after(0, self._add_report_line, report, "SUCCESS")
                self.after(0, lambda: self.run_all_button.config(state="normal"))
            elif status == "FAILED":
                error = response.get('error', 'Unknown error.')
                self.after(0, self._add_report_line, f"SCAN FAILED: {error}", "ERROR") # English Hardcode
                self.after(0, lambda: self.run_all_button.config(state="normal"))
        else:
            self.after(0, self._add_report_line, f"Failed to get scan status: {response}", "ERROR") # English Hardcode
            self.after(0, lambda: self.run_all_button.config(state="normal"))
    def _add_report_line(self, message, level="INFO"):
        if not self.winfo_exists(): return
        self.report_text.config(state='normal')
        self.report_text.insert('end', f"[{level}] {message}\n")
        self.report_text.see('end')
        self.report_text.config(state='disabled')
    def _populate_guide(self):
        pass