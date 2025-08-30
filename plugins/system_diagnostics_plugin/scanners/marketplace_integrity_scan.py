#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\system_diagnostics_plugin\scanners\marketplace_integrity_scan.py
# JUMLAH BARIS : 46
#######################################################################

import os
from .base_scanner import BaseScanner
class MarketplaceIntegrityScan(BaseScanner):
    """
    Ensures the Marketplace UI correctly delegates the upload process to the backend
    services, following the decoupled architecture principles.
    This scanner acts as a regression test for the contribution feature's architecture.
    """
    def run_scan(self) -> str:
        self.report("\n[SCAN] === Starting Marketplace Contribution Architecture Scan ===", "SCAN")
        marketplace_page_path = os.path.join(self.kernel.project_root_path, "plugins", "flowork_core_ui", "marketplace_page.py")
        api_client_path = os.path.join(self.kernel.project_root_path, "flowork_kernel", "api_client.py")
        api_server_path = os.path.join(self.kernel.project_root_path, "flowork_kernel", "services", "api_server_service", "api_server_service.py")
        addon_service_path = os.path.join(self.kernel.project_root_path, "flowork_kernel", "services", "community_addon_service", "community_addon_service.py")
        checks = [
            (marketplace_page_path, "self.api_client.upload_component", "Marketplace UI correctly delegates upload to ApiClient."),
            (api_client_path, "requests.post(f\"{self.base_url}/addons/upload\"", "ApiClient correctly calls the /addons/upload endpoint."),
            (api_server_path, "addon_service.upload_component(comp_type, component_id)", "ApiServer correctly routes the request to CommunityAddonService."),
            (addon_service_path, "variable_manager.get_variable('GITHUB_UPLOAD_TOKEN')", "CommunityAddonService handles fetching the GitHub API token."),
            (addon_service_path, "diagnostics_plugin.scan_single_component_and_get_status", "CommunityAddonService handles the pre-flight scan.")
        ]
        checks_passed = 0
        for file_path, check_string, description in checks:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if check_string in content:
                    checks_passed += 1
                    self.report(f"  [OK] -> {description}", "OK")
                else:
                    self._register_finding(
                        f"  [CRITICAL] -> Architectural Regression! Check failed: '{description}'. The required logic is missing from '{os.path.basename(file_path)}'.",
                        context={"file": file_path}
                    )
            except FileNotFoundError:
                self._register_finding(f"  [CRITICAL] -> Required file for architecture check not found: {os.path.basename(file_path)}", "CRITICAL")
        summary = f"Marketplace Architecture Scan: {checks_passed}/{len(checks)} critical architectural checks passed."
        self.report(f"[DONE] {summary}", "SUCCESS" if checks_passed == len(checks) else "WARN")
        return summary
