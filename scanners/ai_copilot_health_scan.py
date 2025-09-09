#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\scanners\ai_copilot_health_scan.py
# JUMLAH BARIS : 58
#######################################################################

import os
from .base_scanner import BaseScanner
class AICopilotHealthScan(BaseScanner):
    """
    Ensures the entire AI Co-pilot pipeline is correctly wired.
    [UPGRADE] Now provides a file preview on failure for easier debugging.
    [FIXED] Corrected the check string for the on_load hook.
    [FIXED V2] The check for TabManager now correctly verifies that it SETS the preset name in StateManager.
    [FIXED V3] The markdown check is now more flexible to variable name changes.
    """
    def run_scan(self) -> str:
        self.report("\n[SCAN] === Starting AI Co-pilot Health & Integrity Scan ===", "SCAN")
        workflow_executor_path = os.path.join(self.kernel.project_root_path, "flowork_kernel", "services", "workflow_executor_service", "workflow_executor_service.py")
        metrics_logger_path = os.path.join(self.kernel.project_root_path, "plugins", "metrics_logger_plugin", "metrics_logger.py")
        module_manager_path = os.path.join(self.kernel.project_root_path, "flowork_kernel", "services", "module_manager_service", "module_manager_service.py")
        analyzer_path = os.path.join(self.kernel.project_root_path, "flowork_kernel", "services", "ai_analyzer_service", "ai_analyzer_service.py")
        tab_action_handler_path = os.path.join(self.kernel.project_root_path, "flowork_kernel", "ui_shell", "ui_components", "controllers", "TabActionHandler.py")
        checks = [
            (workflow_executor_path, "event_bus.publish(\"NODE_EXECUTION_METRIC\"", "Workflow Executor is publishing detailed metrics."),
            (metrics_logger_path, "event_name=\"NODE_EXECUTION_METRIC\"", "Metrics Logger is subscribing to detailed metrics."),
            (module_manager_path, "if not is_paused and hasattr(module_instance, 'on_load'):", "Module Manager calls the 'on_load' lifecycle hook."),
            (analyzer_path, ".startswith(\"```json\")", "AI Analyzer can clean markdown from AI responses."),
            (tab_action_handler_path, "self.state_manager.set(f\"tab_preset_map::{self.tab.tab_id}\"", "Tab/Action Handler correctly saves the active preset name for the AI to find.")
        ]
        checks_passed = 0
        for file_path, content, description in checks:
            found, file_preview = self._check_file_content(file_path, content)
            if found:
                checks_passed += 1
                self.report(f"  [OK] -> {description}", "OK")
            else:
                error_message = f"  [CRITICAL] -> Regression detected! Check failed: '{description}'. The required code is missing."
                if file_preview:
                    error_message += f"\n    -> File preview for '{os.path.basename(file_path)}' starts with:\n---\n{file_preview}\n---"
                self._register_finding(error_message, context={"file": file_path})
        summary = f"AI Co-pilot Health Scan: {checks_passed}/{len(checks)} critical checks passed."
        self.report(f"[DONE] {summary}", "SUCCESS" if checks_passed == len(checks) else "WARN")
        return summary
    def _check_file_content(self, file_path, content_to_find):
        """Helper to check file content and return a preview on failure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content_to_find in content:
                    return True, None
                else:
                    preview = "\n".join(content.splitlines()[:15])
                    return False, preview
        except FileNotFoundError:
            self._register_finding(f"  [ERROR] -> File not found: {file_path}", context={"file": file_path})
            return False, None
