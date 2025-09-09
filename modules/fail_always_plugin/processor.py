#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\fail_always_plugin\processor.py
# JUMLAH BARIS : 57
#######################################################################

from flowork_kernel.core import build_security
from flowork_kernel.core import build_security
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from typing import Dict, Any
from flowork_kernel.ui_shell import shared_properties
import ttkbootstrap as ttk
class FailAlwaysPlugin(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    FailAlwaysPlugin is a simple plugin designed specifically
    to always produce a failure (error) when executed.
    """
    TIER = "free"
    def __init__(self, module_id: str, services: Dict[str, Any]):
        build_security.perform_runtime_check(__file__)
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
        self.logger(f"Module 'Fail Always' ({self.module_id}) initialized successfully.", "INFO")
    def execute(self, payload: Dict[str, Any], config: Dict[str, Any], status_updater: Any, ui_callback: Any, mode: str = 'EXECUTE') -> Dict[str, Any]:
        self.logger(self.loc.get('fail_always_executing_message', fallback="The 'Fail Always' module is attempting to act..."), "WARN")
        status_updater(self.loc.get('fail_always_status_failing', fallback="Initiating failure..."), "WARN")
        error_message = self.loc.get('fail_always_error_message', fallback="Intentionally FAILED! This is a simulated error.")
        if 'data' not in payload:
            payload['data'] = {}
        payload['data']['error'] = error_message
        return {"payload": payload, "output_name": "error"}
    def create_properties_ui(self, parent_frame: Any, get_current_config: Any, available_vars: Dict[str, Any]) -> dict:
        """
        Even though there are no special properties, we still display the standard UI.
        """
        property_vars = {}
        current_config = get_current_config()
        ttk.Label(parent_frame,
                  text=self.loc.get('fail_always_prop_info', fallback="This module has no special settings.\nIts only purpose is to always fail upon execution."),
                  wraplength=400, justify="center", bootstyle="info").pack(pady=10, padx=10)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, current_config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        """
        Provides a sample of what this module might output for the Data Canvas.
        """
        return [{'status': 'ALWAYS FAILS', 'reason': 'This module is designed to return an error payload.'}]
    def on_install(self):
        self.logger(self.loc.get('fail_always_install_message', fallback="The 'Fail Always' module has been successfully installed!"), "SUCCESS")
    def on_load(self):
        self.logger(self.loc.get('fail_always_load_message', fallback="The 'Fail Always' module is loaded and ready to fail."), "INFO")
    def on_unload(self):
        self.logger(self.loc.get('fail_always_unload_message', fallback="The 'Fail Always' module has been unloaded."), "INFO")
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
_UNUSED_SIGNATURE = 'AOLA_FLOWORK_OFFICIAL_BUILD_2025_TEETAH_ART' # Embedded Signature
