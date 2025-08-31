#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\ai_provider_settings_frame.py
# JUMLAH BARIS : 95
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
import os
class AiProviderSettingsFrame(ttk.LabelFrame):
    """
    [MODIFIED V2] Displays a granular, task-based configuration for default AI models
    instead of a single master AI. Each task type can be mapped to a different provider.
    """
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get('setting_ai_config_title', fallback="Default AI Model Configuration"), padding=15)
        self.provider_vars = {}
        self.endpoint_display_to_id_map = {}
        self.task_types = {
            "text": "setting_ai_for_text",
            "music": "setting_ai_for_music",
            "tts": "setting_ai_for_tts",
            "image": "setting_ai_for_image",
            "video": "setting_ai_for_video",
            "other": "setting_ai_for_other"
        }
        self.gpu_layers_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        """Builds the UI components for this frame."""
        self.columnconfigure(1, weight=1)
        help_text = ttk.Label(self, text=self.loc.get('setting_ai_config_help', fallback="Select the default AI model for each task type. Features like AI Architect will use these settings."), wraplength=400, justify="left", bootstyle="secondary")
        help_text.grid(row=0, column=0, columnspan=2, padx=5, pady=(0,15), sticky="w")
        row_counter = 1
        for key, label_key in self.task_types.items():
            self.provider_vars[key] = StringVar()
            label_text = self.loc.get(label_key, fallback=f"{key.title()}:")
            label = ttk.Label(self, text=label_text)
            label.grid(row=row_counter, column=0, padx=(0, 10), pady=5, sticky="w")
            provider_combo = ttk.Combobox(self, textvariable=self.provider_vars[key], state="readonly")
            provider_combo.grid(row=row_counter, column=1, padx=5, pady=5, sticky="ew")
            row_counter += 1
        ttk.Separator(self).grid(row=row_counter, column=0, columnspan=2, sticky="ew", pady=10)
        row_counter += 1
        gpu_label = ttk.Label(self, text="GPU Offload Layers (GGUF):") # English Hardcode
        gpu_label.grid(row=row_counter, column=0, padx=5, pady=5, sticky="w")
        gpu_entry = ttk.Entry(self, textvariable=self.gpu_layers_var, width=10)
        gpu_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky="w")
    def load_settings_data(self, settings_data):
        """Loads the list of endpoints and sets the current settings for each task type."""
        self.gpu_layers_var.set(str(settings_data.get("ai_gpu_layers", 40)))
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        if not ai_manager:
            for i, (key, label_key) in enumerate(self.task_types.items()):
                combo = self.grid_slaves(row=i + 1, column=1)[0]
                combo['values'] = ["AI Manager Service not found"]
            return
        all_endpoints = ai_manager.get_available_providers()
        self.endpoint_display_to_id_map.clear()
        display_names = []
        for endpoint_id, display_name in all_endpoints.items():
             self.endpoint_display_to_id_map[display_name] = endpoint_id
             display_names.append(display_name)
        sorted_display_names = sorted(display_names)
        for i, (key, label_key) in enumerate(self.task_types.items()):
            combo = self.grid_slaves(row=i + 1, column=1)[0]
            combo['values'] = sorted_display_names
            setting_key = f"ai_model_for_{key}"
            saved_endpoint_id = settings_data.get(setting_key)
            found_saved = False
            if saved_endpoint_id:
                for display, endpoint_id in self.endpoint_display_to_id_map.items():
                    if endpoint_id == saved_endpoint_id:
                        self.provider_vars[key].set(display)
                        found_saved = True
                        break
            if not found_saved and sorted_display_names:
                self.provider_vars[key].set(sorted_display_names[0])
    def get_settings_data(self):
        """Returns all the configured AI settings to be saved."""
        settings_to_save = {}
        for key, var in self.provider_vars.items():
            selected_display_name = var.get()
            if selected_display_name in self.endpoint_display_to_id_map:
                endpoint_id_to_save = self.endpoint_display_to_id_map[selected_display_name]
                setting_key = f"ai_model_for_{key}"
                settings_to_save[setting_key] = endpoint_id_to_save
        try:
            settings_to_save["ai_gpu_layers"] = int(self.gpu_layers_var.get())
        except (ValueError, TypeError):
            settings_to_save["ai_gpu_layers"] = 40
        return settings_to_save
