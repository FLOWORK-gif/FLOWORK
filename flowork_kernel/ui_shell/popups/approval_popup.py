#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\popups\approval_popup.py
# JUMLAH BARIS : 77
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel, Label, Button
class ApprovalPopup(Toplevel):
    """
    Kelas mandiri yang bertanggung jawab untuk membuat dan menampilkan
    jendela popup persetujuan manual.
    """
    def __init__(self, popup_manager, kernel, module_id, workflow_name, message):
        super().__init__(popup_manager.main_window)
        self.popup_manager = popup_manager
        self.kernel = kernel
        self.loc = kernel.get_service("localization_manager")
        self.title(self.loc.get('manual_approval_title', fallback="Persetujuan Manual Dibutuhkan"))
        self.transient(popup_manager.main_window)
        self.grab_set()
        self.resizable(False, False)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        self.configure(background=colors.get('bg', '#222'))
        self._create_widgets(workflow_name, message, colors)
        self._center_window()
    def _create_widgets(self, workflow_name, message, colors):
        """Membangun semua elemen UI di dalam popup."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        message_text = self.loc.get('manual_approval_message', workflow_name=workflow_name, node_message=message)
        Label(
            main_frame,
            text=message_text,
            wraplength=400,
            justify="center",
            background=colors.get('bg', '#222'),
            foreground=colors.get('fg', '#fff'),
            font=("Helvetica", 10)
        ).pack(pady=(0, 20))
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        Button(
            button_frame,
            text=self.loc.get('button_reject', fallback="Tolak"),
            command=lambda: self.popup_manager.handle_approval_response('REJECTED'),
            bg=colors.get('danger', '#dc3545'),
            fg=colors.get('light', '#fff'),
            relief="flat",
            width=15
        ).grid(row=0, column=0, padx=(0, 5), sticky="e")
        Button(
            button_frame,
            text=self.loc.get('button_approve', fallback="Setuju"),
            command=lambda: self.popup_manager.handle_approval_response('APPROVED'),
            bg=colors.get('success', '#28a745'),
            fg=colors.get('light', '#fff'),
            relief="flat",
            width=15
        ).grid(row=0, column=1, padx=(5, 0), sticky="w")
    def _center_window(self):
        """Menghitung dan mengatur posisi popup agar berada di tengah parent."""
        self.update_idletasks()
        parent_window = self.popup_manager.main_window
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()
        win_x = parent_x + (parent_width // 2) - (popup_width // 2)
        win_y = parent_y + (parent_height // 2) - (popup_height // 2)
        self.geometry(f"+{win_x}+{win_y}")
