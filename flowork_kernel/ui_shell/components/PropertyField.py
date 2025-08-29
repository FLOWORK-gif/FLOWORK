#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\components\PropertyField.py
# JUMLAH BARIS : 15
#######################################################################

import ttkbootstrap as ttk
class PropertyField(ttk.Frame):
    def __init__(self, parent, label_text: str, variable, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text=label_text).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(self, textvariable=variable).grid(row=0, column=1, sticky="ew")
        self.pack(fill='x', pady=5)
