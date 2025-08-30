#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\version_manager_popup.py
# JUMLAH BARIS : 116
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel, messagebox, ttk as tk_ttk, Menu
from flowork_kernel.api_client import ApiClient
class VersionManagerPopup(Toplevel):
    def __init__(self, parent_workflow_tab, kernel_instance, preset_name):
        super().__init__(parent_workflow_tab)
        self.parent_workflow_tab = parent_workflow_tab
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.preset_name = preset_name
        self.api_client = ApiClient(kernel=self.kernel)
        self.title(self.loc.get('version_manager_title', preset_name=self.preset_name))
        self.transient(parent_workflow_tab)
        self.grab_set()
        self.resizable(False, False)
        theme_manager = self.kernel.get_service("theme_manager")
        self.colors = theme_manager.get_colors() if theme_manager else {}
        self.apply_styles(self.colors)
        self.create_widgets()
        self.populate_versions()
        self.update_idletasks()
        x = parent_workflow_tab.winfo_x() + (parent_workflow_tab.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent_workflow_tab.winfo_y() + (parent_workflow_tab.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    def apply_styles(self, colors):
        style = tk_ttk.Style(self)
        style.configure('TFrame', background=colors.get('bg'))
        style.configure('TLabel', background=colors.get('bg'), foreground=colors.get('fg'))
        style.configure("Custom.Treeview", background=colors.get('dark'), foreground=colors.get('fg'), fieldbackground=colors.get('dark'), borderwidth=0, rowheight=25)
        style.configure("Custom.Treeview.Heading", background=colors.get('bg'), foreground=colors.get('info'), font=('Helvetica', 10, 'bold'))
        style.map('Custom.Treeview', background=[('selected', colors.get('selectbg'))], foreground=[('selected', colors.get('selectfg'))])
        self.configure(background=colors.get('bg'))
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=15, style='TFrame')
        main_frame.pack(fill='both', expand=True)
        ttk.Label(main_frame, text=self.loc.get('version_list_label'), style='TLabel').pack(anchor='w', pady=(0, 5))
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        columns = ("Nama Versi", "Tanggal & Waktu", "Aksi")
        self.version_tree = tk_ttk.Treeview(tree_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.version_tree.heading("Nama Versi", text=self.loc.get('version_name_column', fallback="Version Name"))
        self.version_tree.heading("Tanggal & Waktu", text=self.loc.get('version_datetime_column', fallback="Date & Time"))
        self.version_tree.heading("Aksi", text=self.loc.get('version_actions_column', fallback="Actions"))
        self.version_tree.column("Nama Versi", width=250, anchor='w')
        self.version_tree.column("Tanggal & Waktu", width=150, anchor='center')
        self.version_tree.column("Aksi", width=120, anchor='center')
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.version_tree.yview)
        self.version_tree.configure(yscrollcommand=tree_scrollbar_y.set)
        self.version_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar_y.pack(side='right', fill='y')
        self.version_tree.bind("<Button-1>", self._on_tree_click)
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill='x', side='bottom', pady=(5, 0))
        ttk.Button(button_frame, text=self.loc.get('button_close', fallback="Close"), command=self.destroy, style='secondary.TButton').pack(side='right')
    def populate_versions(self):
        for item in self.version_tree.get_children():
            self.version_tree.delete(item)
        self.kernel.write_to_log(f"UI: Requesting versions for '{self.preset_name}' via API.", "DEBUG")
        success, versions = self.api_client.get_preset_versions(self.preset_name)
        if not versions or not success:
            self.version_tree.insert("", "end", values=(self.loc.get('no_versions_found'), "", ""), tags=("no_data",))
            return
        for version_info in versions:
            version_display_name = self.loc.get('version_name_format', timestamp=version_info['timestamp'])
            action_placeholder = self.loc.get('version_action_column_placeholder', fallback="Click for Actions...")
            self.version_tree.insert("", "end", values=(version_display_name, version_info['timestamp'], action_placeholder), tags=(version_info['filename'],))
    def _on_tree_click(self, event):
        region = self.version_tree.identify_region(event.x, event.y)
        column_id = self.version_tree.identify_column(event.x)
        if region == "cell" and column_id == "#3":
            item_id = self.version_tree.identify_row(event.y)
            if not item_id: return
            version_filename = self.version_tree.item(item_id, "tags")[0]
            if version_filename == "no_data": return
            self._show_action_menu(event, version_filename)
    def _show_action_menu(self, event, version_filename):
        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label=self.loc.get('version_action_load'), command=lambda: self._load_selected_version(version_filename))
        context_menu.add_command(label=self.loc.get('version_action_delete'), command=lambda: self._delete_selected_version(version_filename))
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    def _load_selected_version(self, version_filename):
        if not messagebox.askyesno(
            self.loc.get('confirm_load_version_title', fallback="Load Version?"),
            self.loc.get('confirm_load_version_message', version_name=version_filename, preset_name=self.preset_name)
        ):
            return
        self.kernel.write_to_log(self.loc.get('log_loading_version', preset_name=self.preset_name, version_name=version_filename), "INFO")
        success, workflow_data = self.api_client.load_preset_version(self.preset_name, version_filename)
        if success and workflow_data:
            self.parent_workflow_tab.canvas_area_instance.canvas_manager.load_workflow_data(workflow_data)
            messagebox.showinfo(self.loc.get('success_title'), self.loc.get('log_version_loaded_success', preset_name=self.preset_name, version_name=version_filename))
            self.destroy()
        else:
            messagebox.showerror(self.loc.get('error_title'), self.loc.get('log_version_load_error', preset_name=self.preset_name, version_name=version_filename, error="Failed to load version file via API."))
    def _delete_selected_version(self, version_filename):
        if not messagebox.askyesno(
            self.loc.get('confirm_delete_version_title'),
            self.loc.get('confirm_delete_version_message', version_name=version_filename)
        ):
            return
        success, response = self.api_client.delete_preset_version(self.preset_name, version_filename)
        if success:
            messagebox.showinfo(self.loc.get('success_title'), self.loc.get('log_version_deleted_success', preset_name=self.preset_name, version_name=version_filename))
            self.populate_versions()
        else:
            messagebox.showerror(self.loc.get('error_title'), self.loc.get('log_version_delete_error', preset_name=self.preset_name, version_name=version_filename, error=response))
