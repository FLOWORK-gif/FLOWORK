#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\widgets\log_viewer_widget\log_viewer_widget.py
# JUMLAH BARIS : 105
#######################################################################

import ttkbootstrap as ttk
from tkinter import Text, ttk as tk_ttk
import datetime
from flowork_kernel.api_contract import BaseDashboardWidget
class LogViewerWidget(BaseDashboardWidget):
    TIER = "free"  # ADDED BY SCANNER: Default tier
    """Widget mandiri untuk menampilkan, memfilter, dan mengelola log eksekusi."""
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self._all_log_entries = []
        self._create_widgets()
        self.on_widget_load()
    def on_widget_load(self):
        """Dipanggil oleh DashboardManager saat widget berhasil dibuat dan ditampilkan."""
        super().on_widget_load()
        if hasattr(self.kernel, 'register_log_viewer'):
            self.kernel.register_log_viewer(self.coordinator_tab.tab_id, self)
    def on_widget_destroy(self):
        """Dipanggil oleh DashboardManager saat widget akan dihancurkan."""
        super().on_widget_destroy()
        if hasattr(self.kernel, 'unregister_log_viewer'):
            self.kernel.unregister_log_viewer(self.coordinator_tab.tab_id)
    def _create_widgets(self):
        ttk.Label(self, text=self.loc.get('execution_log_title'), style='TLabel').pack(pady=5, anchor='w', padx=5)
        log_filter_frame = ttk.Frame(self, style='TFrame')
        log_filter_frame.pack(fill='x', pady=(0, 5), padx=5)
        self.search_entry = ttk.Entry(log_filter_frame, style='Prop.TEntry')
        self.search_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.search_entry.insert(0, self.loc.get('search_log_placeholder'))
        self.search_entry.bind("<KeyRelease>", self._filter_logs)
        self.filter_combobox = ttk.Combobox(log_filter_frame, values=[self.loc.get(k) for k in ['log_level_all', 'log_level_info', 'log_level_warn', 'log_level_error', 'log_level_success', 'log_level_debug', 'log_level_cmd', 'log_level_detail']], state="readonly")
        self.filter_combobox.set(self.loc.get('log_level_all'))
        self.filter_combobox.pack(side='left')
        self.filter_combobox.bind("<<ComboboxSelected>>", self._filter_logs)
        log_button_frame = ttk.Frame(self, style='TFrame')
        log_button_frame.pack(fill='x', side='bottom', pady=(5,5), padx=5)
        ttk.Button(log_button_frame, text=self.loc.get('copy_log_button'), command=self.copy_log_to_clipboard, style="info.TButton").pack(side='left', expand=True, fill='x', padx=(0, 2))
        ttk.Button(log_button_frame, text=self.loc.get('clear_log_button'), command=self.clear_log, style="success.TButton").pack(side='left', expand=True, fill='x')
        log_text_container = ttk.Frame(self, style='TFrame')
        log_text_container.pack(expand=True, fill='both', side='top', padx=5)
        self.log_text = Text(log_text_container, wrap='word', height=10, state='disabled')
        log_text_scroll = ttk.Scrollbar(log_text_container, command=self.log_text.yview)
        log_text_scroll.pack(side='right', fill='y')
        self.log_text.pack(side='left', expand=True, fill='both')
        self.log_text.config(yscrollcommand=log_text_scroll.set)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {}
        self.log_text.tag_config("INFO", foreground=colors.get('fg', 'white'))
        self.log_text.tag_config("SUCCESS", foreground=colors.get('success', '#76ff7b'))
        self.log_text.tag_config("WARN", foreground=colors.get('warning', '#ffb627'))
        self.log_text.tag_config("ERROR", foreground=colors.get('danger', '#ff686b'))
        self.log_text.tag_config("DEBUG", foreground=colors.get('info', '#8be9fd'))
        self.log_text.tag_config("CMD", foreground=colors.get('primary', '#007bff'))
        self.log_text.tag_config("DETAIL", foreground=colors.get('secondary', 'grey'))
    def copy_log_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get('1.0', 'end'))
        self.kernel.write_to_log(self.loc.get('log_copied_to_clipboard'), "SUCCESS")
    def clear_log(self, feedback=True):
        self._all_log_entries = []
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')
        if feedback:
            self.kernel.write_to_log(self.loc.get('log_cleared'), "WARN")
    def write_to_log(self, message, level="INFO"):
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            tag = level.upper()
            entry = {"timestamp": timestamp, "message": message, "level": tag}
            self._all_log_entries.append(entry)
            self._filter_logs()
        except Exception as e:
            print(f"CRITICAL LOGGING ERROR: {e} - Message: {message}")
    def _filter_logs(self, event=None):
        search_term = self.search_entry.get().strip().lower()
        if search_term == self.loc.get('search_log_placeholder').lower():
            search_term = ""
        level_map = {
            self.loc.get('log_level_all').upper(): 'ALL',
            self.loc.get('log_level_info').upper(): 'INFO',
            self.loc.get('log_level_warn').upper(): 'WARN',
            self.loc.get('log_level_error').upper(): 'ERROR',
            self.loc.get('log_level_success').upper(): 'SUCCESS',
            self.loc.get('log_level_debug').upper(): 'DEBUG',
            self.loc.get('log_level_cmd').upper(): 'CMD',
            self.loc.get('log_level_detail').upper(): 'DETAIL'
        }
        selected_display_level = self.filter_combobox.get().strip().upper()
        internal_level = level_map.get(selected_display_level, 'ALL')
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        for entry in self._all_log_entries:
            if (not search_term or search_term in entry["message"].lower()) and (internal_level == 'ALL' or entry["level"] == internal_level):
                self.log_text.insert('end', f"[{entry['timestamp']}] ", ("DETAIL",))
                self.log_text.insert('end', f"{entry['message']}\n", (entry['level'],))
        self.log_text.see('end')
        self.log_text.config(state='disabled')
