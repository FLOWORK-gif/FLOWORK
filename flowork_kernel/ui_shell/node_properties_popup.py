#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\node_properties_popup.py
# JUMLAH BARIS : 62
#######################################################################

import ttkbootstrap as ttk
from tkinter import simpledialog
class NodePropertiesPopup(ttk.Toplevel):
    """
    Jendela popup generik untuk menampilkan properti node.
    Popup ini akan dibuat dan dikelola oleh PropertiesManager.
    """
    def __init__(self, parent, kernel, node_id, module_instance, get_config_func, save_config_func, available_vars):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.loc
        self.node_id = node_id
        self.module_instance = module_instance
        self.get_config_func = get_config_func
        self.save_config_func = save_config_func
        self.available_vars = available_vars
        self.property_vars = {}
        self.title(self.loc.get('properties_title', fallback="Properti Node") + f" ({node_id})")
        self.transient(parent)
        self.grab_set()
        self.main_frame = ttk.Frame(self, padding=15)
        self.main_frame.pack(fill="both", expand=True)
        self._build_ui()
        self.wait_window(self)
    def _build_ui(self):
        """Membangun antarmuka pengguna untuk jendela properti."""
        content_frame = ttk.Frame(self.main_frame, style='TFrame')
        content_frame.pack(fill="both", expand=True)
        if hasattr(self.module_instance, 'create_properties_ui'):
            self.property_vars = self.module_instance.create_properties_ui(
                parent_frame=content_frame,
                get_current_config=self.get_config_func,
                available_vars=self.available_vars
            )
        else:
            ttk.Label(content_frame, text="Modul ini tidak memiliki properti yang bisa diatur.").pack(pady=20)
        action_buttons_frame = ttk.Frame(self.main_frame, style='TFrame')
        action_buttons_frame.pack(side="bottom", fill="x", pady=(10, 0), padx=5)
        save_button = ttk.Button(action_buttons_frame, text=self.loc.get("button_save", fallback="Simpan"), command=self._save_and_close, bootstyle="success")
        save_button.pack(side="right", padx=5, pady=5)
        cancel_button = ttk.Button(action_buttons_frame, text=self.loc.get("button_cancel", fallback="Batal"), command=self.destroy, bootstyle="secondary")
        cancel_button.pack(side="right", padx=5, pady=5)
    def _save_and_close(self):
        """Menyimpan konfigurasi dan menutup jendela."""
        new_config = {}
        for key, var in self.property_vars.items():
            try:
                if hasattr(var, 'get_value'): # Ini adalah EnumVarWrapper
                    new_config[key] = var.get_value()
                else: # Variabel Tkinter biasa
                    new_config[key] = var.get()
            except Exception as e:
                self.kernel.write_to_log(f"Gagal mendapatkan nilai untuk properti '{key}': {e}", "WARN")
        self.save_config_func(new_config)
        self.destroy()
