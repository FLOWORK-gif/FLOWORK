#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\manual_approval_module\processor.py
# JUMLAH BARIS : 55
#######################################################################

from flowork_kernel.api_contract import BaseModule
import threading
import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.ui_shell.shared_properties import create_debug_and_reliability_ui, create_loop_settings_ui
class ManualApprovalModule(BaseModule):
    TIER = "free"  # ADDED BY SCANNER: Default tier
    """
    Modul untuk menampilkan popup persetujuan dan menjeda alur kerja
    sampai pengguna memberikan respons.
    """
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.approval_event = threading.Event()
        self.result = None
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        self.approval_event.clear()
        self.result = None
        message = config.get('approval_message', "Butuh persetujuan Anda.")
        status_updater(f"Menunggu persetujuan pengguna: '{message[:30]}...'", "WARN")
        self.kernel.display_approval_popup(self.module_id, message, self.on_approval_response)
        self.approval_event.wait()
        status_updater(f"Respons diterima: {self.result}", "INFO")
        self.logger(f"Respons popup diterima: {self.result}", "INFO")
        return {"payload": payload, "output_name": self.result}
    def on_approval_response(self, result: str):
        """Callback yang dipanggil oleh Kernel setelah pengguna mengklik tombol di popup."""
        self.result = result
        self.approval_event.set()
    def get_result(self):
        """Metode ini bisa dipanggil oleh executor jika diperlukan."""
        return self.result
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        """
        Membuat UI untuk mengatur pesan persetujuan dan pengaturan standar.
        """
        property_vars = {}
        current_config = get_current_config()
        ttk.Label(parent_frame, text=self.loc.get('prop_approval_message_label', fallback="Pesan Persetujuan:")).pack(fill='x', padx=5, pady=(10,0))
        message_var = StringVar(value=current_config.get('approval_message', ''))
        property_vars['approval_message'] = message_var
        ttk.Entry(parent_frame, textvariable=message_var).pack(fill='x', padx=5, pady=(0, 5))
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = create_debug_and_reliability_ui(parent_frame, current_config, self.loc)
        property_vars.update(debug_vars)
        loop_vars = create_loop_settings_ui(parent_frame, current_config, self.loc, available_vars)
        property_vars.update(loop_vars)
        return property_vars
