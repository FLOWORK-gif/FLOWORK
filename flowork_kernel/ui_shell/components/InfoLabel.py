#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\components\InfoLabel.py
# JUMLAH BARIS : 14
#######################################################################

import ttkbootstrap as ttk
class InfoLabel(ttk.Frame):
    def __init__(self, parent, text: str, **kwargs):
        super().__init__(parent, padding=10, **kwargs)
        label = ttk.Label(self, text=text, wraplength=350, justify='left', bootstyle="secondary")
        label.pack(fill='x')
        self.pack(fill='x', pady=5)
