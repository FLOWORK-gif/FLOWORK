#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\license_management_frame.py
# JUMLAH BARIS : 71
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox
import os
import threading
from flowork_kernel.api_client import ApiClient
class LicenseManagementFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.loc
        super().__init__(parent, text=self.loc.get("settings_license_title", fallback="License Management"), padding=15)
        self.api_client = ApiClient(kernel=self.kernel)
        self._build_widgets()
        self.load_settings_data(None)
    def _build_widgets(self):
        self.deactivate_button = ttk.Button(
            self,
            text=self.loc.get("settings_license_deactivate_button", fallback="Deactivate License on This Computer"),
            command=self._deactivate_license_action,
            bootstyle="danger-outline"
        )
        self.deactivate_button.pack(pady=5, padx=5, fill='x')
    def refresh_content(self):
        """Refreshes the UI state of the component based on the current kernel license status."""
        if hasattr(self, 'deactivate_button') and self.deactivate_button.winfo_exists():
            if self.kernel.current_user and self.kernel.is_premium_user():
                self.deactivate_button.config(state="normal")
            else:
                self.deactivate_button.config(state="disabled")
    def _deactivate_license_action(self):
        """
        Prompts for confirmation and then runs the license deactivation in a thread.
        """
        if messagebox.askyesno(
            self.loc.get("settings_license_deactivate_confirm_title", fallback="Confirm Deactivation"),
            self.loc.get("settings_license_deactivate_confirm_message"),
            parent=self
        ):
            self.deactivate_button.config(state="disabled")
            threading.Thread(target=self._deactivate_worker, daemon=True).start()
    def _deactivate_worker(self):
        """
        Worker function to call the deactivation method via ApiClient.
        """
        success, message = self.api_client.deactivate_license()
        self.after(0, self._on_deactivate_complete, success, message)
    def _on_deactivate_complete(self, success, message):
        """
        (MODIFIKASI) UI callback yang disederhanakan untuk mencegah race condition.
        """
        if success:
            messagebox.showinfo(
                self.loc.get("messagebox_success_title", fallback="Success"),
                message
            )
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Failed"), message, parent=self)
            if hasattr(self, 'deactivate_button') and self.deactivate_button.winfo_exists():
                self.deactivate_button.config(state="normal")
    def load_settings_data(self, settings_data):
        """This frame's UI is updated based on kernel state, not settings data."""
        self.refresh_content()
    def get_settings_data(self):
        """This frame doesn't save any settings, it only performs actions."""
        return {}
