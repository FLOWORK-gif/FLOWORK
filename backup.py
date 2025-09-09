#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\backup.py
# JUMLAH BARIS : 23
#######################################################################

import os
import logging
from tools.backup_system.archiver import Archiver
from tools.guardian_angel.guardian import GuardianAngel
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
def main():
    """
    The main entry point to start the backup guardian angel.
    This script's single responsibility is to launch the system.
    """
    project_root = os.getcwd()
    archiver_instance = Archiver(project_root=project_root)
    guardian = GuardianAngel(project_root=project_root, archiver_instance=archiver_instance)
    guardian.start()
if __name__ == "__main__":
    main()
