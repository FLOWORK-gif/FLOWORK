#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\popups\license_popup.py
# JUMLAH BARIS : 88
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel, Label, Button, StringVar
class LicensePopup(Toplevel):
    """
    Kelas mandiri yang bertanggung jawab untuk membuat dan menampilkan
    jendela popup yang meminta pengguna memasukkan kunci lisensi.
    """
    def __init__(self, parent_window, kernel, module_name, license_event, callback):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.kernel = kernel
        self.loc = kernel.get_service("localization_manager")
        self.license_event = license_event
        self.callback = callback
        self.license_key_var = StringVar()
        self.title(self.loc.get('license_popup_title', fallback="Aktivasi Fitur Premium"))
        self.transient(parent_window)
        self.grab_set()
        self.resizable(False, False)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        self.configure(background=colors.get('bg', '#222'))
        self._create_widgets(module_name, colors)
        self._center_window()
    def _create_widgets(self, module_name, colors):
        """Membangun semua elemen UI di dalam popup."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        info_text = self.loc.get('license_popup_message', module_name=module_name, fallback=f"Modul '{module_name}' adalah fitur premium.\n\nSilakan masukkan kunci lisensi Anda untuk mengaktifkan.")
        Label(
            main_frame,
            text=info_text,
            wraplength=400,
            justify="center",
            background=colors.get('bg', '#222'),
            foreground=colors.get('fg', '#fff'),
            font=("Helvetica", 10)
        ).pack(pady=(0, 20))
        ttk.Label(main_frame, text=self.loc.get('license_popup_entry_label', fallback="Kunci Lisensi:")).pack(anchor='w')
        entry = ttk.Entry(main_frame, textvariable=self.license_key_var, font=("Consolas", 11))
        entry.pack(fill='x', expand=True, pady=(2, 20))
        entry.focus_set()
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        cancel_button = ttk.Button(
            button_frame,
            text=self.loc.get('button_cancel', fallback="Batal"),
            command=self._on_cancel,
            style="secondary.TButton"
        )
        cancel_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        activate_button = ttk.Button(
            button_frame,
            text=self.loc.get('license_popup_activate_button', fallback="Aktifkan"),
            command=self._on_activate,
            style="success.TButton"
        )
        activate_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    def _on_activate(self):
        """Dipanggil saat tombol 'Aktifkan' ditekan."""
        entered_key = self.license_key_var.get()
        self.callback(entered_key, self.license_event)
        self.destroy()
    def _on_cancel(self):
        """Dipanggil saat tombol 'Batal' ditekan."""
        self.callback("", self.license_event)
        self.destroy()
    def _center_window(self):
        """Menghitung dan mengatur posisi popup agar berada di tengah parent."""
        self.update_idletasks()
        parent_x = self.parent_window.winfo_x()
        parent_y = self.parent_window.winfo_y()
        parent_width = self.parent_window.winfo_width()
        parent_height = self.parent_window.winfo_height()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()
        win_x = parent_x + (parent_width // 2) - (popup_width // 2)
        win_y = parent_y + (parent_height // 2) - (popup_height // 2)
        self.geometry(f"+{win_x}+{win_y}")
