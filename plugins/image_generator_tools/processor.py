#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\image_generator_tools\processor.py
# JUMLAH BARIS : 75
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, EnumVarWrapper
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
from flowork_kernel.ui_shell.components.InfoLabel import InfoLabel
class ImageGeneratorModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    (REMASTERED V3) A tool to generate an image. It now simply delegates the task to the
    globally configured AI model for image generation via the smart AIProviderManager.
    """
    TIER = "pro"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        prompt_variable = config.get('prompt_source_variable', 'data.prompt_gambar')
        prompt_text = get_nested_value(payload, prompt_variable)
        if not prompt_text or not isinstance(prompt_text, str):
             prompt_text = get_nested_value(payload, 'data.prompt')
        if not prompt_text or not isinstance(prompt_text, str):
            raise ValueError(f"Could not find a valid text prompt in payload. Checked '{prompt_variable}' and 'data.prompt'.")
        status_updater("Sending image generation task to Kernel...", "INFO") # English Log
        self.logger(f"ImageGenerator: Delegating image generation task for prompt: '{prompt_text[:50]}...'", "INFO") # English Log
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        if not ai_manager:
            raise RuntimeError("AIProviderManagerService is not available.")
        try:
            response = ai_manager.query_ai_by_task('image', prompt_text)
            if "error" in response:
                raise ValueError(response["error"])
            image_path = response.get('data')
            if not image_path:
                raise ValueError("The AI did not return a valid image path.")
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data']['generated_image_path'] = image_path
            status_updater("Image generated successfully.", "SUCCESS")
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            error_msg = f"Failed to generate image: {e}"
            self.logger(error_msg, "ERROR") # English Log
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        InfoLabel(
            parent=parent_frame,
            text=self.loc.get('prop_image_gen_model_info', fallback="The AI model for image generation is configured globally in the main application Settings."),
            bootstyle="info"
        )
        property_vars['prompt_source_variable'] = StringVar(value=config.get('prompt_source_variable', 'data.prompt_gambar'))
        LabelledCombobox(
            parent=parent_frame,
            label_text=self.loc.get('prop_image_gen_prompt_source_label', fallback="Prompt from Variable:"),
            variable=property_vars['prompt_source_variable'],
            values=list(available_vars.keys())
        )
        return property_vars
    def get_dynamic_output_schema(self, config):
        return [{
            "name": "data.generated_image_path",
            "type": "string",
            "description": "The full local path to the generated image file."
        }]
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'AI image generation is a live process.'}]
