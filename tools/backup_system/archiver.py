#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\Users\User\Desktop\FLOWORK\tools\backup_system\archiver.py
# PERBAIKAN : - Menambahkan 'absolute_path = os.path.abspath(file_path)' untuk
#               mendefinisikan variabel yang hilang di dalam scope fungsi.
# 			- Memperbaiki variabel 'total_lines_after_write' dengan cara yang sama.
#######################################################################
import os
import time
import logging
import shutil
import re
import traceback

class Archiver:
    """Encapsulates all logic for cleaning source files and creating the backup.md archive."""

    def __init__(self, project_root):
        self.project_root = project_root

        self.backup_filename = "backup.md"
        self.backup_dir = os.path.join(self.project_root, "data", "plan")
        self.backup_file_path = os.path.join(self.backup_dir, self.backup_filename)

        # MODIFIED: Added 'ai_models' to the exclusion list.
        self.excluded_dirs_entirely = {'.git', '.idea', '__pycache__', 'build', 'dist', 'flowork.egg-info', 'tools', 'generated_services', 'data', 'ai_models','docs','vendor','python','supabase','logs','.venv'}

        self.excluded_files = {self.backup_filename, '.gitignore', 'refactor_scanners.py', 'run_scanners_cli.py', '__init__.py','get-pip.py','mkdocs.yml','nuitka-crash-report.xml'}

        self.allowed_extensions_for_content = {'.py', '.json'}

        self.included_specific_files_for_content = set()
        self.excluded_extensions_for_map = {'.awenkaudico', '.teetah', '.pyd', '.aola', '.so', '.c', '.egg-info','get-pip.py','.vendor_hash','.module.flowork','.plugin.flowork','.flowork'}

    def _get_line_count(self, file_path):
        """
        Counts the total number of lines in a file, including empty ones.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = sum(1 for line in f)
            return line_count
        except Exception as e:
            logging.error(f"ARCHIVER: Could not count lines for {file_path}: {e}")
            return 0

    def clean_pycache(self):
        logging.info("Starting Python cache cleanup...")
        cleaned_count = 0
        for root, dirs, _ in os.walk(self.project_root):
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(pycache_path)
                    cleaned_count += 1
                except Exception as e:
                    logging.error(f"FAILED TO DELETE CACHE: {pycache_path} | Error: {e}")
        if cleaned_count > 0:
            logging.info(f"Cache cleanup complete. {cleaned_count} __pycache__ folders deleted.")
        else:
            logging.info("No __pycache__ folders found.")

    def clean_python_comments(self, content):
        pattern = re.compile(r"^\s*#.*$")
        return "\n".join([line for line in content.splitlines() if not pattern.match(line)])

    def fix_file_spacing(self, source_code: str) -> str:
        lines = source_code.splitlines()
        non_blank_lines = [line for line in lines if line.strip()]
        return "\n".join(non_blank_lines)

    def process_source_files(self):
        logging.info("--- STARTING SOURCE FILE FIX & STAMP OPERATION (EDIT MASAL UNTUK .PY) ---")
        files_to_process = [f for f in self.get_content_backup_files() if f.endswith('.py')]

        old_header_footer_pattern = re.compile(r"#######################################################################.*?awenk audico.*?#######################################################################\n?", re.DOTALL)

        for file_path in files_to_process:
            if os.path.abspath(file_path) == os.path.abspath(__file__):
                continue
            try:
                logging.info(f"PROCESSING .PY FILE: {os.path.basename(file_path)}")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    original_content = f.read()

                core_code = old_header_footer_pattern.sub("", original_content).strip()

                if not core_code:
                    logging.info(f"Skipping .py file with no core code: {os.path.basename(file_path)}")
                    continue

                content_no_comments = self.clean_python_comments(core_code)
                content_fixed_spacing = self.fix_file_spacing(content_no_comments)

                absolute_path = os.path.abspath(file_path)
                core_code_line_count = len(content_fixed_spacing.splitlines())
                total_lines_after_write = 7 + core_code_line_count

                header_footer_block = (
                    "#######################################################################\n"
                    f"# dev : awenk audico\n"
                    f"# EMAIL SAHIDINAOLA@GMAIL.COM\n"
                    f"# WEBSITE https://github.com/FLOWORK-gif/FLOWORK\n"
                    f"# File NAME : {absolute_path}\n"
                    f"# JUMLAH BARIS : {total_lines_after_write}\n"
                    "#######################################################################"
                )

                final_content = f"{header_footer_block}\n\n{content_fixed_spacing}\n"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
            except Exception as e:
                logging.error(f"MODIFICATION FAILED: {os.path.basename(file_path)} | Error: {e}")
                logging.error(traceback.format_exc())
        logging.info("--- SOURCE FILE FIX & STAMP OPERATION COMPLETE ---")

    def get_content_backup_files(self):
        content_files = []

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs_entirely]

            for file in files:
                if file in self.excluded_files:
                    continue
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1]
                if file_extension in self.allowed_extensions_for_content:
                    content_files.append(file_path)
        return content_files

    def format_backup_content(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lstrip('.')
        # ADDED: Define the missing variables within the correct scope.
        absolute_path = os.path.abspath(file_path)
        total_lines_after_write = self._get_line_count(file_path)

        line_count = self._get_line_count(file_path)
        header_block = (
                    "#######################################################################\n"
                    f"# dev : awenk audico\n"
                    f"# EMAIL SAHIDINAOLA@GMAIL.COM\n"
                    f"# WEBSITE https://github.com/FLOWORK-gif/FLOWORK\n"
                    f"# File NAME : {absolute_path}\n"
                    f"# JUMLAH BARIS : {total_lines_after_write}\n"
                    "#######################################################################"
        )

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()

            if file_path.endswith('.py'):
                old_header_pattern = re.compile(r"#######################################################################.*?awenk audico.*?#######################################################################\n?", re.DOTALL)
                content = old_header_pattern.sub("", content).strip()

            if content:
                return f"{header_block}\n\n```{file_extension}\n{content}\n```"
            else:
                return None
        except Exception as e:
            logging.error(f"FAILED TO READ (for backup): {file_path} | Error: {e}")
            return None

    def run_backup_cycle(self):
        logging.info("--- STARTING MAIN CYCLE ---")
        self.clean_pycache()
        logging.info("Waiting 1 second after cache cleanup.")
        time.sleep(1)

        self.process_source_files()
        logging.info("Waiting 1 second after source file modification.")
        time.sleep(1)

        logging.info(f"Starting archive creation process to '{self.backup_file_path}'...")
        os.makedirs(self.backup_dir, exist_ok=True)

        files_to_archive = self.get_content_backup_files()

        with open(self.backup_file_path, 'w', encoding='utf-8') as backup_f:
            all_content_blocks = []
            for file_path in files_to_archive:
                formatted_content = self.format_backup_content(file_path)
                if formatted_content:
                    all_content_blocks.append(formatted_content)

            backup_f.write("\n\n".join(all_content_blocks))

        logging.info(f"Archive '{self.backup_filename}' successfully created in data/plan folder. {len(all_content_blocks)} file contents were archived.")
        logging.info("--- MAIN CYCLE COMPLETE ---\n")