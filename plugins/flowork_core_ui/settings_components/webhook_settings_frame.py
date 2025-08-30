#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\webhook_settings_frame.py
# JUMLAH BARIS : 38
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
class WebhookSettingsFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_webhook_title", fallback="Webhook Settings"), padding=15)
        self.webhook_enabled_var = BooleanVar()
        self.webhook_port_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        webhook_check = ttk.Checkbutton(self, text=self.loc.get("settings_webhook_enable_label", fallback="Enable Webhook/API Server"), variable=self.webhook_enabled_var)
        webhook_check.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        port_label = ttk.Label(self, text=self.loc.get("settings_webhook_port_label", fallback="Server Port:"))
        port_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        port_entry = ttk.Entry(self, textvariable=self.webhook_port_var, width=10)
        port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    def load_settings_data(self, settings_data):
        """Loads webhook settings from the provided data dictionary."""
        self.webhook_enabled_var.set(settings_data.get("webhook_enabled", False))
        self.webhook_port_var.set(str(settings_data.get("webhook_port", 8989)))
    def get_settings_data(self) -> dict:
        """Returns the current webhook settings from the UI."""
        try:
            port = int(self.webhook_port_var.get())
            return {
                "webhook_enabled": self.webhook_enabled_var.get(),
                "webhook_port": port
            }
        except ValueError:
            raise ValueError("Port must be a valid number.")
