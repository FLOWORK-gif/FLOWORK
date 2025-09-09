#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\views\components\InfoLabel.py
# JUMLAH BARIS : 16
#######################################################################

import ttkbootstrap as ttk
from api_client.client import ApiClient # PENAMBAHAN OTOMATIS
class InfoLabel(ttk.Frame):
    def __init__(self, parent, text: str, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, padding=10, **kwargs)
        label = ttk.Label(self, text=text, wraplength=350, justify='left', bootstyle="secondary")
        label.pack(fill='x')
        self.pack(fill='x', pady=5)
