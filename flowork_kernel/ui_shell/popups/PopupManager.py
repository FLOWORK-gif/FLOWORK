#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\popups\PopupManager.py
# JUMLAH BARIS : 46
#######################################################################

from .approval_popup import ApprovalPopup
from .license_popup import LicensePopup
from .NotificationManager import NotificationManager
class PopupManager:
    """
    Acts as a centralized command center for all popups in the application.
    This includes manual approvals, license prompts, and notification toasts.
    """
    def __init__(self, main_window, kernel):
        self.main_window = main_window
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.notification_manager = NotificationManager(self.main_window, self.kernel)
        self._current_approval_popup = None
        self._current_approval_module_id = None
        self.current_license_popup = None
    def show_notification(self, title: str, message: str, level: str = "INFO"):
        """Displays a notification toast."""
        self.notification_manager.show_toast(title, message, level)
        self.kernel.write_to_log(f"POPUP NOTIFICATION: {title} - {message}", level)
    def show_approval(self, module_id, workflow_name, message):
        """Displays a manual approval dialog."""
        if self._current_approval_popup and self._current_approval_popup.winfo_exists():
            self.kernel.write_to_log(f"Popup request for '{module_id}' ignored, another popup is active.", "WARN")
            return
        self._current_approval_module_id = module_id
        self._current_approval_popup = ApprovalPopup(self, self.kernel, module_id, workflow_name, message)
    def handle_approval_response(self, result: str):
        """Handles the user's response from the approval dialog."""
        if self._current_approval_module_id:
            module_manager = self.kernel.get_service("module_manager_service")
            if module_manager:
                module_manager.notify_approval_response(self._current_approval_module_id, result)
        if self._current_approval_popup and self._current_approval_popup.winfo_exists():
            self._current_approval_popup.destroy()
        self._current_approval_popup, self._current_approval_module_id = None, None
    def show_license_prompt(self):
        """Displays the license activation dialog."""
        self.main_window.prompt_for_license_file()
