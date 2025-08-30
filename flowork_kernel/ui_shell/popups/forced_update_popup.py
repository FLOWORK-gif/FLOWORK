#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\popups\forced_update_popup.py
# JUMLAH BARIS : 67
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel, scrolledtext
import webbrowser
class ForcedUpdatePopup(Toplevel):
    """
    A custom, non-closable popup that forces the user to update.
    This version is fully localized.
    """
    def __init__(self, parent, kernel, update_info):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.update_info = update_info
        self.title(self.loc.get('update_popup_title', fallback="Mandatory Update Available"))
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        self.configure(background=colors.get('bg', '#222'))
        self._create_widgets(colors)
        self._center_window()
    def _create_widgets(self, colors):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        version = self.update_info.get('version', 'N/A')
        header_text = self.loc.get('update_popup_header', fallback="Update to Version {version} Required", version=version)
        ttk.Label(main_frame, text=header_text, font=("Helvetica", 14, "bold")).pack(pady=(0, 10))
        ttk.Label(main_frame, text=self.loc.get('update_popup_changelog_label', fallback="Changes in this version:"), justify="left").pack(anchor='w', pady=(10, 2))
        changelog_text = scrolledtext.ScrolledText(main_frame, height=8, wrap="word", font=("Helvetica", 9))
        changelog_text.pack(fill="both", expand=True, pady=(0, 15))
        changelog_content = self.update_info.get('changelog', ["No details available."])
        changelog_text.insert("1.0", "\n".join(f"- {item}" for item in changelog_content))
        changelog_text.config(state="disabled")
        self.update_button = ttk.Button(
            main_frame,
            text=self.loc.get('update_popup_button', fallback="Download Update & Exit"),
            command=self._do_update,
            bootstyle="success"
        )
        self.update_button.pack(fill='x', ipady=5)
    def _do_update(self):
        self.update_button.config(state="disabled", text=self.loc.get('update_popup_button_loading', fallback="Opening browser..."))
        download_url = self.update_info.get('download_url')
        if download_url:
            webbrowser.open(download_url)
        self.after(2000, self.kernel.root.destroy)
    def _center_window(self):
        self.update_idletasks()
        parent_window = self.master
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()
        win_x = parent_x + (parent_width // 2) - (popup_width // 2)
        win_y = parent_y + (parent_height // 2) - (popup_height // 2)
        self.geometry(f"+{win_x}+{win_y}")
