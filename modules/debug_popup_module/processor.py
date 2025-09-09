#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\debug_popup_module\processor.py
# JUMLAH BARIS : 54
#######################################################################

from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
import json
import ttkbootstrap as ttk
from tkinter import scrolledtext
class DebugPopupModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "free" # ADDED BY SCANNER: Default tier
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self._active_popups = {}
    def _show_popup_on_ui_thread(self, node_instance_id, title, data_string):
        if node_instance_id in self._active_popups and self._active_popups[node_instance_id].winfo_exists():
            self._active_popups[node_instance_id].destroy()
            self.logger("An existing debug popup for this node was found and automatically closed.", "INFO") # English Log
        popup = ttk.Toplevel(title=title)
        popup.geometry("600x400")
        txt_area = scrolledtext.ScrolledText(popup, wrap="word", width=70, height=20)
        txt_area.pack(expand=True, fill="both", padx=10, pady=10)
        txt_area.insert("1.0", data_string)
        txt_area.config(state="disabled")
        self._active_popups[node_instance_id] = popup
        def _on_popup_close():
            self.logger("Debug popup was closed manually by the user.", "DEBUG") # English Log
            if node_instance_id in self._active_popups:
                del self._active_popups[node_instance_id]
            popup.destroy()
        popup.protocol("WM_DELETE_WINDOW", _on_popup_close)
        popup.transient()
        popup.grab_set()
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        node_instance_id = config.get('__internal_node_id', self.module_id)
        status_updater("Preparing popup...", "INFO") # English Log
        try:
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
        except Exception:
            payload_str = str(payload)
        popup_title = "Debug Output From Previous Node" # English Hardcode
        ui_callback(self._show_popup_on_ui_thread, node_instance_id, popup_title, payload_str)
        status_updater("Popup displayed", "SUCCESS") # English Log
        return payload
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        ttk.Label(parent_frame, text="This module has no properties to configure.").pack(pady=10)
        return {}
    def get_data_preview(self, config: dict):
        """
        Provides a sample of what this module might output for the Data Canvas.
        """
        return [{'status': 'preview_not_available', 'reason': 'Displays live payload data during execution.'}]
