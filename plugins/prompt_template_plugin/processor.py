#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\prompt_template_plugin\processor.py
# JUMLAH BARIS : 76
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
from flowork_kernel.api_client import ApiClient
class PromptTemplateModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    (REMASTERED V2) This module now fetches a list of pre-saved templates
    from the PromptManagerService and allows the user to select one via a dropdown.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.prompt_manager = services.get("prompt_manager_service")
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        selected_prompt_id = config.get('selected_prompt_id')
        if not selected_prompt_id:
            raise ValueError("No prompt template has been selected in the node properties.")
        if not self.prompt_manager:
            raise RuntimeError("PromptManagerService is not available.")
        status_updater(f"Fetching prompt template (ID: {selected_prompt_id[:8]}...)", "INFO")
        prompt_data = self.prompt_manager.get_prompt(selected_prompt_id)
        if not prompt_data or 'content' not in prompt_data:
            raise FileNotFoundError(f"Could not find or load the prompt template with ID: {selected_prompt_id}")
        template_content = prompt_data['content']
        if 'data' not in payload or not isinstance(payload['data'], dict):
            payload['data'] = {}
        payload['data']['prompt_template'] = template_content
        status_updater("Prompt template loaded successfully.", "SUCCESS")
        return {"payload": payload, "output_name": "success"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        api_client = ApiClient(kernel=self.kernel)
        success, prompts = api_client.get_prompts()
        if not success:
            ttk.Label(parent_frame, text=f"Error fetching prompts: {prompts}", bootstyle="danger").pack(padx=5, pady=10)
            return {}
        prompt_map = {p['name']: p['id'] for p in prompts}
        prompt_names = sorted(prompt_map.keys())
        selected_prompt_id = config.get('selected_prompt_id')
        current_selection_name = ""
        if selected_prompt_id:
            for name, pid in prompt_map.items():
                if pid == selected_prompt_id:
                    current_selection_name = name
                    break
        prompt_name_var = StringVar(value=current_selection_name)
        LabelledCombobox(
            parent=parent_frame,
            label_text=self.loc.get('prop_prompt_template_select_label', fallback="Select a Prompt Template:"),
            variable=prompt_name_var,
            values=prompt_names
        )
        class PromptIdVar:
            """A proxy to translate the selected name back to an ID for saving."""
            def __init__(self, tk_var, mapping):
                self.tk_var = tk_var
                self.mapping = mapping
            def get(self):
                selected_name = self.tk_var.get()
                return self.mapping.get(selected_name)
        property_vars['selected_prompt_id'] = PromptIdVar(prompt_name_var, prompt_map)
        return property_vars
    def get_data_preview(self, config: dict):
        selected_id = config.get('selected_prompt_id')
        if not selected_id:
            return [{'status': 'No prompt selected.'}]
        return [{'status': f"Will load the content of prompt template with ID: {selected_id[:8]}..."}]
