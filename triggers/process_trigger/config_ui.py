#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\triggers\process_trigger\config_ui.py
# JUMLAH BARIS : 32
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
class ProcessConfigUI(ttk.Frame):
    """UI untuk mengkonfigurasi pemicu Proses."""
    def __init__(self, parent, loc, initial_config):
        super().__init__(parent)
        self.loc = loc
        self.process_name_var = StringVar(value=initial_config.get('process_name', ''))
        self.on_start_var = BooleanVar(value=initial_config.get('on_start', True))
        self.on_stop_var = BooleanVar(value=initial_config.get('on_stop', True))
        content_frame = ttk.Frame(self)
        content_frame.pack(fill='both', expand=True)
        ttk.Label(content_frame, text=self.loc.get('process_label_name', fallback="Nama Proses (e.g., notepad.exe):")).pack(anchor='w', pady=(0,2))
        ttk.Entry(content_frame, textvariable=self.process_name_var).pack(fill='x', expand=True, pady=(0,10))
        event_frame = ttk.LabelFrame(content_frame, text=self.loc.get('process_label_events', fallback="Picu Saat"))
        event_frame.pack(fill='x', expand=True, pady=(5,0))
        ttk.Checkbutton(event_frame, text=self.loc.get('process_event_started', fallback="Proses Dimulai"), variable=self.on_start_var).pack(anchor='w', padx=5, pady=(5,2))
        ttk.Checkbutton(event_frame, text=self.loc.get('process_event_stopped', fallback="Proses Berhenti"), variable=self.on_stop_var).pack(anchor='w', padx=5, pady=(2,5))
    def get_config(self):
        """Mengembalikan konfigurasi yang telah diatur oleh pengguna."""
        return {
            "process_name": self.process_name_var.get(),
            "on_start": self.on_start_var.get(),
            "on_stop": self.on_stop_var.get()
        }
