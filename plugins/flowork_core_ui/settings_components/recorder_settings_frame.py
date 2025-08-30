#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\recorder_settings_frame.py
# JUMLAH BARIS : 47
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, filedialog
import os
class RecorderSettingsFrame(ttk.LabelFrame):
    """
    Manages the UI for screen recorder settings.
    """
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text="Screen Recorder Settings", padding=15)
        self.save_path_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        """Builds the UI components for this frame."""
        path_label = ttk.Label(self, text="Default Save Location:")
        path_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_frame = ttk.Frame(self)
        entry_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5)
        entry_frame.columnconfigure(0, weight=1)
        path_entry = ttk.Entry(entry_frame, textvariable=self.save_path_var)
        path_entry.pack(side="left", fill="x", expand=True)
        browse_button = ttk.Button(entry_frame, text="Browse...", command=self._browse_folder, width=10)
        browse_button.pack(side="left", padx=(5, 0))
        self.columnconfigure(1, weight=1)
    def _browse_folder(self):
        """Opens a dialog to select a folder."""
        default_path = os.path.join(os.path.expanduser("~"), "Videos")
        folder_selected = filedialog.askdirectory(initialdir=default_path)
        if folder_selected:
            self.save_path_var.set(folder_selected)
    def load_settings_data(self, settings_data):
        """Loads recorder settings from the provided data dictionary."""
        default_path = os.path.join(os.path.expanduser("~"), "Videos", "Flowork Tutorials")
        self.save_path_var.set(settings_data.get("recorder_save_path", default_path))
    def get_settings_data(self) -> dict:
        """Returns the current recorder settings from the UI."""
        return {
            "recorder_save_path": self.save_path_var.get()
        }
