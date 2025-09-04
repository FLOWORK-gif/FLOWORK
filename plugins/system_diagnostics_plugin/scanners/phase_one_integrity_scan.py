#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\system_diagnostics_plugin\scanners\phase_one_integrity_scan.py
# JUMLAH BARIS : 111
#######################################################################

import os
import re
from .base_scanner import BaseScanner
class PhaseOneIntegrityScan(BaseScanner):
    """
    Scans the UI layer to enforce the rules of Phase 1: Total Independence.
    This "Doctor Code" scanner not only finds violations but also attempts to
    auto-patch them by replacing direct kernel calls with their ApiClient equivalents.
    """
    def run_scan(self) -> str:
        self.report("\n[SCAN] === Starting Phase 1: Independence Integrity Scan (Doctor Code Mode) ===", "SCAN")
        ui_paths = [
            os.path.join(self.kernel.project_root_path, "flowork_kernel", "ui_shell"),
            os.path.join(self.kernel.project_root_path, "widgets"),
            os.path.join(self.kernel.project_root_path, "plugins")
        ]
        illegal_pattern = re.compile(r"self\.kernel\.get_service\([\"']([\w_]+)[\"']\)\.([\w_]+)\((.*)\)")
        files_scanned = 0
        total_violations_found = 0
        total_violations_healed = 0
        for path in ui_paths:
            if not os.path.isdir(path):
                continue
            for root, _, files in os.walk(path):
                if 'system_diagnostics_plugin' in root:
                    continue
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        files_scanned += 1
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                original_content = f.read()
                            content_to_patch = original_content
                            patches_made_in_file = 0
                            matches = list(illegal_pattern.finditer(original_content))
                            if matches:
                                for match in matches:
                                    total_violations_found += 1
                                    line_num = original_content.count('\n', 0, match.start()) + 1
                                    full_match_text = match.group(0)
                                    self.report(f"  [CRITICAL] -> Found violation in '{os.path.relpath(file_path, self.kernel.project_root_path)}' on line {line_num}:", "CRITICAL", context={"file": file_path, "line": line_num})
                                    self.report(f"    -> Code: {full_match_text}", "DEBUG")
                                    healed_code, patched_content = self._auto_patch_file(file_path, content_to_patch, match)
                                    if healed_code:
                                        self.report(f"    -> [HEALED] Auto-patched to: self.{healed_code}", "SUCCESS")
                                        content_to_patch = patched_content
                                        total_violations_healed += 1
                                        patches_made_in_file += 1
                                    else:
                                        self.report("    -> [MANUAL FIX NEEDED] Could not automatically determine the ApiClient equivalent.", "MAJOR")
                            if patches_made_in_file > 0:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(content_to_patch)
                                self.report(f"  -> Saved {patches_made_in_file} patch(es) to '{os.path.basename(file_path)}'.", "INFO")
                        except Exception as e:
                            self.report(f"  [ERROR] -> Could not read or process file: {file_path}. Reason: {e}", "CRITICAL")
        summary = f"Phase 1 Integrity Scan complete. Scanned {files_scanned} files. Found {total_violations_found} violations. Auto-healed {total_violations_healed}."
        self.report(f"[DONE] {summary}", "SUCCESS" if total_violations_found == total_violations_healed else "WARN")
        return summary
    def _auto_patch_file(self, file_path, current_content, match):
        """
        The core healing logic. Takes the file content and a regex match,
        and returns the patched content if successful.
        """
        service_name = match.group(1)
        method_name = match.group(2)
        arguments = match.group(3)
        service_to_api_map = {
            ("preset_manager_service", "get_preset_list"): "get_presets()",
            ("preset_manager_service", "get_preset_data"): f"get_preset_data({arguments})",
            ("module_manager_service", "get_manifest"): f"get_components('modules', {arguments})", # This is an approximation
            ("localization_manager", "get_setting"): f"get_all_settings()", # API gets all settings
        }
        api_equivalent_key = (service_name, method_name)
        if api_equivalent_key not in service_to_api_map:
            return None, current_content # Cannot heal automatically
        api_call = service_to_api_map[api_equivalent_key]
        new_code = f"api_client.{api_call}" # Assuming the instance is named self.api_client
        line_start_index = current_content.rfind('\n', 0, match.start()) + 1
        line_end_index = current_content.find('\n', match.end())
        line_content = current_content[line_start_index:line_end_index]
        assignment_match = re.match(r"(\s*)(([\w\s,]+)\s*=\s*)", line_content)
        if assignment_match:
            prefix = assignment_match.group(1) + assignment_match.group(2)
            new_line = prefix + f"self.{new_code}"
        else:
            prefix = re.match(r"(\s*)", line_content).group(1)
            new_line = prefix + f"self.{new_code}"
        patched_content = current_content.replace(match.group(0), new_code) # Use the simpler replacement for now
        import_str = "from flowork_kernel.api_client import ApiClient"
        if import_str not in patched_content:
            patched_content = import_str + "\n" + patched_content
        init_pattern = re.compile(r"def\s+__init__\(self,[^)]*\):")
        init_match = init_pattern.search(patched_content)
        instantiation_str = "self.api_client = ApiClient()"
        if init_match and instantiation_str not in patched_content:
            init_end = init_match.end()
            first_line_break = patched_content.find('\n', init_end)
            indentation_match = re.search(r"(\n\s+)", patched_content[first_line_break:])
            indentation = indentation_match.group(1) if indentation_match else "\n        "
            injection_point = first_line_break + 1
            patched_content = patched_content[:injection_point] + indentation + instantiation_str + patched_content[injection_point:]
        return new_code, patched_content
