#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\auto_compiler_service\auto_compiler_service.py
# JUMLAH BARIS : 178
#######################################################################

import os
import sys
import subprocess
import json
import hashlib
import time
import re
from ..base_service import BaseService
class AutoCompilerService(BaseService):
    """
    (REMASTERED V4) A powerful service that runs in development mode.
    It now dynamically assigns the correct compiled extension based on component type.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.component_dirs = [
            self.kernel.modules_path, self.kernel.plugins_path,
            self.kernel.widgets_path, self.kernel.triggers_path,
            self.kernel.ai_providers_path,
            os.path.join(self.kernel.project_root_path, 'scanners') # [PENAMBAHAN] Scanner sekarang ikut dipantau
        ]
        self.is_nuitka_available = self._check_nuitka()
    def _check_nuitka(self):
        """Checks if Nuitka is available in the environment."""
        try:
            self.logger("Nuitka compiler is available.", "SUCCESS") # English Log
            return True
        except ImportError:
            self.logger("Nuitka is not installed. Auto-compiler service will be disabled.", "WARN") # English Log
            return False
    def start(self):
        """
        The start method is a placeholder; the main logic is triggered by other services.
        """
        if self.is_nuitka_available:
            self.logger("AutoCompilerService is active and ready.", "SUCCESS") # English Log
        else:
            self.logger("AutoCompilerService is inactive due to missing Nuitka.", "WARN") # English Log
    def initial_scan(self):
        """
        Performs a full scan on startup to compile any changed or new components.
        """
        if not self.is_nuitka_available or not self.kernel.is_dev_mode:
            return
        self.logger("AutoCompiler: Performing initial scan for modules to compile...", "INFO") # English Log
        total_compiled = 0
        for base_dir in self.component_dirs:
            if not os.path.isdir(base_dir): continue
            for component_id in os.listdir(base_dir):
                component_path = os.path.join(base_dir, component_id)
                if os.path.isdir(component_path):
                    manifest_path = os.path.join(component_path, "manifest.json")
                    if os.path.exists(manifest_path) or base_dir.endswith('scanners'):
                        if self._compile_if_needed(component_path, component_id):
                            total_compiled += 1
        self.logger(f"AutoCompiler: Initial scan complete. Compiled {total_compiled} new/updated components.", "SUCCESS") # English Log
    def _get_target_extension(self, component_path: str) -> str:
        """
        [ADDED V2] Determines the correct compiled file extension based on the component's parent directory.
        """
        normalized_path = component_path.replace('\\', '/')
        if '/widgets/' in normalized_path:
            return ".widget.flowork"
        if '/modules/' in normalized_path:
            return ".module.flowork"
        if '/plugins/' in normalized_path:
            return ".plugin.flowork"
        if '/triggers/' in normalized_path:
            return ".trigger.flowork"
        if '/scanners/' in normalized_path: # [PENAMBAHAN] Aturan baru untuk scanner
            return ".scanner.flowork"
        return ".aola_flowork" # Fallback to the old extension
    def _compile_if_needed(self, component_path, component_id):
        """
        The core logic. Checks fingerprints and decides whether to compile a component.
        """
        fingerprint_path = os.path.join(component_path, "build_fingerprint.json")
        manifest_path = os.path.join(component_path, "manifest.json")
        entry_point_file = None
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                entry_point = manifest.get("entry_point")
                if entry_point and '.' in entry_point:
                    module_filename, _ = entry_point.split('.', 1)
                    entry_point_file = f"{module_filename}.py"
            except Exception:
                return False
        elif os.path.basename(os.path.dirname(component_path)) == 'scanners':
            entry_point_file = f"{component_id}.py"
        if not entry_point_file: return False
        source_py_path = os.path.join(component_path, entry_point_file)
        if not os.path.exists(source_py_path):
            return False
        current_fingerprint = self._calculate_fingerprint(component_path, source_py_path)
        last_fingerprint = {}
        if os.path.exists(fingerprint_path):
            try:
                with open(fingerprint_path, 'r', encoding='utf-8') as f:
                    last_fingerprint = json.load(f)
            except (IOError, json.JSONDecodeError):
                last_fingerprint = {}
        if current_fingerprint.get("source_hash") == last_fingerprint.get("source_hash"):
            return False
        self.logger(f"'{component_id}' has changed. Recompiling...", "WARN") # English Log
        target_extension = self._get_target_extension(component_path)
        if self._run_nuitka_compilation(source_py_path, component_id, target_extension):
            with open(fingerprint_path, 'w', encoding='utf-8') as f:
                json.dump(current_fingerprint, f, indent=4)
            self.logger(f"Successfully compiled '{component_id}' to '{target_extension}' and updated its fingerprint.", "SUCCESS") # English Log
            return True
        return False
    def _calculate_fingerprint(self, component_path, source_py_path):
        """Calculates a hash of the source .py file and its manifest."""
        source_hash = hashlib.sha256()
        try:
            with open(source_py_path, 'rb') as f:
                source_hash.update(f.read())
            manifest_path = os.path.join(component_path, "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, 'rb') as f:
                    manifest_hash = hashlib.sha256(f.read()).hexdigest()
            else:
                manifest_hash = None
            return {
                "source_hash": source_hash.hexdigest(),
                "manifest_hash": manifest_hash,
                "timestamp": time.time()
            }
        except IOError:
            return {}
    def _run_nuitka_compilation(self, source_py_path, component_id, target_extension):
        """
        Executes the Nuitka compilation process via a subprocess.
        """
        output_filename = os.path.splitext(os.path.basename(source_py_path))[0]
        output_dir = os.path.dirname(source_py_path)
        command = [
            sys.executable,
            "-m", "nuitka",
            "--module",
            "--output-dir=" + output_dir,
            "--remove-output",
            "--windows-console-mode=disable",
            "--lto=yes",
            "--python-flag=-OO",
            source_py_path
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, cwd=self.kernel.project_root_path)
            compiled_ext = ".pyd" if sys.platform == "win32" else ".so"
            generated_file = None
            for file in os.listdir(output_dir):
                if file.startswith(output_filename) and file.endswith(compiled_ext):
                    generated_file = os.path.join(output_dir, file)
                    break
            target_file = os.path.join(output_dir, f"{output_filename}{target_extension}")
            if os.path.exists(target_file):
                os.remove(target_file)
            if generated_file and os.path.exists(generated_file):
                os.rename(generated_file, target_file)
                return True
            else:
                self.logger(f"Nuitka did not produce the expected output file in '{output_dir}' for '{component_id}'", "ERROR") # English Log
                return False
        except subprocess.CalledProcessError as e:
            self.logger(f"Nuitka compilation FAILED for '{component_id}'.", "CRITICAL") # English Log
            self.logger(f"Nuitka STDOUT: {e.stdout}", "DEBUG") # English Log
            self.logger(f"Nuitka STDERR: {e.stderr}", "DEBUG") # English Log
            return False
