#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\system_diagnostics_plugin\diagnostics_page.py
# JUMLAH BARIS : 342
#######################################################################

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
from flowork_kernel.ui_shell.custom_widgets.scrolled_frame import ScrolledFrame
from .scanners.base_scanner import BaseScanner
class DiagnosticsPage(ttk.Frame):
    """
    The main UI frame for the System Diagnostics tab.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, padding=0) # MODIFIKASI: Padding dihapus
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.scanner_classes = []
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
        self.scanner_config = self._load_config()
        self._build_ui()
        self._discover_and_populate_scanners()
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
    def _load_config(self):
        self.config_path = os.path.join(os.path.dirname(__file__), 'diagnostics_config.json')
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_lines = [line for line in f if not line.strip().startswith('//')]
                config_string = "".join(config_lines)
                config_data = json.loads(config_string)
            self.kernel.write_to_log("Scanner configuration loaded successfully.", "SUCCESS")
            return config_data.get("scanners", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.kernel.write_to_log(f"Failed to load diagnostics_config.json: {e}. Using defaults.", "ERROR")
            return {}
    def _build_ui(self):
        """Builds the two-pane layout for the diagnostics page."""
        main_content_frame = ttk.Frame(self, padding=15)
        main_content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        paned_window = ttk.PanedWindow(main_content_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True)
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('diagnostics_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        guide_handle.lift()
        left_pane = ttk.Frame(paned_window, padding=10)
        paned_window.add(left_pane, weight=1)
        control_frame = ttk.LabelFrame(left_pane, text=self.loc.get('diagnostics_control_panel_title', fallback="Control Panel"))
        control_frame.pack(fill='both', expand=True)
        control_frame.rowconfigure(1, weight=1)
        control_frame.columnconfigure(0, weight=1)
        header_frame = ttk.Frame(control_frame)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(5,10), padx=5)
        self.select_all_var = BooleanVar(value=True)
        ttk.Checkbutton(header_frame, text=self.loc.get('diagnostics_select_all_toggle', fallback="Select / Deselect All"), variable=self.select_all_var, command=self._toggle_all_scanners).pack(side='left')
        scrolled_list = ScrolledFrame(control_frame)
        scrolled_list.grid(row=1, column=0, sticky='nsew', padx=5)
        self.scanner_list_frame = scrolled_list.scrollable_frame
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, sticky='ew', pady=(10,0), padx=5)
        button_frame.columnconfigure((0,1), weight=1)
        self.run_selected_button = ttk.Button(button_frame, text=self.loc.get('diagnostics_run_selected_button', fallback="Run Selected Scanners"), command=lambda: self._start_scan_thread(selected_only=True))
        self.run_selected_button.grid(row=0, column=0, sticky='ew', padx=(0,5))
        self.run_all_button = ttk.Button(button_frame, text=self.loc.get('diagnostics_run_all_button', fallback="Run All Scanners"), command=self._start_scan_thread, bootstyle="success")
        self.run_all_button.grid(row=0, column=1, sticky='ew', padx=(5,0))
        self.save_config_button = ttk.Button(button_frame, text=self.loc.get('diagnostics_save_config_button', fallback="Save Configuration"), command=self._save_scanner_config, bootstyle="primary")
        self.save_config_button.grid(row=1, column=0, sticky='ew', pady=(5,0), padx=(0,5))
        self.copy_results_button = ttk.Button(button_frame, text=self.loc.get("diagnostics_copy_results_button"), command=self._copy_report_to_clipboard, bootstyle="info")
        self.copy_results_button.grid(row=1, column=1, sticky='ew', pady=(5,0), padx=(5,0))
        right_pane = ttk.Frame(paned_window, padding=10)
        paned_window.add(right_pane, weight=3)
        right_pane.rowconfigure(2, weight=1)
        right_pane.columnconfigure(0, weight=1)
        report_frame = ttk.LabelFrame(right_pane, text=self.loc.get('diagnostics_report_panel_title', fallback="Report Panel"))
        report_frame.pack(fill='both', expand=True)
        report_frame.rowconfigure(2, weight=1)
        report_frame.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(report_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        filter_controls_frame = ttk.Frame(report_frame)
        filter_controls_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=(0, 10))
        ttk.Label(filter_controls_frame, text=self.loc.get('diagnostics_filter_level_label', fallback="Show Levels:")).pack(side='left', anchor='w', padx=(0, 10))
        filter_options = [("CRITICAL", "danger"), ("MAJOR", "danger"), ("MINOR", "warning"), ("INFO", "info"), ("SCAN", "primary"), ("OK", "success")]
        for text, style in filter_options:
            cb = ttk.Checkbutton(filter_controls_frame, text=text, variable=self.filter_vars.get(text), bootstyle=f"{style}-round-toggle", command=self._apply_filters_to_report)
            cb.pack(side='left', padx=3)
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap='word', state='disabled', font=("Consolas", 9))
        self.report_text.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0,10))
        self._configure_text_tags()
    def _save_scanner_config(self):
        self.kernel.write_to_log("Saving scanner configuration...", "INFO")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            full_config = {"scanners": {}}
        current_scanners_config = full_config.get("scanners", {})
        for class_name, var in self.scanner_vars.items():
            scanner_id = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name.replace("Core", "").replace("Scan", "")).lower()
            if scanner_id in current_scanners_config:
                current_scanners_config[scanner_id]['enabled'] = var.get()
            else:
                current_scanners_config[scanner_id] = {"enabled": var.get(), "severity": "MINOR", "config": {}}
        full_config["scanners"] = current_scanners_config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=4)
            self.kernel.write_to_log("Scanner configuration saved successfully.", "SUCCESS")
            messagebox.showinfo("Success", "Scanner configuration saved successfully.")
        except Exception as e:
            self.kernel.write_to_log(f"Failed to save scanner configuration: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    def _discover_and_populate_scanners(self):
        for child in self.scanner_list_frame.winfo_children():
            child.destroy()
        self.scanner_classes.clear()
        self.scanner_vars.clear()
        self.animation_labels.clear()
        plugin_path = os.path.dirname(__file__)
        scanners_dir = os.path.join(plugin_path, 'scanners')
        discovered_classes = []
        if os.path.isdir(scanners_dir):
            for root, _, files in os.walk(scanners_dir):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__') and file not in ['base_scanner.py', 'dashboard_view.py']:
                        rel_path = os.path.relpath(os.path.join(root, file), self.kernel.plugins_path)
                        module_path = os.path.splitext(rel_path)[0].replace(os.sep, '.')
                        module_name = f"plugins.{module_path}"
                        try:
                            module = importlib.import_module(module_name)
                            for name, obj in inspect.getmembers(module, inspect.isclass):
                                if issubclass(obj, BaseScanner) and obj is not BaseScanner:
                                    discovered_classes.append(obj)
                        except Exception as e:
                            self.kernel.write_to_log(f"DiagnosticsUI: Failed to import scanner from '{file}': {e}", "ERROR")
        discovered_classes.sort(key=lambda x: x.__name__)
        list_counter = 1
        for scanner_class in discovered_classes:
            class_name = scanner_class.__name__
            scanner_id = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name.replace("Core", "").replace("Scan", "")).lower()
            is_enabled_from_config = self.scanner_config.get(scanner_id, {}).get("enabled", True)
            self.scanner_classes.append(scanner_class)
            display_name = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', class_name.replace("Core", "")).replace("Scan", " Scan")
            item_frame = ttk.Frame(self.scanner_list_frame)
            item_frame.pack(fill='x', padx=10, pady=2)
            number_label = ttk.Label(item_frame, text=f"{list_counter}.", width=4, anchor='w')
            number_label.pack(side='left')
            var = BooleanVar(value=is_enabled_from_config)
            self.scanner_vars[class_name] = var
            checkbutton = ttk.Checkbutton(item_frame, text=display_name, variable=var)
            checkbutton.pack(side='left')
            animation_label = ttk.Label(item_frame, text="", width=3, bootstyle="info")
            animation_label.pack(side='left', padx=(5, 0))
            self.animation_labels[class_name] = animation_label
            list_counter += 1
    def _toggle_all_scanners(self):
        is_checked = self.select_all_var.get()
        for var in self.scanner_vars.values():
            var.set(is_checked)
    def _configure_text_tags(self):
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        colors = theme_manager.get_colors()
        self.report_text.config(background=colors.get('dark', '#333'), foreground=colors.get('fg', 'white'))
        style = ttk.Style.get_instance()
        critical_bg = style.colors.get('danger')
        tags_to_configure = {
            "CRITICAL": {'foreground': colors.get('light'), 'background': critical_bg, 'font': ('Consolas', 9, 'bold')},
            "MAJOR": {'foreground': colors.get('danger')}, "MINOR": {'foreground': colors.get('warning')},
            "INFO": {'foreground': colors.get('fg')}, "SUCCESS": {'foreground': colors.get('success')},
            "OK": {'foreground': colors.get('success')}, "SCAN": {'foreground': colors.get('info')},
            "DEBUG": {'foreground': colors.get('secondary')}
        }
        for tag, config in tags_to_configure.items():
            self.report_text.tag_config(tag, **config)
    def _add_report_line(self, message, level="INFO", context=None):
        if not self.winfo_exists(): return
        self._all_report_entries.append({'message': message, 'level': level.upper(), 'context': context or {}})
        self._apply_filters_to_report()
    def _apply_filters_to_report(self):
        if not self.winfo_exists(): return
        levels_to_show = {level for level, var in self.filter_vars.items() if var.get()}
        self.report_text.config(state='normal')
        self.report_text.delete('1.0', 'end')
        for entry in self._all_report_entries:
            if entry['level'] in levels_to_show:
                self.report_text.insert('end', f"{entry['message']}\n", (entry['level'],))
        self.report_text.see('end')
        self.report_text.config(state='disabled')
        self.update_idletasks()
    def _copy_report_to_clipboard(self):
        try:
            content = self.report_text.get("1.0", "end-1c")
            if content.strip():
                self.clipboard_clear()
                self.clipboard_append(content)
                self.kernel.write_to_log(self.loc.get("diagnostics_log_copied_success"), "SUCCESS")
        except Exception as e:
            self.kernel.write_to_log(f"Failed to copy diagnostics report: {e}", "ERROR")
    def _clear_animations(self):
        for label in self.animation_labels.values():
            label.config(text="")
    def _start_animation(self, class_name):
        if class_name in self.animation_jobs:
            self.after_cancel(self.animation_jobs[class_name])
        self._update_animation_frame(class_name, 0)
    def _update_animation_frame(self, class_name, frame_index):
        if class_name in self.animation_labels:
            label = self.animation_labels[class_name]
            if label.winfo_exists():
                label.config(text=f" {self.animation_frames[frame_index]}", bootstyle="info")
                next_frame_index = (frame_index + 1) % len(self.animation_frames)
                job_id = self.after(150, self._update_animation_frame, class_name, next_frame_index)
                self.animation_jobs[class_name] = job_id
    def _stop_animation(self, class_name):
        if class_name in self.animation_jobs:
            self.after_cancel(self.animation_jobs[class_name])
            del self.animation_jobs[class_name]
        if class_name in self.animation_labels:
            label = self.animation_labels[class_name]
            if label.winfo_exists():
                label.config(text="✓", bootstyle="success")
    def _start_scan_thread(self, selected_only=False):
        self.run_selected_button.config(state="disabled")
        self.run_all_button.config(state="disabled")
        self.save_config_button.config(state="disabled")
        self.progress['value'] = 0
        self._all_report_entries.clear()
        self._apply_filters_to_report()
        self._clear_animations()
        scanners_to_run = []
        if selected_only:
            for scanner_class in self.scanner_classes:
                if self.scanner_vars[scanner_class.__name__].get():
                    scanners_to_run.append(scanner_class)
        else:
            for scanner_class in self.scanner_classes:
                scanner_id = re.sub(r'(?<!^)(?=[A-Z])', '_', scanner_class.__name__.replace("Core", "").replace("Scan", "")).lower()
                if self.scanner_config.get(scanner_id, {}).get("enabled", True):
                     scanners_to_run.append(scanner_class)
        if not scanners_to_run:
            self.run_selected_button.config(state="normal")
            self.run_all_button.config(state="normal")
            self.save_config_button.config(state="normal")
            return
        def scan_target():
            total_scanners = len(scanners_to_run)
            self.progress['maximum'] = total_scanners
            total_counts = {'CRITICAL': 0, 'MAJOR': 0, 'MINOR': 0, 'INFO': 0}
            for i, scanner_class in enumerate(scanners_to_run):
                if not self.winfo_exists(): break
                class_name = scanner_class.__name__
                self.after(0, self._start_animation, class_name)
                scanner_id = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name.replace("Core", "").replace("Scan", "")).lower()
                scanner_specific_config = self.scanner_config.get(scanner_id, {})
                instance = scanner_class(self.kernel, lambda msg, lvl, context=None: self.after(0, self._add_report_line, msg, lvl, context), config=scanner_specific_config)
                instance.run_scan()
                self.after(0, self._stop_animation, class_name)
                total_counts['CRITICAL'] += getattr(instance, 'critical_count', 0)
                total_counts['MAJOR'] += getattr(instance, 'major_count', 0)
                total_counts['MINOR'] += getattr(instance, 'minor_count', 0)
                total_counts['INFO'] += getattr(instance, 'info_count', 0)
                self.after(0, lambda i=i: self.progress.config(value=i + 1))
                time.sleep(0.05)
            summary_parts = [f"{count} {level}" for level, count in total_counts.items() if count > 0]
            final_summary = f"Scan Complete. Total findings: {', '.join(summary_parts) if summary_parts else '0'}."
            self.after(0, self._add_report_line, f"\n{'='*60}\n{final_summary}\n{'='*60}", "SUCCESS")
            if self.winfo_exists():
                self.after(0, lambda: self.run_selected_button.config(state="normal"))
                self.after(0, lambda: self.run_all_button.config(state="normal"))
                self.after(0, lambda: self.save_config_button.config(state="normal"))
        threading.Thread(target=scan_target, daemon=True).start()
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None
