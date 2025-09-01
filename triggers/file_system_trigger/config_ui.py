#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\triggers\file_system_trigger\config_ui.py
# JUMLAH BARIS : 41
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar, filedialog
class FileSystemConfigUI(ttk.Frame):
    """UI untuk mengkonfigurasi pemicu File System."""
    def __init__(self, parent, loc, initial_config):
        super().__init__(parent)
        self.loc = loc
        self.path_var = StringVar(value=initial_config.get('path_to_watch', ''))
        self.event_created_var = BooleanVar(value=initial_config.get('on_created', True))
        self.event_modified_var = BooleanVar(value=initial_config.get('on_modified', True))
        self.event_deleted_var = BooleanVar(value=initial_config.get('on_deleted', False))
        path_frame = ttk.Frame(self)
        path_frame.pack(fill='x', expand=True, pady=(0, 10))
        ttk.Label(path_frame, text=self.loc.get('filesystem_label_path', fallback="Folder/File untuk Dipantau:")).pack(anchor='w')
        entry_frame = ttk.Frame(path_frame)
        entry_frame.pack(fill='x', expand=True)
        ttk.Entry(entry_frame, textvariable=self.path_var).pack(side='left', fill='x', expand=True)
        ttk.Button(entry_frame, text="...", command=self._browse_path, width=4).pack(side='left', padx=(5,0))
        event_frame = ttk.LabelFrame(self, text=self.loc.get('filesystem_label_events', fallback="Jenis Kejadian"))
        event_frame.pack(fill='x', expand=True)
        ttk.Checkbutton(event_frame, text=self.loc.get('filesystem_event_created', fallback="Saat Dibuat"), variable=self.event_created_var).pack(anchor='w', padx=5)
        ttk.Checkbutton(event_frame, text=self.loc.get('filesystem_event_modified', fallback="Saat Diubah"), variable=self.event_modified_var).pack(anchor='w', padx=5)
        ttk.Checkbutton(event_frame, text=self.loc.get('filesystem_event_deleted', fallback="Saat Dihapus"), variable=self.event_deleted_var).pack(anchor='w', padx=5)
    def _browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
    def get_config(self):
        return {
            "path_to_watch": self.path_var.get(),
            "on_created": self.event_created_var.get(),
            "on_modified": self.event_modified_var.get(),
            "on_deleted": self.event_deleted_var.get()
        }
