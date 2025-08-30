#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\fail_always_plugin\processor.py
# JUMLAH BARIS : 47
#######################################################################

from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from typing import Dict, Any
from flowork_kernel.ui_shell import shared_properties
import ttkbootstrap as ttk
class FailAlwaysPlugin(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    FailAlwaysPlugin adalah sebuah plugin sederhana yang dirancang khusus
    untuk selalu menghasilkan kegagalan (error) saat dieksekusi.
    """
    TIER = "free"
    def __init__(self, module_id: str, services: Dict[str, Any]):
        super().__init__(module_id, services)
        self.logger(f"Module 'Fail Always' ({self.module_id}) initialized successfully.", "INFO")
    def execute(self, payload: Dict[str, Any], config: Dict[str, Any], status_updater: Any, ui_callback: Any, mode: str = 'EXECUTE') -> Dict[str, Any]:
        self.logger(self.loc.get('fail_always_executing_message', fallback="Modul 'Selalu Gagal' sedang mencoba beraksi..."), "WARN")
        status_updater(self.loc.get('fail_always_status_failing', fallback="Memulai kegagalan..."), "WARN")
        raise Exception(self.loc.get('fail_always_error_message', fallback="Sengaja GAGAL! Ini adalah kesalahan yang disimulasikan."))
    def create_properties_ui(self, parent_frame: Any, get_current_config: Any, available_vars: Dict[str, Any]) -> dict:
        """
        Meskipun tidak ada properti khusus, kita tetap tampilkan UI standar.
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
        return [{'status': 'ALWAYS FAILS', 'reason': 'This module is designed to throw an exception.'}]
    def on_install(self):
        self.logger(self.loc.get('fail_always_install_message', fallback="Modul 'Fail Always' berhasil diinstal!"), "SUCCESS")
    def on_load(self):
        self.logger(self.loc.get('fail_always_load_message', fallback="Modul 'Fail Always' dimuat dan siap untuk gagal."), "INFO")
    def on_unload(self):
        self.logger(self.loc.get('fail_always_unload_message', fallback="Modul 'Fail Always' dinonaktifkan."), "INFO")
