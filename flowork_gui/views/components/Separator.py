#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\views\components\Separator.py
# JUMLAH BARIS : 14
#######################################################################

import ttkbootstrap as ttk
from api_client.client import ApiClient # PENAMBAHAN OTOMATIS
class Separator(ttk.Separator):
    def __init__(self, parent, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, orient='horizontal', **kwargs)
        self.pack(fill='x', pady=15, padx=5)
