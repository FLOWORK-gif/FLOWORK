#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\variable_manager_frame.py
# JUMLAH BARIS : 158
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox
from .variable_dialog import VariableDialog
from flowork_kernel.api_client import ApiClient
import threading
import base64
class VariableManagerFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_variables_title", fallback="Variable & Secret Management"), padding=15)
        self.variables_data_cache = []
        self.api_client = ApiClient(kernel=self.kernel)
        self._build_widgets()
        self.load_variables_to_ui()
    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=0, sticky="nsew", columnspan=3)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        columns = ("name", "value", "status")
        self.var_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.var_tree.heading("name", text=self.loc.get("settings_variables_col_name", fallback="Variable Name"))
        self.var_tree.heading("value", text=self.loc.get("settings_variables_col_value", fallback="Value"))
        self.var_tree.heading("status", text=self.loc.get("settings_variables_col_status", fallback="Status"))
        self.var_tree.column("name", width=150, anchor="w")
        self.var_tree.column("value", width=300, anchor="w")
        self.var_tree.column("status", width=80, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.var_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.var_tree.xview)
        self.var_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.var_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10,0))
        add_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_btn_add", fallback="Add"), command=self._add_variable)
        add_button.pack(side="left", padx=5)
        edit_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_btn_edit", fallback="Edit"), command=self._edit_variable, bootstyle="info")
        edit_button.pack(side="left", padx=5)
        self.toggle_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_btn_disable", fallback="Disable"), command=self._toggle_variable_state, bootstyle="warning")
        self.toggle_button.pack(side="left", padx=5)
        delete_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_btn_delete", fallback="Delete"), command=self._delete_variable, bootstyle="danger")
        delete_button.pack(side="left", padx=5)
        copy_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_action_copy", fallback="[ Copy ]"), command=self._copy_variable_placeholder, bootstyle="secondary-outline")
        copy_button.pack(side="right", padx=5)
        self.var_tree.bind('<<TreeviewSelect>>', self._update_button_state)
    def load_variables_to_ui(self):
        for item in self.var_tree.get_children():
            self.var_tree.delete(item)
        threading.Thread(target=self._load_variables_worker, daemon=True).start()
    def _load_variables_worker(self):
        success, data = self.api_client.get_variables()
        self.after(0, self._populate_tree_from_data, success, data)
    def _populate_tree_from_data(self, success, data):
        if success:
            self.variables_data_cache = data
            for var_data in self.variables_data_cache:
                is_enabled = var_data.get('is_enabled', True)
                status_text = self.loc.get("status_enabled") if is_enabled else self.loc.get("status_disabled")
                value_for_display = ""
                if var_data.get('mode', 'single') != 'single':
                    value_for_display = f"[Pool: {len(var_data.get('values', []))} keys] - Mode: {var_data.get('mode', '').capitalize()}"
                elif var_data.get('is_secret'):
                    value_for_display = '*****'
                else:
                    value_for_display = var_data.get('value')
                tags = ('secret' if var_data.get('is_secret') else 'normal',)
                if not is_enabled:
                    tags += ('disabled',)
                self.var_tree.insert("", "end", iid=var_data["name"], values=(var_data["name"], value_for_display, status_text), tags=tags)
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"Failed to load variables from API: {data}")
        self.var_tree.tag_configure('secret', foreground='orange')
        self.var_tree.tag_configure('disabled', foreground='grey')
        self._update_button_state()
    def _add_variable(self):
        dialog = VariableDialog(self, title=self.loc.get("settings_variables_dialog_add_title", fallback="Add New Variable"), kernel=self.kernel)
        if dialog.result:
            name, value, is_secret, mode = dialog.result
            success, response = self.api_client.update_variable(name, value, is_secret, is_enabled=True, mode=mode)
            if success:
                self.load_variables_to_ui()
            else:
                messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _edit_variable(self):
        selected_item = self.var_tree.focus()
        if not selected_item:
            messagebox.showwarning(self.loc.get("messagebox_warning_title"), self.loc.get("settings_variables_warn_select_to_edit"), parent=self)
            return
        var_name = selected_item
        var_backend_data = next((vc for vc in self.variables_data_cache if vc['name'] == var_name), None)
        if not var_backend_data:
            messagebox.showerror(self.loc.get("messagebox_error_title"), "Could not find variable data to edit.")
            return
        dialog = VariableDialog(self, title=self.loc.get("settings_variables_dialog_edit_title"), kernel=self.kernel, existing_name=var_name, existing_data=var_backend_data)
        if dialog.result:
            _name, value, is_secret, mode = dialog.result
            success, response = self.api_client.update_variable(var_name, value, is_secret, var_backend_data.get('is_enabled', True), mode=mode)
            if success:
                self.load_variables_to_ui()
            else:
                messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _toggle_variable_state(self):
        selected_item = self.var_tree.focus()
        if not selected_item: return
        var_name = selected_item
        var_cache = next((vc for vc in self.variables_data_cache if vc['name'] == var_name), None)
        if not var_cache: return
        new_state = not var_cache.get('is_enabled', True)
        success, response = self.api_client.update_variable_state(var_name, new_state)
        if success:
            self.load_variables_to_ui()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _update_button_state(self, event=None):
        selected_item = self.var_tree.focus()
        if not selected_item:
            self.toggle_button.config(state="disabled")
            return
        self.toggle_button.config(state="normal")
        var_cache = next((vc for vc in self.variables_data_cache if vc['name'] == selected_item), None)
        if var_cache:
            if var_cache.get('is_enabled', True):
                self.toggle_button.config(text=self.loc.get("settings_variables_btn_disable", fallback="Disable"))
            else:
                self.toggle_button.config(text=self.loc.get("settings_variables_btn_enable", fallback="Enable"))
    def _delete_variable(self):
        selected_item = self.var_tree.focus()
        if not selected_item:
            messagebox.showwarning(self.loc.get("messagebox_warning_title"), self.loc.get("settings_variables_warn_select_to_delete"), parent=self)
            return
        var_name = selected_item
        if messagebox.askyesno(self.loc.get("messagebox_confirm_title"), self.loc.get("settings_variables_confirm_delete", var_name=var_name), parent=self):
            success, response = self.api_client.delete_variable(var_name)
            if success:
                self.load_variables_to_ui()
            else:
                 messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _copy_variable_placeholder(self):
        selected_item = self.var_tree.focus()
        if not selected_item:
            messagebox.showwarning(self.loc.get("messagebox_warning_title"), self.loc.get("settings_variables_warn_select_to_copy"), parent=self)
            return
        var_name = selected_item
        placeholder = f"{{{{vars.{var_name}}}}}"
        self.clipboard_clear()
        self.clipboard_append(placeholder)
        self.kernel.write_to_log(self.loc.get("settings_variables_copy_success", fallback=f"Placeholder '{placeholder}' has been copied to clipboard."), "SUCCESS")
