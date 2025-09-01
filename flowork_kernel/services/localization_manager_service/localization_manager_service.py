#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\localization_manager_service\localization_manager_service.py
# JUMLAH BARIS : 159
#######################################################################

import os
import json
from ..base_service import BaseService
class LocalizationManagerService(BaseService):
    """
    Manages all multilingual application text from a centralized source and standalone modules.
    This service is critical and must be loaded early in the kernel's lifecycle.
    [FIXED] Now correctly scans the 'triggers' directory for localization files.
    """
    SETTINGS_FILE = "settings.json"
    SETTINGS_DIR_NAME = "data"
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.locales_path = self.kernel.locales_path
        self.settings_dir = self.kernel.data_path
        self.settings_file_path = os.path.join(self.settings_dir, self.SETTINGS_FILE)
        self.languages = {}
        self.current_lang = "en"
        self._settings_cache = {}
        self.language_map = {
            "en": "English",
            "id": "Bahasa Indonesia"
        }
        os.makedirs(self.locales_path, exist_ok=True)
        os.makedirs(self.settings_dir, exist_ok=True)
        self.kernel.write_to_log("Service 'LocalizationManager' initialized.", "DEBUG")
        self.load_base_languages()
        self._load_settings()
    def get_available_languages_display(self):
        return [self.language_map[lang_code] for lang_code in self.languages.keys() if lang_code in self.language_map]
    def get_current_language_code(self):
        return self.current_lang
    def load_base_languages(self):
        self.kernel.write_to_log("LocalizationManager: Loading base languages...", "DEBUG")
        for filename in os.listdir(self.locales_path):
            if filename.endswith(".json"):
                lang_id = os.path.splitext(filename)[0]
                filepath = os.path.join(self.locales_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        if lang_id not in self.languages:
                            self.languages[lang_id] = {}
                        self.languages[lang_id].update(json.load(f))
                except Exception as e:
                    self.kernel.write_to_log(f"Failed to load base language '{lang_id}': {e}", "ERROR")
        if "en" not in self.languages:
            self.kernel.write_to_log("Warning: Base language file 'en.json' not found. Creating emergency entry.", "WARN")
            self.languages["en"] = {"app_title": "Flowork (Fallback)"}
    def load_all_languages(self):
        self.kernel.write_to_log("LocalizationManager: Starting language scan and merge...", "INFO")
        self.languages.clear()
        self.load_base_languages()
        module_manager = self.kernel.get_service("module_manager_service")
        widget_manager = self.kernel.get_service("widget_manager_service")
        trigger_manager = self.kernel.get_service("trigger_manager_service")
        loaded_modules_data = {}
        if module_manager:
            loaded_modules_data = module_manager.loaded_modules
        items_to_scan = {
            **(loaded_modules_data if loaded_modules_data else {}),
            **(widget_manager.loaded_widgets if widget_manager else {}),
            **(trigger_manager.loaded_triggers if trigger_manager else {})
        }
        for item_id, item_data in items_to_scan.items():
            if item_data.get('is_paused', False):
                continue
            component_path = item_data.get('path')
            if not component_path:
                continue
            module_locales_path = os.path.join(component_path, 'locales')
            if os.path.isdir(module_locales_path):
                for filename in os.listdir(module_locales_path):
                    if filename.endswith(".json"):
                        lang_id = os.path.splitext(filename)[0]
                        filepath = os.path.join(module_locales_path, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                item_lang_data = json.load(f)
                                if lang_id not in self.languages:
                                    self.languages[lang_id] = {}
                                self.languages[lang_id].update(item_lang_data)
                        except Exception as e:
                            self.kernel.write_to_log(f"Failed to merge language '{lang_id}' from '{item_id}': {e}", "ERROR")
        self.kernel.write_to_log("LocalizationManager: Language merge complete.", "INFO")
    def set_language(self, lang_id):
        if lang_id in self.languages:
            self.current_lang = lang_id
            self.save_setting("language", lang_id)
            self.kernel.write_to_log(f"LocalizationManager: Language set to '{lang_id}'.", "INFO")
            return True
        self.kernel.write_to_log(f"LocalizationManager: Language '{lang_id}' not found.", "WARN")
        return False
    def get(self, key, **kwargs):
        stripped_key = key.strip()
        lang_data = self.languages.get(self.current_lang)
        if lang_data and stripped_key in lang_data:
            text = lang_data[stripped_key]
            return text.format(**kwargs) if kwargs else text
        lang_data_en = self.languages.get("en")
        if lang_data_en and stripped_key in lang_data_en:
            return lang_data_en[stripped_key].format(**kwargs) if kwargs else lang_data_en[stripped_key]
        fallback_text = kwargs.get('fallback')
        if fallback_text is None:
            return f"[{key}]"
        if isinstance(fallback_text, str):
            return fallback_text.format(**kwargs) if kwargs else fallback_text
        return fallback_text
    def _load_settings(self):
        try:
            current_settings = {}
            if os.path.exists(self.settings_file_path):
                with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                    current_settings = json.load(f)
            defaults = {
                "language": "id", "theme": "flowork_default", "webhook_enabled": False,
                "webhook_port": 8989, "global_error_handler_enabled": False,
                "global_error_workflow_preset": "", "premium_license_active": False,
                "premium_expiry_date": None, "premium_user_email": None,
                "last_run_time": None, "notifications_enabled": True,
                "notifications_duration_seconds": 5, "notifications_position": "bottom_right",
                "license_seal": None
            }
            settings_changed = False
            for key, value in defaults.items():
                if key not in current_settings:
                    current_settings[key] = value
                    settings_changed = True
            if settings_changed:
                with open(self.settings_file_path, 'w', encoding='utf-8') as f:
                    json.dump(current_settings, f, indent=4)
            self._settings_cache = current_settings
            loaded_lang = self._settings_cache.get("language", "id")
            if loaded_lang in self.languages:
                self.current_lang = loaded_lang
            else:
                self.current_lang = "id"
        except Exception as e:
            self.kernel.write_to_log(f"LocalizationManager: Failed to load settings: {e}", "ERROR")
            self._settings_cache = {}
    def _save_settings(self, settings_to_save):
        try:
            with open(self.settings_file_path, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=4)
            self._settings_cache = settings_to_save
        except Exception as e:
            self.kernel.write_to_log(f"LocalizationManager: Failed to save settings: {e}", "ERROR")
    def save_setting(self, key, value):
        current_settings = self._settings_cache.copy()
        current_settings[key] = value
        self._save_settings(current_settings)
    def get_setting(self, key, default=None):
        return self._settings_cache.get(key, default)
