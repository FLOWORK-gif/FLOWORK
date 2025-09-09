#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\plugins\flowork_core_ui\settings_tab.py
# JUMLAH BARIS : 138
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox
from .settings_components.general_settings_frame import GeneralSettingsFrame
from .settings_components.webhook_settings_frame import WebhookSettingsFrame
from .settings_components.notification_settings_frame import NotificationSettingsFrame
from .settings_components.license_management_frame import LicenseManagementFrame
from .settings_components.error_handler_frame import ErrorHandlerFrame
from .settings_components.variable_manager_frame import VariableManagerFrame
from .settings_components.ai_provider_settings_frame import AiProviderSettingsFrame
from .settings_components.recorder_settings_frame import RecorderSettingsFrame
import threading
from flowork_gui.views.custom_widgets.scrolled_frame import ScrolledFrame
from flowork_gui.exceptions import PermissionDeniedError # PENAMBAHAN: Importing exceptions from the new local GUI file.
from flowork_gui.api_client.client import ApiClient
class SettingsTab(ttk.Frame):
    """
    Acts as a container and coordinator for all the individual settings frames.
    [REFACTORED] Now fetches all settings from the API and orchestrates saving.
    """
    def __init__(self, parent_notebook, api_client, loc_service, **kwargs):
        super().__init__(parent_notebook, padding=15)
        self.loc = loc_service
        self.api_client = api_client
        class MockKernel:
            def __init__(self, api_client_instance, loc_instance):
                self.api_client = api_client_instance
                self.loc = loc_instance
                self.services = {'localization_manager': self.loc}
                self.write_to_log = lambda msg, lvl="INFO": print(f"[INFO] (from MockKernel in SettingsTab): {msg}")
            def get_service(self, service_name):
                if service_name not in self.services:
                    class MockService:
                        def __init__(self, api_client):
                            self.api_client = api_client
                    self.services[service_name] = MockService(self.api_client)
                return self.services.get(service_name)
        self.kernel = MockKernel(self.api_client, self.loc)
        self.all_settings_frames = []
        self._content_initialized = False
        ttk.Label(self, text="Loading Settings...").pack(expand=True) # English Hardcode
    def _initialize_content(self):
        if self._content_initialized:
            return
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
        self._load_all_settings_from_api()
        self._content_initialized = True
    def refresh_content(self):
        """Refreshes the content and state of all child setting frames."""
        self.kernel.write_to_log("SettingsTab: Refreshing content.", "DEBUG")
        for frame in self.all_settings_frames:
            if hasattr(frame, 'refresh_content'):
                frame.refresh_content()
        if hasattr(self, 'variable_manager_frame'):
            self.variable_manager_frame.load_variables_to_ui()
    def _build_ui(self):
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(fill='both', expand=True)
        left_scrolled_frame = ScrolledFrame(paned_window)
        paned_window.add(left_scrolled_frame, weight=1)
        right_frame = ttk.Frame(paned_window, padding=5)
        paned_window.add(right_frame, weight=1)
        self._build_left_panel(left_scrolled_frame.scrollable_frame)
        self._build_right_panel(right_frame)
    def _build_left_panel(self, parent_frame):
        self.general_frame = GeneralSettingsFrame(parent_frame, self.kernel)
        self.general_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.general_frame)
        self.ai_provider_frame = AiProviderSettingsFrame(parent_frame, self.kernel)
        self.ai_provider_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.ai_provider_frame)
        self.recorder_frame = RecorderSettingsFrame(parent_frame, self.kernel)
        self.recorder_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.recorder_frame)
        self.webhook_frame = WebhookSettingsFrame(parent_frame, self.kernel)
        self.webhook_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.webhook_frame)
        self.notification_frame = NotificationSettingsFrame(parent_frame, self.kernel)
        self.notification_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.notification_frame)
        self.license_frame = LicenseManagementFrame(parent_frame, self.kernel)
        self.all_settings_frames.append(self.license_frame)
        self.license_frame.pack(fill="x", pady=5, padx=5)
        self.error_handler_frame = ErrorHandlerFrame(parent_frame, self.kernel)
        self.error_handler_frame.pack(fill="x", pady=5, padx=5, expand=True, anchor="n")
        self.all_settings_frames.append(self.error_handler_frame)
        save_button = ttk.Button(parent_frame, text=self.loc.get("settings_save_button", fallback="Save All Settings"), command=self._save_all_settings, bootstyle="success")
        save_button.pack(pady=10, padx=5, side="bottom", anchor="e")
    def _build_right_panel(self, parent_frame):
        self.variable_manager_frame = VariableManagerFrame(parent_frame, self.kernel)
        self.variable_manager_frame.pack(fill="both", expand=True, pady=5, padx=5)
    def _load_all_settings_from_api(self):
        threading.Thread(target=self._load_settings_worker, daemon=True).start()
    def _load_settings_worker(self):
        success, settings_data = self.api_client.get_all_settings()
        self.after(0, self._populate_settings_ui, success, settings_data)
    def _populate_settings_ui(self, success, settings_data):
        if success:
            for frame in self.all_settings_frames:
                try:
                    if hasattr(frame, 'load_settings_data'):
                        frame.load_settings_data(settings_data)
                except PermissionDeniedError:
                    self.kernel.write_to_log(f"Hiding settings frame '{frame.__class__.__name__}' due to insufficient permissions.", "WARN")
                    frame.pack_forget()
                except Exception as e:
                    self.kernel.write_to_log(f"Error loading settings for frame '{frame.__class__.__name__}': {e}", "ERROR")
                    frame.pack_forget()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"Failed to load settings from API: {settings_data}")
    def _save_all_settings(self):
        all_new_settings = {}
        try:
            for frame in self.all_settings_frames:
                if frame.winfo_ismapped() and hasattr(frame, 'get_settings_data'):
                    all_new_settings.update(frame.get_settings_data())
            threading.Thread(target=self._save_settings_worker, args=(all_new_settings,), daemon=True).start()
        except ValueError as e:
            messagebox.showerror(self.loc.get("messagebox_error_title"), str(e))
        except Exception as e:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"{self.loc.get('settings_save_error_msg')}: {e}")
    def _save_settings_worker(self, settings_to_save):
        success, response = self.api_client.save_settings(settings_to_save)
        self.after(0, self._on_save_settings_complete, success, response)
    def _on_save_settings_complete(self, success, response):
        if success:
            messagebox.showinfo(self.loc.get("messagebox_success_title"), self.loc.get("settings_save_success_msg"))
            self._load_all_settings_from_api()
        else:
             messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
