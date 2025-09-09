#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\views\components\LabelledCombobox.py
# JUMLAH BARIS : 21
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from api_client.client import ApiClient # PENAMBAHAN OTOMATIS
class LabelledCombobox(ttk.Frame):
    """A reusable widget that combines a Label and a Combobox."""
    def __init__(self, parent, label_text: str, variable: StringVar, values: list, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)
        label = ttk.Label(self, text=label_text)
        label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        combobox = ttk.Combobox(self, textvariable=variable, values=values, state="readonly")
        combobox.grid(row=0, column=1, sticky="ew")
        self.pack(fill='x', pady=5)
