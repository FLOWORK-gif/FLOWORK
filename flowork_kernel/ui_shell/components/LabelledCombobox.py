#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\components\LabelledCombobox.py
# JUMLAH BARIS : 19
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
class LabelledCombobox(ttk.Frame):
    """A reusable widget that combines a Label and a Combobox."""
    def __init__(self, parent, label_text: str, variable: StringVar, values: list, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)
        label = ttk.Label(self, text=label_text)
        label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        combobox = ttk.Combobox(self, textvariable=variable, values=values, state="readonly")
        combobox.grid(row=0, column=1, sticky="ew")
        self.pack(fill='x', pady=5)
