from flowork_kernel.core import build_security
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\stable_diffusion_xl_module\processor.py
# JUMLAH BARIS : 146
#######################################################################

import os
import time
import ttkbootstrap as ttk
from tkinter import StringVar, IntVar, DoubleVar, scrolledtext, filedialog
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.utils.file_helper import sanitize_filename
import shutil
class StableDiffusionXLModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    (REMASTERED V4 - Final) Acts as a smart manager that gathers all necessary parameters
    and delegates the image generation task to the central AIProviderManagerService,
    ensuring consistent, high-quality results.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
        self.output_dir = os.path.join(self.kernel.data_path, "generated_images")
        os.makedirs(self.output_dir, exist_ok=True)
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        model_folder_name = config.get('model_folder')
        endpoint_id = f"(Local Model) {model_folder_name}"
        prompt = get_nested_value(payload, config.get('prompt_source_variable')) or \
                 get_nested_value(payload, 'data.prompt') or \
                 config.get('prompt')
        if not prompt:
            raise ValueError("A prompt is required, either from a payload variable or manual input.")
        generation_params = {
            "negative_prompt": config.get('negative_prompt', ''),
            "width": config.get('width', 1024),
            "height": config.get('height', 1024),
            "guidance_scale": config.get('guidance_scale', 7.5),
            "num_inference_steps": config.get('num_inference_steps', 30)
        }
        filename_prefix = config.get('output_filename_prefix', '')
        user_output_folder = config.get('output_folder', '').strip()
        save_dir = user_output_folder if user_output_folder and os.path.isdir(user_output_folder) else self.output_dir
        try:
            ai_manager = self.kernel.get_service("ai_provider_manager_service")
            if not ai_manager:
                raise RuntimeError("AIProviderManagerService is not available.")
            status_updater(f"Delegating generation to {model_folder_name}...", "INFO")
            response = ai_manager.query_ai_by_task(
                'image',
                prompt,
                endpoint_id=endpoint_id,
                **generation_params  # Kirim semua parameter tambahan
            )
            if "error" in response:
                raise RuntimeError(response['error'])
            image_path_from_service = response.get('data')
            if not image_path_from_service or not os.path.exists(image_path_from_service):
                raise FileNotFoundError("AI Manager service did not return a valid image path.")
            sanitized_prefix = sanitize_filename(filename_prefix) or sanitize_filename(prompt[:20])
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            final_filename = f"{sanitized_prefix}_{timestamp}.png"
            final_output_path = os.path.join(save_dir, final_filename)
            shutil.move(image_path_from_service, final_output_path)
            self.logger(f"Image moved to final destination: {final_output_path}", "INFO")
            status_updater("Image generated successfully!", "SUCCESS")
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data']['image_path'] = final_output_path
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            self.logger(f"An error occurred during image generation: {e}", "ERROR")
            payload['error'] = str(e)
            return {"payload": payload, "output_name": "error"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        model_frame = ttk.LabelFrame(parent_frame, text="Model and Prompt")
        model_frame.pack(fill='x', padx=5, pady=10)
        image_models_path = os.path.join(self.kernel.project_root_path, "ai_models", "image")
        available_models = []
        if os.path.isdir(image_models_path):
            available_models = [d for d in os.listdir(image_models_path) if os.path.isdir(os.path.join(image_models_path, d))]
        property_vars['model_folder'] = StringVar(value=config.get('model_folder', ''))
        LabelledCombobox(parent=model_frame, label_text="AI Model:", variable=property_vars['model_folder'], values=sorted(available_models))
        property_vars['prompt_source_variable'] = StringVar(value=config.get('prompt_source_variable', ''))
        LabelledCombobox(parent=model_frame, label_text=self.loc.get('prop_prompt_source_label', fallback="Prompt from Variable:"), variable=property_vars['prompt_source_variable'], values=[''] + list(available_vars.keys()))
        ttk.Label(model_frame, text=self.loc.get('prop_prompt_label', fallback="Prompt (Fallback):")).pack(fill='x', padx=5, pady=(5,0))
        prompt_editor = scrolledtext.ScrolledText(model_frame, height=5, font=("Consolas", 10))
        prompt_editor.pack(fill="x", expand=True, padx=5, pady=(0, 5))
        prompt_editor.insert('1.0', config.get('prompt', ''))
        property_vars['prompt'] = prompt_editor
        ttk.Label(model_frame, text="Negative Prompt:").pack(fill='x', padx=5, pady=(5,0))
        neg_prompt_editor = scrolledtext.ScrolledText(model_frame, height=3, font=("Consolas", 10))
        neg_prompt_editor.pack(fill="x", expand=True, padx=5, pady=(0, 5))
        neg_prompt_editor.insert('1.0', config.get('negative_prompt', ''))
        property_vars['negative_prompt'] = neg_prompt_editor
        output_frame = ttk.LabelFrame(parent_frame, text="Output Settings")
        output_frame.pack(fill='x', padx=5, pady=5)
        dest_frame = ttk.Frame(output_frame)
        dest_frame.pack(fill='x', pady=5, padx=5)
        ttk.Label(dest_frame, text=self.loc.get('prop_output_folder_label', fallback="Output Folder:")).pack(anchor='w')
        entry_frame = ttk.Frame(dest_frame)
        entry_frame.pack(fill='x', expand=True, pady=(2,0))
        dest_var = StringVar(value=config.get('output_folder', ''))
        property_vars['output_folder'] = dest_var
        dest_entry = ttk.Entry(entry_frame, textvariable=dest_var)
        dest_entry.pack(side='left', fill='x', expand=True)
        def _browse_folder():
            folder_selected = filedialog.askdirectory(title="Select Output Folder")
            if folder_selected:
                dest_var.set(folder_selected)
        browse_button = ttk.Button(entry_frame, text=self.loc.get('prop_output_folder_browse', fallback="Browse..."), command=_browse_folder)
        browse_button.pack(side='left', padx=(5,0))
        ttk.Label(output_frame, text="Output Filename Prefix (Optional):").pack(fill='x', padx=5, pady=(5,0))
        property_vars['output_filename_prefix'] = StringVar(value=config.get('output_filename_prefix', ''))
        ttk.Entry(output_frame, textvariable=property_vars['output_filename_prefix']).pack(fill='x', padx=5, pady=(0, 10))
        params_frame = ttk.LabelFrame(parent_frame, text="Generation Parameters")
        params_frame.pack(fill='x', padx=5, pady=5)
        size_frame = ttk.Frame(params_frame)
        size_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(size_frame, text="Width:").pack(side='left')
        property_vars['width'] = IntVar(value=config.get('width', 1024))
        ttk.Entry(size_frame, textvariable=property_vars['width'], width=8).pack(side='left', padx=(5, 20))
        ttk.Label(size_frame, text="Height:").pack(side='left')
        property_vars['height'] = IntVar(value=config.get('height', 1024))
        ttk.Entry(size_frame, textvariable=property_vars['height'], width=8).pack(side='left', padx=5)
        advanced_frame = ttk.Frame(params_frame)
        advanced_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(advanced_frame, text="Guidance (CFG):").pack(side='left')
        property_vars['guidance_scale'] = DoubleVar(value=config.get('guidance_scale', 7.5))
        ttk.Entry(advanced_frame, textvariable=property_vars['guidance_scale'], width=8).pack(side='left', padx=(5, 20))
        ttk.Label(advanced_frame, text="Steps:").pack(side='left')
        property_vars['num_inference_steps'] = IntVar(value=config.get('num_inference_steps', 30))
        ttk.Entry(advanced_frame, textvariable=property_vars['num_inference_steps'], width=8).pack(side='left', padx=5)
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_dynamic_output_schema(self, config):
        return [{"name": "data.image_path", "type": "string", "description": "The full local path to the generated image file."}]
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Image generation is a heavy process.'}]


_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
