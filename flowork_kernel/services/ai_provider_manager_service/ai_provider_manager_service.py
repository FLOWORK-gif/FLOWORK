#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\ai_provider_manager_service\ai_provider_manager_service.py
# JUMLAH BARIS : 345
#######################################################################

import os
import json
import importlib.util
import subprocess
import sys
import importlib.metadata
import tempfile
import zipfile
import shutil
import traceback
import time
import hashlib # (ADDED) For hash checking
from ..base_service import BaseService
from flowork_kernel.utils.file_helper import sanitize_filename
try:
    import torch
    from diffusers import StableDiffusionXLPipeline, AutoencoderKL
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
try:
    importlib.metadata.version('llama-cpp-python')
    LLAMA_CPP_AVAILABLE = True
except importlib.metadata.PackageNotFoundError:
    LLAMA_CPP_AVAILABLE = False
class AIProviderManagerService(BaseService):
    """
    (REMASTERED V5) Can now differentiate between local GGUF models and local HF/Diffusers models.
    It intelligently routes execution to the appropriate worker or internal handler.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.providers_path = os.path.join(self.kernel.project_root_path, "ai_providers")
        os.makedirs(self.providers_path, exist_ok=True)
        self.loaded_providers = {}
        self.local_models = {}
        self.hf_pipelines = {}
        self.image_output_dir = os.path.join(self.kernel.data_path, "generated_images_by_service")
        os.makedirs(self.image_output_dir, exist_ok=True)
        self.discover_and_load_endpoints()
    def query_ai_by_task(self, task_type: str, prompt: str, endpoint_id: str = None, **kwargs) -> dict:
        if endpoint_id:
            target_endpoint_id = endpoint_id
            self.kernel.write_to_log(f"AI Query by Task: Using specified endpoint '{target_endpoint_id}' for task '{task_type}'", "DEBUG") # English Log
        else:
            setting_key = f"ai_model_for_{task_type}"
            target_endpoint_id = self.loc.get_setting(setting_key) or self.loc.get_setting("ai_model_for_other")
            self.kernel.write_to_log(f"AI Query by Task: Using default endpoint '{target_endpoint_id}' for task '{task_type}'", "DEBUG") # English Log
        if not target_endpoint_id:
            return {"error": f"No default or specified AI model is configured for task type '{task_type}'."}
        if target_endpoint_id in self.loaded_providers:
            provider = self.get_provider(target_endpoint_id)
            if provider:
                is_ready, msg = provider.is_ready()
                if is_ready:
                    return provider.generate_response(prompt, **kwargs)
                else:
                    return {"error": f"Provider '{target_endpoint_id}' for task '{task_type}' is not ready: {msg}"}
            else:
                 return {"error": f"Provider '{target_endpoint_id}' not found although it is in loaded_providers list."}
        elif target_endpoint_id.startswith("(Local Model)"):
            model_info = self.local_models.get(target_endpoint_id)
            if not model_info:
                return {"error": f"Local model '{target_endpoint_id}' not found in the manager's index."}
            model_type = model_info.get('type')
            if model_type == 'gguf':
                if not LLAMA_CPP_AVAILABLE:
                    return {"error": "Library 'llama-cpp-python' is required to use local GGUF models."}
                model_full_path = model_info.get('full_path')
                if not model_full_path or not os.path.exists(model_full_path):
                    return {"error": f"Local model file not found at path: {model_full_path}"}
                try:
                    worker_path = os.path.join(self.kernel.project_root_path, "flowork_kernel", "workers", "ai_worker.py")
                    gpu_layers_setting = self.loc.get_setting("ai_gpu_layers", 40)
                    command = [sys.executable, worker_path, model_full_path, str(gpu_layers_setting)]
                    self.kernel.write_to_log(f"Delegating GGUF task to isolated AI worker for model '{os.path.basename(model_full_path)}'...", "INFO") # English Log
                    timeout_seconds = self.loc.get_setting("ai_worker_timeout_seconds", 300)
                    process = subprocess.run(command, input=prompt, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout_seconds)
                    if process.returncode == 0:
                        return {"type": "text", "data": process.stdout}
                    else:
                        return {"type": "text", "data": f"ERROR: AI Worker process failed: {process.stderr}"}
                except Exception as e:
                    self.kernel.write_to_log(f"Error calling local GGUF worker: {e}", "CRITICAL") # English Log
                    return {"error": str(e)}
            elif model_type == 'hf_image_single_file':
                return self._run_single_file_image_model(model_info, prompt, **kwargs)
            else:
                return {"error": f"Unsupported local model type '{model_type}' for endpoint '{target_endpoint_id}'."}
        else:
            return {"error": f"Unsupported or unknown AI endpoint type for task '{task_type}': {target_endpoint_id}"}
    def _run_single_file_image_model(self, model_info, prompt, **kwargs):
        if not DIFFUSERS_AVAILABLE:
            return {"error": "Libraries 'diffusers', 'torch', 'Pillow' are required."}
        model_folder_name = model_info.get('name')
        try:
            pipeline = self.hf_pipelines.get(model_folder_name)
            if not pipeline:
                self.kernel.write_to_log(f"Loading HF pipeline for '{model_folder_name}' for the first time...", "INFO")
                model_path = model_info.get('full_path')
                device = "cuda" if torch.cuda.is_available() else "cpu"
                torch_dtype = torch.float16 if device == "cuda" else torch.float32
                vae_path = os.path.join(self.kernel.project_root_path, "ai_models", "vae", "sdxl-vae-fp16-fix")
                if not os.path.isdir(vae_path):
                     raise FileNotFoundError("VAE folder 'sdxl-vae-fp16-fix' not found in 'ai_models/vae'. This is crucial for quality.")
                vae = AutoencoderKL.from_pretrained(vae_path, torch_dtype=torch_dtype).to(device)
                safetensor_files = [f for f in os.listdir(model_path) if f.endswith(".safetensors")]
                if not safetensor_files:
                    raise FileNotFoundError(f"No .safetensors file found in '{model_path}'")
                full_model_path = os.path.join(model_path, safetensor_files[0])
                pipeline = StableDiffusionXLPipeline.from_single_file(
                    full_model_path,
                    vae=vae,
                    torch_dtype=torch_dtype,
                    variant="fp16" if device == "cuda" else "fp32"
                ).to(device)
                if device == "cuda":
                    pipeline.enable_model_cpu_offload()
                self.hf_pipelines[model_folder_name] = pipeline
            self.kernel.write_to_log(f"Generating image with '{model_folder_name}'...", "INFO")
            generation_params = {
                "prompt": prompt,
                "negative_prompt": kwargs.get('negative_prompt', 'blurry, worst quality, low quality'),
                "width": int(kwargs.get('width', 1024)),
                "height": int(kwargs.get('height', 1024)),
                "guidance_scale": float(kwargs.get('guidance_scale', 7.5)),
                "num_inference_steps": int(kwargs.get('num_inference_steps', 30))
            }
            image = pipeline(**generation_params).images[0]
            sanitized_prefix = sanitize_filename(prompt[:25])
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{sanitized_prefix}_{timestamp}.png"
            output_path = os.path.join(self.image_output_dir, filename)
            image.save(output_path)
            self.kernel.write_to_log(f"Image saved to: {output_path}", "SUCCESS")
            return {"type": "image", "data": output_path}
        except Exception as e:
            self.kernel.write_to_log(f"Error during local image generation: {e}\n{traceback.format_exc()}", "CRITICAL")
            return {"error": str(e)}
    def _calculate_requirements_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except IOError:
            return None
    def _install_dependencies(self, provider_dir, provider_name):
        requirements_path = os.path.join(provider_dir, 'requirements.txt')
        if not os.path.exists(requirements_path):
            return True # Success, nothing to install
        vendor_path = os.path.join(provider_dir, 'vendor')
        hash_file_path = os.path.join(provider_dir, '.vendor_hash')
        current_hash = self._calculate_requirements_hash(requirements_path)
        if os.path.isdir(vendor_path) and os.path.exists(hash_file_path):
            try:
                with open(hash_file_path, 'r') as f:
                    saved_hash = f.read().strip()
                if saved_hash == current_hash:
                    return True
            except IOError:
                pass
        self.kernel.write_to_log(f"AIProvider '{provider_name}' has local dependencies. Installing into its 'vendor' folder...", "INFO") # English Log
        if os.path.isdir(vendor_path):
            shutil.rmtree(vendor_path, ignore_errors=True)
        try:
            python_exe = sys.executable
            command = [
                python_exe, "-m", "pip", "install", "--target", vendor_path,
                "-r", requirements_path, "--no-user", "--disable-pip-version-check"
            ]
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW
            subprocess.run(command, check=True, capture_output=True, creationflags=creation_flags)
            with open(hash_file_path, 'w') as f:
                f.write(current_hash)
            self.kernel.write_to_log(f"Successfully installed local dependencies for '{provider_name}'.", "SUCCESS") # English Log
            return True
        except subprocess.CalledProcessError as e:
            self.kernel.write_to_log(f"FAILED to install local dependencies for '{provider_name}'. Pip Error: {e.stderr.decode('utf-8', 'ignore')}", "CRITICAL") # English Log
            return False
        except Exception as e:
            self.kernel.write_to_log(f"An unexpected error occurred during local dependency installation for '{provider_name}': {e}", "CRITICAL") # English Log
            return False
    def discover_and_load_endpoints(self):
        self.kernel.write_to_log("--- STARTING AI ENDPOINT DISCOVERY (V5 - Type Aware) ---", "WARN") # English Log
        self.loaded_providers.clear()
        self.local_models.clear()
        self.hf_pipelines.clear()
        self.kernel.write_to_log(f"Scanning for AI Providers in: {self.providers_path}", "DEBUG") # English Log
        if self.providers_path not in sys.path:
            sys.path.insert(0, self.providers_path)
        for root, dirs, files in os.walk(self.providers_path):
            if 'manifest.json' in files:
                provider_dir = root
                provider_id = os.path.basename(provider_dir)
                category_name = os.path.basename(os.path.dirname(provider_dir))
                if provider_dir == self.providers_path or "__pycache__" in provider_dir:
                    continue
                try:
                    manifest_path = os.path.join(provider_dir, "manifest.json")
                    with open(manifest_path, 'r', encoding='utf-8') as f: manifest = json.load(f)
                    provider_name = manifest.get('name', provider_id)
                    entry_point = manifest.get('entry_point')
                    if not entry_point or '.' not in entry_point: continue
                    self.kernel.write_to_log(f"AIProviderManager: Checking dependencies for '{provider_name}'...", "DEBUG")
                    if not self._install_dependencies(provider_dir, provider_name): continue
                    vendor_path = os.path.join(provider_dir, 'vendor')
                    is_path_added = False
                    if os.path.isdir(vendor_path):
                        sys.path.insert(0, vendor_path)
                        is_path_added = True
                    try:
                        module_filename, class_name = entry_point.split('.')
                        module_path = os.path.join(provider_dir, f"{module_filename}.py")
                        if not os.path.exists(module_path): continue
                        full_module_name = f"ai_providers.{category_name}.{provider_id}.{module_filename}"
                        spec = importlib.util.spec_from_file_location(full_module_name, module_path)
                        module_lib = importlib.util.module_from_spec(spec)
                        sys.modules[full_module_name] = module_lib
                        spec.loader.exec_module(module_lib)
                        ProviderClass = getattr(module_lib, class_name)
                        self.loaded_providers[provider_id] = ProviderClass(self.kernel, manifest)
                        self.kernel.write_to_log(f"  -> AI Provider '{provider_name}' loaded.", "SUCCESS") # English Log
                    finally:
                        if is_path_added:
                            try:
                                sys.path.remove(vendor_path)
                            except ValueError:
                                pass
                except Exception as e:
                    self.kernel.write_to_log(f"  -> CRITICAL FAILURE loading provider '{provider_id}'. Error: {e}", "ERROR") # English Log
        ai_models_base_path = os.path.join(self.kernel.project_root_path, "ai_models")
        self.kernel.write_to_log(f"Scanning for Local AI Models in: {ai_models_base_path}", "DEBUG") # English Log
        if os.path.isdir(ai_models_base_path):
            for category in os.listdir(ai_models_base_path):
                category_path = os.path.join(ai_models_base_path, category)
                if not os.path.isdir(category_path): continue
                self.kernel.write_to_log(f"  -> Scanning category: '{category}'", "DETAIL") # English Log
                for item_name in os.listdir(category_path):
                    item_path = os.path.join(category_path, item_name)
                    model_id = f"(Local Model) {item_name}"
                    if os.path.isdir(item_path):
                        files_in_dir = os.listdir(item_path)
                        gguf_files = [f for f in files_in_dir if f.lower().endswith(".gguf")]
                        safetensor_files = [f for f in files_in_dir if f.lower().endswith(".safetensors")]
                        if gguf_files:
                            self.local_models[model_id] = {"full_path": os.path.join(item_path, gguf_files[0]), "type": 'gguf', "name": item_name}
                            self.kernel.write_to_log(f"    -> Found Local GGUF Model (in Folder): '{item_name}'", "SUCCESS") # English Log
                        elif safetensor_files and category == 'image':
                            self.local_models[model_id] = {"full_path": item_path, "type": 'hf_image_single_file', "name": item_name}
                            self.kernel.write_to_log(f"    -> Found Local Single-File Image Model (Folder): '{item_name}'", "SUCCESS") # English Log
                        else:
                            self.kernel.write_to_log(f"    -> Found generic local model folder (unsupported type): '{item_name}'", "WARN") # English Log
                    elif item_name.lower().endswith(".gguf"):
                        self.local_models[model_id] = {"full_path": item_path, "type": 'gguf', "name": item_name}
                        self.kernel.write_to_log(f"    -> Found Local GGUF Model (File): '{item_name}'", "SUCCESS") # English Log
        self.kernel.write_to_log(f"--- AI ENDPOINT DISCOVERY FINISHED ---", "WARN") # English Log
        self.kernel.write_to_log(f"Total endpoints available: {len(self.loaded_providers) + len(self.local_models)}", "SUCCESS") # English Log
    def get_provider(self, provider_id: str):
        return self.loaded_providers.get(provider_id)
    def get_available_providers(self) -> dict:
        provider_names = {}
        for provider_id, provider_instance in self.loaded_providers.items():
            provider_names[provider_id] = provider_instance.get_provider_name()
        for model_id, model_data in self.local_models.items():
            display_name = f"{model_data.get('name')} ({model_data.get('type', 'local').upper()})"
            provider_names[model_id] = display_name
        return provider_names
    def get_default_provider(self):
        loc = self.kernel.get_service("localization_manager")
        if loc:
            saved_provider_id = loc.get_setting("ai_center_master_provider")
            if saved_provider_id and saved_provider_id in self.loaded_providers:
                return self.loaded_providers[saved_provider_id]
        if self.loaded_providers:
            first_provider_key = next(iter(self.loaded_providers))
            first_provider = self.loaded_providers[first_provider_key]
            self.kernel.write_to_log(f"AI Manager: No master provider set. Falling back to first available: {first_provider.get_provider_name()}", "WARN") # English Log
            return first_provider
        return None
    def install_component(self, zip_filepath: str) -> (bool, str):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                component_root_path = None
                if os.path.exists(os.path.join(temp_dir, 'manifest.json')):
                    component_root_path = temp_dir
                else:
                    dir_items = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                    if len(dir_items) == 1:
                        potential_path = os.path.join(temp_dir, dir_items[0])
                        if os.path.exists(os.path.join(potential_path, 'manifest.json')):
                            component_root_path = potential_path
                if not component_root_path:
                    return False, "manifest.json not found in the root of the zip archive or in a single subdirectory."
                with open(os.path.join(component_root_path, 'manifest.json'), 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                required_tier = manifest.get('tier', 'free')
                if not self.kernel.is_tier_sufficient(required_tier):
                    error_msg = f"Installation failed. This AI Provider requires a '{required_tier.capitalize()}' license."
                    return False, error_msg
                component_id = manifest.get('id')
                if not component_id:
                    return False, "Component 'id' is missing from manifest.json."
                component_category = manifest.get('category', 'specialized')
                self.kernel.write_to_log(f"Installing '{component_id}' to category '{component_category}' based on manifest.", "INFO") # English Log
                category_path = os.path.join(self.providers_path, component_category)
                os.makedirs(category_path, exist_ok=True)
                final_path = os.path.join(category_path, component_id)
                if os.path.exists(final_path):
                    return False, f"AI Provider '{component_id}' is already installed."
                shutil.move(component_root_path, final_path)
                return True, f"AI Provider '{manifest.get('name', component_id)}' installed successfully."
            except Exception as e:
                return False, f"An error occurred during AI Provider installation: {e}"
    def _find_component_path(self, component_id: str) -> str | None:
        for category_name in os.listdir(self.providers_path):
            category_path = os.path.join(self.providers_path, category_name)
            if os.path.isdir(category_path):
                potential_path = os.path.join(category_path, component_id)
                if os.path.isdir(potential_path):
                    return potential_path
        return None
    def uninstall_component(self, component_id: str) -> (bool, str):
        component_path = self._find_component_path(component_id)
        if not component_path:
            return False, f"Path for AI Provider '{component_id}' not found in any category."
        try:
            shutil.rmtree(component_path)
            if component_id in self.loaded_providers:
                del self.loaded_providers[component_id]
            return True, f"AI Provider '{component_id}' uninstalled successfully."
        except Exception as e:
            return False, f"Could not delete AI Provider folder: {e}"
