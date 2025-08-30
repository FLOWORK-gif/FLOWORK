#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\notification_settings_frame.py
# JUMLAH BARIS : 45
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
class NotificationSettingsFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_notifications_title", fallback="Popup Notification Settings"), padding=15)
        self.notifications_enabled_var = BooleanVar()
        self.notifications_duration_var = StringVar()
        self.notifications_position_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        enabled_check = ttk.Checkbutton(self, text=self.loc.get("settings_notifications_enable_label", fallback="Enable Popup Notifications"), variable=self.notifications_enabled_var)
        enabled_check.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        duration_label = ttk.Label(self, text=self.loc.get("settings_notifications_duration_label", fallback="Display Duration (seconds):"))
        duration_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        duration_entry = ttk.Entry(self, textvariable=self.notifications_duration_var, width=10)
        duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        position_label = ttk.Label(self, text=self.loc.get("settings_notifications_position_label", fallback="Popup Position:"))
        position_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        position_combo = ttk.Combobox(self, textvariable=self.notifications_position_var, values=["bottom_right", "top_right", "bottom_left", "top_left"], state="readonly")
        position_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    def load_settings_data(self, settings_data):
        """Loads notification settings from the provided data dictionary."""
        self.notifications_enabled_var.set(settings_data.get("notifications_enabled", True))
        self.notifications_duration_var.set(str(settings_data.get("notifications_duration_seconds", 5)))
        self.notifications_position_var.set(settings_data.get("notifications_position", "bottom_right"))
    def get_settings_data(self):
        """Returns the current notification settings from the UI."""
        try:
            duration = int(self.notifications_duration_var.get())
            return {
                "notifications_enabled": self.notifications_enabled_var.get(),
                "notifications_duration_seconds": duration,
                "notifications_position": self.notifications_position_var.get()
            }
        except ValueError:
            raise ValueError("Duration must be a valid number.")
