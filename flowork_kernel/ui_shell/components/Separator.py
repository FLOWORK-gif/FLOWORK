#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\components\Separator.py
# JUMLAH BARIS : 12
#######################################################################

import ttkbootstrap as ttk
class Separator(ttk.Separator):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, orient='horizontal', **kwargs)
        self.pack(fill='x', pady=15, padx=5)
