#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\debug_popup_module\processor.py
# JUMLAH BARIS : 48
#######################################################################

from flowork_kernel.api_contract import BaseModule
import json
import ttkbootstrap as ttk
from tkinter import scrolledtext
class DebugPopupModule(BaseModule):
    TIER = "free"
    _active_popup = None
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
    def _show_popup_on_ui_thread(self, module_instance, title, data_string):
        """
        (MODIFIED) This function now manages the lifecycle of the popup window.
        """
        if module_instance._active_popup and module_instance._active_popup.winfo_exists():
            module_instance._active_popup.destroy() # Close the old one.
            module_instance.logger("An existing debug popup was found and automatically closed.", "INFO")
        popup = ttk.Toplevel(title=title)
        popup.geometry("600x400")
        txt_area = scrolledtext.ScrolledText(popup, wrap="word", width=70, height=20)
        txt_area.pack(expand=True, fill="both", padx=10, pady=10)
        txt_area.insert("1.0", data_string)
        txt_area.config(state="disabled")
        module_instance._active_popup = popup
        def _on_popup_close():
            module_instance.logger("Debug popup was closed manually by the user.", "DEBUG")
            module_instance._active_popup = None # Forget the popup.
            popup.destroy()
        popup.protocol("WM_DELETE_WINDOW", _on_popup_close)
        popup.transient()
        popup.grab_set()
        popup.wait_window()
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        status_updater("Preparing popup...", "INFO")
        try:
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
        except Exception:
            payload_str = str(payload)
        popup_title = "Debug Output From Previous Node"
        ui_callback(self._show_popup_on_ui_thread, self, popup_title, payload_str)
        status_updater("Popup displayed", "SUCCESS")
        return payload
