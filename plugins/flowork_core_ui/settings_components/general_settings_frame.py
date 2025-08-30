#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\general_settings_frame.py
# JUMLAH BARIS : 53
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
class GeneralSettingsFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_general_title", fallback="General Settings"), padding=15)
        self.lang_var = StringVar()
        self.theme_var = StringVar()
        self.available_themes = {}
        self._build_widgets()
    def _build_widgets(self):
        lang_label = ttk.Label(self, text=self.loc.get("settings_language_label", fallback="Interface Language:"))
        lang_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        lang_combo = ttk.Combobox(self, textvariable=self.lang_var, values=self.loc.get_available_languages_display(), state="readonly")
        lang_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        theme_label = ttk.Label(self, text=self.loc.get("settings_theme_label", fallback="Application Theme:"))
        theme_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.theme_combo = ttk.Combobox(self, textvariable=self.theme_var, values=[], state="readonly")
        self.theme_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.columnconfigure(1, weight=1)
    def load_settings_data(self, settings_data):
        """Loads settings data provided by the parent coordinator."""
        theme_manager = self.kernel.get_service("theme_manager")
        if theme_manager:
            self.available_themes = theme_manager.get_all_themes()
            theme_names = [d.get('name', 'Unknown') for d in self.available_themes.values()]
            self.theme_combo['values'] = sorted(theme_names)
        else:
            self.available_themes = {}
        active_theme_id = settings_data.get("theme", "flowork_default")
        active_theme_name = self.available_themes.get(active_theme_id, {}).get('name', '')
        lang_code = settings_data.get("language", "id")
        lang_display_name = self.loc.language_map.get(lang_code, "Bahasa Indonesia")
        self.lang_var.set(lang_display_name)
        self.theme_var.set(active_theme_name)
    def get_settings_data(self) -> dict:
        """Returns the current settings from the UI as a dictionary."""
        selected_theme_name = self.theme_var.get()
        theme_id_to_save = next((tid for tid, data in self.available_themes.items() if data.get('name') == selected_theme_name), "flowork_default")
        selected_lang_display = self.lang_var.get()
        lang_code_to_save = next((code for code, display in self.loc.language_map.items() if display == selected_lang_display), "id")
        return {
            "language": lang_code_to_save,
            "theme": theme_id_to_save
        }
