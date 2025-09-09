#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\backup.py
# JUMLAH BARIS : 46
#######################################################################

import os
import sys
def main():
    """
    Scans the project directory for all .py files, formats them into a markdown file,
    and saves it as backup.md. This script is designed to package the current
    state of the code for analysis or sharing.
    """
    project_root = os.getcwd()
    output_filename = "GUI.md"
    ignore_dirs = {'.venv', '__pycache__', 'python','vendor'}
    all_content = []
    print("[INFO] Starting code backup process...") # English Log
    for root, dirs, files in os.walk(project_root, topdown=True):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in sorted(files):
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_root)
                print(f"[INFO] Processing: {relative_path}") # English Log
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        line_count = len(content.splitlines())
                    header = (
                        f"\n\n"
                    )
                    formatted_content = f"```py\n{content}\n```"
                    all_content.append(header + formatted_content)
                except Exception as e:
                    print(f"[ERROR] Could not process file {relative_path}: {e}") # English Log
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(all_content))
        print(f"\n[SUCCESS] Backup complete! All code saved to '{output_filename}'") # English Log
    except Exception as e:
        print(f"\n[FATAL] Failed to write backup file: {e}") # English Log
if __name__ == "__main__":
    main()
