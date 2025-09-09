#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\views\components\PropertyField.py
# JUMLAH BARIS : 17
#######################################################################

import ttkbootstrap as ttk
from api_client.client import ApiClient # PENAMBAHAN OTOMATIS
class PropertyField(ttk.Frame):
    def __init__(self, parent, label_text: str, variable, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text=label_text).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(self, textvariable=variable).grid(row=0, column=1, sticky="ew")
        self.pack(fill='x', pady=5)
