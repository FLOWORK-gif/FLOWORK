#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\custom_widgets\tooltip.py
# JUMLAH BARIS : 51
#######################################################################

import ttkbootstrap as ttk
from tkinter import TclError
class ToolTip:
    """Membuat tooltip (hover text) untuk sebuah widget."""
    def __init__(self, widget):
        self.widget = widget
        self.text = "" # Inisialisasi dengan string kosong
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = ttk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        try:
            colors = self.widget.winfo_toplevel().kernel.theme_manager.get_colors()
            bg_color = colors.get('bg', '#222222')
            fg_color = colors.get('fg', '#FFFFFF')
        except (AttributeError, TclError):
            bg_color="#222222"
            fg_color = "#FFFFFF"
        label = ttk.Label(
            tw,
            text=self.text,
            justify='left',
            background=bg_color,
            foreground=fg_color,
            relief='solid',
            borderwidth=1,
            font=("tahoma", "8", "normal"),
            padding=4
        )
        label.pack(ipadx =1)
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window= None
    def update_text(self, new_text):
        self.text = new_text
