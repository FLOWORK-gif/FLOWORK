#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\brain_provider_plugin\processor.py
# JUMLAH BARIS : 60
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.api_contract import BaseBrainProvider, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
class BrainProviderPlugin(BaseBrainProvider, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "pro"
    """
    A universal AI Brain provider for the Agent Host. It allows selecting any configured
    AI Provider to act as the agent's brain.
    """
    def __init__(self, module_id: str, services: dict):
        super().__init__(module_id, services)
        self.ai_manager = self.kernel.get_service("ai_provider_manager_service")
    def get_provider_name(self) -> str:
        return "AI Brain Provider"
    def is_ready(self) -> tuple[bool, str]:
        return (True, "")
    def think(self, objective: str, tools_string: str, history: list, last_observation: str) -> dict:
        self.logger("The 'think' method on a Brain Provider node should not be called directly.", "WARN")
        return {"error": "This node is a configuration provider for Agent Host and does not execute 'think' logic itself."}
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        status_updater("Brain Provider ready. Connect to an Agent Host.", "INFO")
        return {"payload": payload, "output_name": "brain_output"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        main_frame = ttk.Frame(parent_frame, padding=10)
        main_frame.pack(fill='both', expand=True)
        all_endpoints = self.ai_manager.get_available_providers() if self.ai_manager else {}
        display_to_id_map = {name: id for id, name in all_endpoints.items()}
        id_to_display_map = {id: name for id, name in all_endpoints.items()}
        endpoint_display_list = sorted(list(display_to_id_map.keys()))
        provider_display_var = StringVar()
        saved_endpoint_id = config.get('selected_ai_provider')
        if saved_endpoint_id and saved_endpoint_id in id_to_display_map:
            provider_display_var.set(id_to_display_map[saved_endpoint_id])
        LabelledCombobox(
            parent=main_frame,
            label_text=self.loc.get('brain_provider_select_label', fallback="AI Provider to Use as Brain:"),
            variable=provider_display_var,
            values=endpoint_display_list
        )
        class ProviderVar:
            def __init__(self, tk_var, name_map):
                self.tk_var = tk_var
                self.name_map = name_map
            def get(self):
                display_name = self.tk_var.get()
                return self.name_map.get(display_name)
        property_vars['selected_ai_provider'] = ProviderVar(provider_display_var, display_to_id_map)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'This is a brain node and has no direct data output to preview.'}]
