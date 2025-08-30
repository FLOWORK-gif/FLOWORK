#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\article_generator_tools\processor.py
# JUMLAH BARIS : 107
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, EnumVarWrapper
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
class ArticleGeneratorModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    A simple, single-purpose module to generate an article from a prompt using a specific AI provider.
    This is a 'dumb tool' designed to be commanded by an Agent Host.
    (UPGRADED V2) More flexible prompt sourcing.
    """
    TIER = "pro"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        provider_id = config.get('selected_ai_provider')
        prompt_variable_options = [
            config.get('prompt_source_variable', 'data.prompt_artikel'), # 1. Check the configured variable first
            'data.prompt'                                              # 2. Fallback to the agent's generic key
        ]
        prompt_text = None
        used_variable = None
        for var_option in prompt_variable_options:
            value = get_nested_value(payload, var_option)
            if value and isinstance(value, str):
                prompt_text = value
                used_variable = var_option
                self.logger(f"ArticleGenerator found prompt in '{used_variable}'.", "DEBUG") # English Log
                break
        if not provider_id:
            raise ValueError("AI Provider/Model has not been selected in the Article Generator properties.")
        if not prompt_text:
            raise ValueError(f"Could not find a valid text prompt in the payload. Checked: {', '.join(prompt_variable_options)}")
        status_updater(f"Sending prompt to '{provider_id}'...", "INFO")
        self.logger(f"ArticleGenerator: Sending prompt from '{used_variable}' to '{provider_id}' for generation.", "INFO") # English Log
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        if not ai_manager:
            raise RuntimeError("AIProviderManagerService is not available.")
        try:
            response = ai_manager.query_ai_by_task('text', prompt_text, endpoint_id=provider_id)
            if "error" in response:
                raise ValueError(response["error"])
            article_text = response.get('data')
            if not article_text:
                raise ValueError("The AI provider returned an empty response.")
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data']['article_text'] = article_text
            status_updater("Article generated successfully.", "SUCCESS")
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            error_msg = f"Failed to generate article: {e}"
            self.logger(error_msg, "ERROR") # English Log
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        ai_frame = ttk.LabelFrame(parent_frame, text="AI Configuration")
        ai_frame.pack(fill='x', padx=5, pady=10)
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        all_endpoints = ai_manager.get_available_providers() if ai_manager else {}
        display_to_id_map = {name: id for id, name in all_endpoints.items()}
        id_to_display_map = {id: name for id, name in all_endpoints.items()}
        endpoint_display_list = sorted(list(display_to_id_map.keys()))
        provider_display_var = StringVar()
        saved_endpoint_id = config.get('selected_ai_provider')
        if saved_endpoint_id and saved_endpoint_id in id_to_display_map:
            provider_display_var.set(id_to_display_map[saved_endpoint_id])
        LabelledCombobox(
            parent=ai_frame,
            label_text=self.loc.get('prop_article_gen_provider_label', fallback="AI Provider/Model to Use:"),
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
        property_vars['prompt_source_variable'] = StringVar(value=config.get('prompt_source_variable', 'data.prompt_artikel'))
        LabelledCombobox(
            parent=ai_frame,
            label_text=self.loc.get('prop_article_gen_prompt_source_label', fallback="Prompt from Variable:"),
            variable=property_vars['prompt_source_variable'],
            values=list(available_vars.keys())
        )
        return property_vars
    def get_dynamic_output_schema(self, config):
        return [{
            "name": "data.article_text",
            "type": "string",
            "description": "The final article text generated by the AI."
        }]
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'AI generation is a live process.'}]
