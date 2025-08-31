#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\variable_dialog.py
# JUMLAH BARIS : 87
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar, messagebox, scrolledtext
class VariableDialog(ttk.Toplevel):
    def __init__(self, parent, title, kernel, existing_name=None, existing_data=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.loc = kernel.get_service("localization_manager")
        self.result = None
        existing_data = existing_data or {}
        self.name_var = StringVar(value=existing_name or "")
        initial_mode = existing_data.get('mode', 'single')
        initial_value_text = ""
        if initial_mode == 'single':
            if existing_data.get('is_secret'):
                 initial_value_text = self.loc.get("settings_variables_dialog_secret_placeholder")
            else:
                 initial_value_text = existing_data.get('value', '')
        else: # (ADDED) For 'random' or 'sequential', join the list with newlines
            initial_value_text = "\n".join(existing_data.get('values', []))
        self.value_var_text = initial_value_text # (COMMENT) We use this to populate the text widget directly
        self.is_secret_var = BooleanVar(value=existing_data.get('is_secret', False))
        self.mode_var = StringVar(value=initial_mode)
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        name_label = ttk.Label(main_frame, text=self.loc.get("settings_variables_dialog_name", fallback="Name:"))
        name_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50)
        self.name_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        if existing_name:
            self.name_entry.config(state="readonly")
        value_label = ttk.Label(main_frame, text=self.loc.get("settings_variables_dialog_value", fallback="Value:"))
        value_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.value_entry = scrolledtext.ScrolledText(main_frame, width=50, height=8, wrap="word")
        self.value_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.value_entry.insert("1.0", self.value_var_text)
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=4, column=0, columnspan=2, pady=(10,0), sticky="ew")
        secret_check = ttk.Checkbutton(options_frame, text=self.loc.get("settings_variables_dialog_secret_check", fallback="Mask this value (secret)"), variable=self.is_secret_var)
        secret_check.pack(side="left", anchor="w")
        if existing_name:
            secret_check.config(state="disabled")
        mode_combo = ttk.Combobox(options_frame, textvariable=self.mode_var, values=["single", "random", "sequential"], state="readonly", width=12)
        mode_combo.pack(side="right", anchor="e")
        ttk.Label(options_frame, text="Retrieval Mode:").pack(side="right", padx=(0, 5)) # English Hardcode
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20,0), sticky="e")
        ok_button = ttk.Button(button_frame, text=self.loc.get("button_save", fallback="Save"), command=self._on_ok, bootstyle="success")
        ok_button.pack(side="right", padx=5)
        cancel_button = ttk.Button(button_frame, text=self.loc.get("button_cancel", fallback="Cancel"), command=self.destroy, bootstyle="secondary")
        cancel_button.pack(side="right")
        self.wait_window(self)
    def _on_ok(self):
        name = self.name_var.get().strip().upper()
        value_str = self.value_entry.get("1.0", "end-1c").strip()
        is_secret = self.is_secret_var.get()
        mode = self.mode_var.get()
        if not name:
            messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), self.loc.get("settings_variables_warn_name_empty", fallback="Name cannot be empty."), parent=self)
            return
        if not name.replace('_', '').isalnum():
            messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), self.loc.get("settings_variables_warn_name_format"), parent=self)
            return
        if value_str == "" or (self.name_entry.cget('state') == 'readonly' and value_str == self.loc.get("settings_variables_dialog_secret_placeholder")):
             messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), self.loc.get("settings_variables_warn_value_empty", fallback="Value cannot be empty."), parent=self)
             return
        final_value = None
        if mode == 'single':
            if '\n' in value_str:
                messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), "Single value mode cannot contain multiple lines.", parent=self)
                return
            final_value = value_str
        else: # random or sequential
            final_value = [line.strip() for line in value_str.split('\n') if line.strip()]
            if not final_value:
                messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), "Please provide at least one value for the pool.", parent=self)
                return
        self.result = (name, final_value, is_secret, mode)
        self.destroy()
