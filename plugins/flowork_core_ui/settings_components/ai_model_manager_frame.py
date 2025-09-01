#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\ai_model_manager_frame.py
# JUMLAH BARIS : 53
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox
import os
import threading
class AiModelManagerFrame(ttk.LabelFrame):
    """UI component for managing the on-demand download of AI models."""
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text="Manajemen Model AI Lokal", padding=15)
        self.status_label = ttk.Label(self, text="Mengecek status...", anchor="center")
        self.status_label.pack(pady=5, fill="x")
        self.download_button = ttk.Button(self, text="Download Model AI (~70 GB)", command=self._start_download_action)
        self.download_button.pack(pady=5, fill="x", ipady=5)
        self.progress_bar = ttk.Progressbar(self, mode='determinate')
        self.progress_bar.pack(pady=5, fill="x")
        self.progress_bar.pack_forget() # Sembunyikan dulu
        self.check_status()
    def check_status(self):
        """Checks if models are installed and updates the UI accordingly."""
        ai_models_path = os.path.join(self.kernel.project_root_path, "ai_models")
        if os.path.isdir(ai_models_path):
            self.status_label.config(text="Model AI Lokal sudah terinstall.", bootstyle="success")
            self.download_button.pack_forget()
            self.progress_bar.pack_forget()
        else:
            self.status_label.config(text="Model AI Lokal belum terinstall.", bootstyle="warning")
            self.download_button.pack(pady=5, fill="x", ipady=5) # Tampilkan tombol
            if self.kernel.is_tier_sufficient('pro'):
                self.download_button.config(state="normal")
            else:
                self.download_button.config(state="disabled")
                self.status_label.config(text="Model AI membutuhkan lisensi PRO atau lebih tinggi.")
    def _start_download_action(self):
        """Starts the download process in a background thread."""
        if messagebox.askyesno("Konfirmasi Download", "Proses ini akan mengunduh file berukuran sangat besar (~70 GB) dan mungkin memakan waktu lama. Lanjutkan?"):
            self.download_button.config(state="disabled")
            self.progress_bar.pack(pady=5, fill="x")
            self.status_label.config(text="Fitur download sedang dalam pengembangan...")
            self.kernel.write_to_log("TODO: Implement asset downloader service call.", "WARN")
    def load_settings_data(self, settings_data):
        """This component is stateful and doesn't load from settings."""
        self.check_status()
    def get_settings_data(self):
        """This component doesn't save any settings."""
        return {}
