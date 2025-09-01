#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\startup_service\startup_service.py
# (Full code for the modified file)
#######################################################################

from ..base_service import BaseService
import time
from tkinter import messagebox
from flowork_kernel.exceptions import MandatoryUpdateRequiredError, PermissionDeniedError
from flowork_kernel.api_client import ApiClient

class StartupService(BaseService):
    """
    A dedicated service to handle the application's startup sequence.
    (MODIFIED) Now correctly starts the AutoCompilerService during the sequence.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.api_client = ApiClient(kernel=self.kernel)

    def run_startup_sequence(self):
        """
        Executes the main startup logic with robust error handling.
        """
        try:
            self.logger("StartupService (Phase 1): Running automatic file update check...", "INFO")
            update_service = self.kernel.get_service("update_service", is_system_call=True)
            if update_service:
                update_service.run_update_check()

            self.logger("StartupService (Phase 2): Running Benteng Baja file integrity check...", "INFO")
            integrity_checker = self.kernel.get_service("integrity_checker_service", is_system_call=True)
            if integrity_checker: integrity_checker.verify_core_files()

            self._attempt_auto_login()

            self.logger("StartupService (Phase 3): Remote License Verification...", "INFO")
            license_manager = self.kernel.get_service("license_manager_service", is_system_call=True)
            if license_manager: license_manager.verify_license_on_startup()

            permission_manager = self.kernel.get_service("permission_manager_service", is_system_call=True)
            if permission_manager and license_manager:
                self.logger("StartupService: Injecting remote rules into PermissionManager...", "INFO")
                permission_manager.load_rules_from_source(license_manager.remote_permission_rules)

            self.logger("StartupService (Phase 4): All checks passed. Starting normal services...", "INFO")

            # (MODIFIED) The list of services to start now includes our new auto-compiler.
            # The order is important: component managers must run before the compiler.
            services_to_start = [
                ("documentation_service", lambda s: s.start() if hasattr(s, 'start') else None),
                ("module_manager_service", lambda s: s.discover_and_load_modules()),
                ("widget_manager_service", lambda s: s.discover_and_load_widgets()),
                ("trigger_manager_service", lambda s: s.discover_and_load_triggers()),
                ("localization_manager", lambda s: s.load_all_languages()),
                # (ADDED) The AutoCompiler runs here, after all components are known but before they are heavily used.
                ("auto_compiler_service", lambda s: s.initial_scan() if hasattr(s, 'initial_scan') else None),
                # (ADDED) AI Provider Manager is now started here, after the compiler has run.
                ("ai_provider_manager_service", lambda s: s.start() if hasattr(s, 'start') else None),
                ("tab_manager_service", lambda s: s.start() if hasattr(s, 'start') else None),
                ("scheduler_manager_service", lambda s: s.start() if hasattr(s, 'start') else None),
                ("trigger_manager_service", lambda s: s.start() if hasattr(s, 'start') else None),
                ("api_server_service", lambda s: s.start() if hasattr(s, 'start') else None)
            ]

            for service_id, start_action in services_to_start:
                try:
                    # (COMMENT) We get the service instance. The 'is_system_call' flag is important
                    # for critical services like this during startup.
                    service_instance = self.kernel.get_service(service_id, is_system_call=True)
                    if service_instance:
                        start_action(service_instance)
                except PermissionDeniedError as e:
                    self.logger(f"StartupService: Skipped loading/starting '{service_id}' due to license restrictions.", "WARN")
                except Exception as e:
                    self.logger(f"StartupService: An error occurred with service '{service_id}': {e}", "ERROR")

            time.sleep(1)
            event_bus = self.kernel.get_service("event_bus", is_system_call=True)
            if event_bus:
                event_bus.publish("event_all_services_started", {})

            self.kernel.startup_complete = True
            self.logger("StartupService: All services started successfully.", "SUCCESS")
            return {"status": "complete"}

        except MandatoryUpdateRequiredError:
            raise
        except Exception as e:
            self.logger(f"A critical, unrecoverable error occurred during startup: {e}", "CRITICAL")
            raise e

    def _attempt_auto_login(self):
        # ... (kode di sini tidak berubah, jadi aku singkat)
        self.logger("StartupService: Checking for saved user session...", "INFO") # English Log
        state_manager = self.kernel.get_service("state_manager", is_system_call=True)
        if not state_manager:
            self.logger("StartupService: StateManager not available for auto-login.", "WARN") # English Log
            return
        saved_token = state_manager.get("user_session_token")
        if not saved_token:
            self.logger("StartupService: No saved session token found.", "INFO") # English Log
            return
        self.logger("StartupService: Found session token, attempting to validate with server...", "INFO") # English Log
        success, user_data = self.api_client.get_user_profile_by_token(saved_token)
        if success:
            self.logger(f"Auto-login successful for user: {user_data.get('email')}", "SUCCESS") # English Log
            self.kernel.current_user = user_data
            user_tier = user_data.get('tier', 'free')
            self.kernel.license_tier = user_tier
            self.kernel.is_premium = self.kernel.TIER_HIERARCHY.get(user_tier, 0) > 0
            event_bus = self.kernel.get_service("event_bus", is_system_call=True)
            if event_bus:
                event_bus.publish("USER_LOGGED_IN", user_data)
        else:
            self.logger(f"Auto-login failed: Token is invalid or expired. Reason: {user_data}", "WARN") # English Log
            state_manager.delete("user_session_token")