#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\upload_dialog.py
# JUMLAH BARIS : 57
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, messagebox
from tkinter.scrolledtext import ScrolledText
class UploadDialog(ttk.Toplevel):
    """
    A dialog for users to enter details before uploading a component to the marketplace.
    """
    def __init__(self, parent, kernel, component_name):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.title(self.loc.get('marketplace_upload_dialog_title', fallback="Upload to Community"))
        self.result = None
        self.description_var = StringVar()
        self.tier_var = StringVar()
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text=self.loc.get('marketplace_upload_dialog_header', component_name=component_name, fallback=f"You are about to upload: {component_name}")).pack(pady=(0, 10))
        ttk.Label(main_frame, text=self.loc.get('marketplace_upload_dialog_desc_label', fallback="Description:")).pack(anchor='w')
        self.description_text = ScrolledText(main_frame, height=5, wrap="word")
        self.description_text.pack(fill="x", pady=(0, 10))
        self.description_text.insert("1.0", f"A great component: {component_name}")
        ttk.Label(main_frame, text=self.loc.get('marketplace_upload_dialog_tier_label', fallback="Select Tier:")).pack(anchor='w')
        tier_options = list(self.kernel.TIER_HIERARCHY.keys())
        tier_combo = ttk.Combobox(main_frame, textvariable=self.tier_var, values=tier_options, state="readonly")
        tier_combo.pack(fill="x")
        tier_combo.set("free") # Default to free tier
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        upload_button = ttk.Button(button_frame, text=self.loc.get('marketplace_upload_btn', fallback="Upload"), command=self._on_upload, bootstyle="success")
        upload_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text=self.loc.get('button_cancel', fallback="Cancel"), command=self.destroy, bootstyle="secondary")
        cancel_button.pack(side="right", padx=(0, 10))
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    def _on_upload(self):
        """
        Validates the input and sets the result.
        """
        description = self.description_text.get("1.0", "end-1c").strip()
        tier = self.tier_var.get()
        if not description or not tier:
            messagebox.showwarning(self.loc.get('warning_title', fallback="Warning"), self.loc.get('marketplace_upload_dialog_validation_error', fallback="Description and Tier cannot be empty."), parent=self)
            return
        self.result = {
            "description": description,
            "tier": tier
        }
        self.destroy()
