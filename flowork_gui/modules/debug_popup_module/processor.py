#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\modules\debug_popup_module\processor.py
# JUMLAH BARIS : 30
#######################################################################

from api_contract import BaseModule # PENAMBAHAN OTOMATIS
import json
class DebugPopupModule(BaseModule):
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self._active_popups = {}
    def _show_popup_on_ui_thread(self, node_instance_id, title, data_string):
        if node_instance_id in self._active_popups and self._active_popups[node_instance_id].winfo_exists():
            self._active_popups[node_instance_id].destroy()
            self.logger("An existing debug popup for this node was found and automatically closed.", "INFO") # English Log
        pass # ADDED: Added pass to prevent syntax error after commenting out.
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
