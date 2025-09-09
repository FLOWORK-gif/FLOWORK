#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\fix_imports.py
# JUMLAH BARIS : 74
#######################################################################

import os
import re
def fix_imports_in_file(file_path):
    """Reads a file, fixes imports based on new rules, and writes it back."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return 0
    new_lines = []
    changes_made = 0
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('#'):
            new_lines.append(line)
            continue
        match1 = re.match(r"^\s*from\s+flowork_gui\.([\w.]+)\s+import\s+.*", stripped_line)
        if match1:
            corrected_import = stripped_line.replace("flowork_gui.", "", 1)
            new_lines.append(f"# {stripped_line} # (PERBAIKAN OTOMATIS v2)\n")
            new_lines.append(f"{corrected_import}\n")
            changes_made += 1
            continue
        match2 = re.match(r"^\s*from\s+flowork_kernel\.ui_shell\.([\w.]+)\s+import\s+.*", stripped_line)
        if match2:
            corrected_import = stripped_line.replace("flowork_kernel.ui_shell", "views", 1)
            new_lines.append(f"# {stripped_line} # (PERBAIKAN OTOMATIS v2)\n")
            new_lines.append(f"{corrected_import}\n")
            changes_made += 1
            continue
        new_lines.append(line)
    if changes_made > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"  - Patched {changes_made} import(s) in: {os.path.basename(file_path)}")
            return changes_made
        except Exception:
            return 0
    return 0
def main():
    """Main function to run the import fixer."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    print("\n--- Starting Automatic Import Fixer Script v2.0 ---")
    print(f"Scanning project root: {project_root}\n")
    total_files_patched = 0
    total_fixes_made = 0
    for root, _, files in os.walk(project_root):
        if '__pycache__' in root or '.venv' in root:
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if os.path.basename(file_path) == "fix_imports.py":
                    continue
                fixes = fix_imports_in_file(file_path)
                if fixes > 0:
                    total_files_patched += 1
                    total_fixes_made += fixes
    print("\n--- Doctor Script v2.0 Finished ---")
    if total_fixes_made > 0:
        print(f"✅ Success! Made {total_fixes_made} fixes across {total_files_patched} files.")
        print("All import paths should now be corrected.")
    else:
        print("✅ No incorrect imports found. Everything looks good!")
if __name__ == "__main__":
    main()
