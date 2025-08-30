#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\triggers\event_bus_trigger\config_ui.py
# JUMLAH BARIS : 23
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
class EventBusConfigUI(ttk.Frame):
    """UI untuk mengkonfigurasi pemicu Event Bus."""
    def __init__(self, parent, loc, initial_config):
        super().__init__(parent)
        self.loc = loc
        self.event_name_var = StringVar(value=initial_config.get('event_name', ''))
        ttk.Label(self, text=self.loc.get('eventbus_label_event_name', fallback="Nama Event:")).pack(anchor='w')
        ttk.Entry(self, textvariable=self.event_name_var, width=50).pack(fill='x', expand=True, pady=(0, 5))
        ttk.Label(self, text=self.loc.get('eventbus_help_text', fallback="Nama event yang akan didengarkan dari sistem."), style='secondary.TLabel').pack(anchor='w')
    def get_config(self):
        """Mengembalikan konfigurasi yang telah diatur oleh pengguna."""
        return {
            "event_name": self.event_name_var.get()
        }
