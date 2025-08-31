#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\error_handler_frame.py
# JUMLAH BARIS : 37
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
class ErrorHandlerFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_error_handler_title", fallback="Global Error Handler Settings"), padding=15)
        self.error_handler_enabled_var = BooleanVar()
        self.error_handler_preset_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        enabled_check = ttk.Checkbutton(self, text=self.loc.get("settings_error_handler_enable_label", fallback="Enable Global Error Handler"), variable=self.error_handler_enabled_var)
        enabled_check.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        preset_label = ttk.Label(self, text=self.loc.get("settings_error_handler_preset_label", fallback="Select Error Handler Preset:"))
        preset_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        preset_manager = self.kernel.get_service("preset_manager")
        preset_list = [""] + preset_manager.get_preset_list() if preset_manager else [""]
        preset_combo = ttk.Combobox(self, textvariable=self.error_handler_preset_var, values=preset_list, state="readonly")
        preset_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.columnconfigure(1, weight=1)
    def load_settings_data(self, settings_data):
        """Loads error handler settings from the provided data dictionary."""
        self.error_handler_enabled_var.set(settings_data.get("global_error_handler_enabled", False))
        self.error_handler_preset_var.set(settings_data.get("global_error_workflow_preset", ""))
    def get_settings_data(self):
        """Returns the current error handler settings from the UI."""
        return {
            "global_error_handler_enabled": self.error_handler_enabled_var.get(),
            "global_error_workflow_preset": self.error_handler_preset_var.get()
        }
