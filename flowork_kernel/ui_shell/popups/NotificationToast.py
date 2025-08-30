#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\popups\NotificationToast.py
# JUMLAH BARIS : 58
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel
class NotificationToast(Toplevel):
    """
    Kelas untuk membuat jendela popup notifikasi (toast) yang bisa hilang otomatis.
    """
    def __init__(self, parent, title, message, level="INFO", duration=5000):
        super().__init__(parent)
        self.parent = parent
        self.duration = duration
        self.alpha = 0.0
        self.target_alpha = 0.9
        self.fade_step = 0.05
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.attributes('-alpha', self.alpha)
        style_map = {
            "SUCCESS": "success",
            "INFO": "info",
            "WARN": "warning",
            "ERROR": "danger"
        }
        bootstyle = style_map.get(level.upper(), "primary")
        main_frame = ttk.Frame(self, bootstyle=f"{bootstyle}.TFrame", padding=1, relief="solid")
        main_frame.pack(expand=True, fill="both")
        content_frame = ttk.Frame(main_frame, bootstyle="dark.TFrame", padding=(10, 5))
        content_frame.pack(expand=True, fill="both")
        title_label = ttk.Label(content_frame, text=title, font=("Helvetica", 10, "bold"), bootstyle=f"{bootstyle}.inverse")
        title_label.pack(fill="x")
        message_label = ttk.Label(content_frame, text=message, wraplength=280, font=("Helvetica", 9), bootstyle="secondary.inverse")
        message_label.pack(fill="x", pady=(2, 5))
        self.fade_in()
    def fade_in(self):
        """Animasi untuk memunculkan popup secara perlahan."""
        if self.alpha < self.target_alpha:
            self.alpha += self.fade_step
            self.attributes('-alpha', self.alpha)
            self.after(20, self.fade_in)
        else:
            self.after(self.duration, self.fade_out)
    def fade_out(self):
        """Animasi untuk menghilangkan popup secara perlahan."""
        if self.alpha > 0.0:
            self.alpha -= self.fade_step
            self.attributes('-alpha', self.alpha)
            self.after(30, self.fade_out)
        else:
            self.destroy()
    def set_position(self, x, y):
        """Menempatkan jendela popup di posisi yang ditentukan."""
        self.geometry(f"+{x}+{y}")
