#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\properties_popup.py
# JUMLAH BARIS : 120
#######################################################################

import ttkbootstrap as ttk
from tkinter import Text, TclError, Listbox
from flowork_kernel.api_contract import EnumVarWrapper, IDynamicOutputSchema # (PENAMBAHAN) Import kontrak baru
from flowork_kernel.api_client import ApiClient
class PropertiesPopup(ttk.Toplevel):
    def __init__(self, parent_canvas_manager, node_id):
        super().__init__(parent_canvas_manager.coordinator_tab)
        self.canvas_manager = parent_canvas_manager
        self.parent_tab = parent_canvas_manager.coordinator_tab
        self.kernel = self.parent_tab.kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.node_id = node_id
        self.property_vars = {}
        self.dynamic_widgets = {}
        node_data = self.canvas_manager.canvas_nodes.get(self.node_id)
        if not node_data:
            self.destroy()
            return
        node_name = node_data.get('name', 'Unknown')
        self.title(f"{self.loc.get('properties_title')} - {node_name}")
        self.geometry("450x700")
        self.transient(self.parent_tab.winfo_toplevel())
        self.grab_set()
        self._create_widgets()
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(expand=True, fill="both")
        top_static_frame = ttk.Frame(main_frame)
        top_static_frame.pack(side="top", fill="x", expand=False)
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x", padx=15, pady=(5, 15))
        self.save_button = ttk.Button(button_frame, text=self.loc.get('save_changes_button'), command=self._save_changes, bootstyle="success.TButton")
        self.save_button.pack(side="right")
        ttk.Button(button_frame, text=self.loc.get('button_cancel', fallback="Cancel"), command=self.destroy, bootstyle="secondary.TButton").pack(side="right", padx=(0, 10))
        scroll_container = ttk.Frame(main_frame)
        scroll_container.pack(side="top", fill="both", expand=True, pady=(10,0))
        scroll_canvas = ttk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=scroll_canvas.yview)
        self.scrollable_frame = ttk.Frame(scroll_canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._populate_static_content(top_static_frame)
        self._populate_scrollable_content(self.scrollable_frame)
    def _populate_static_content(self, parent_frame):
        style = ttk.Style()
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {}
        style.configure('Readonly.TEntry', fieldbackground=colors.get('dark', '#333333'), insertwidth=0)
        style.map('Readonly.TEntry', foreground=[('readonly', colors.get('light', '#ffffff'))], fieldbackground=[('readonly', colors.get('dark', '#333333'))])
        id_input_frame = ttk.Frame(parent_frame)
        id_input_frame.pack(fill='x', expand=True)
        ttk.Label(id_input_frame, text=self.loc.get('node_id_label', fallback="Node ID:")).pack(fill='x', anchor='w')
        id_entry_frame = ttk.Frame(id_input_frame)
        id_entry_frame.pack(fill='x', expand=True, pady=(2,0))
        node_id_var = ttk.StringVar(value=self.node_id)
        id_entry = ttk.Entry(id_entry_frame, textvariable=node_id_var, state="readonly", style='Readonly.TEntry')
        id_entry.pack(side='left', fill='x', expand=True)
        copy_button = ttk.Button(id_entry_frame, text=self.loc.get('copy_id_button', fallback="Copy ID"), command=self._copy_node_id, style="info.Outline.TButton")
        copy_button.pack(side='left', padx=(5,0))
        ttk.Separator(parent_frame).pack(fill='x', pady=(15, 0))
    def _populate_scrollable_content(self, parent_frame):
        node_data = self.canvas_manager.canvas_nodes.get(self.node_id)
        ttk.Label(parent_frame, text=self.loc.get('module_name_label')).pack(fill='x', padx=5, pady=(5,0))
        self.property_vars['name'] = ttk.StringVar(value=node_data['name'])
        ttk.Entry(parent_frame, textvariable=self.property_vars['name']).pack(fill='x', padx=5, pady=(0, 10))
        ttk.Label(parent_frame, text=self.loc.get('description_label')).pack(fill='x', padx=5, pady=(5,0))
        desc_text = Text(parent_frame, height=3, font=("Helvetica", 9))
        desc_text.pack(fill='x', expand=True, padx=5, pady=(0, 10))
        desc_text.insert('1.0', node_data.get('description', ''))
        self.property_vars['description'] = desc_text
        ttk.Separator(parent_frame).pack(fill='x', pady=10, padx=5)
        module_manager = self.kernel.get_service("module_manager_service")
        module_instance = module_manager.get_instance(node_data['module_id']) if module_manager else None
        if module_instance and hasattr(module_instance, 'create_properties_ui'):
            get_current_config = lambda: self.canvas_manager.canvas_nodes.get(self.node_id, {}).get('config_values', {})
            available_vars_for_module = self._get_incoming_variables()
            returned_vars = module_instance.create_properties_ui(parent_frame, get_current_config, available_vars_for_module)
            if returned_vars: self.property_vars.update(returned_vars)
    def _get_incoming_variables(self):
        incoming_vars = {}
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager: return {}
        for conn in self.canvas_manager.canvas_connections.values():
            if conn['to'] == self.node_id:
                from_node_data = self.canvas_manager.canvas_nodes.get(conn['from'])
                if from_node_data:
                    from_module_id = from_node_data['module_id']
                    from_module_instance = module_manager.get_instance(from_module_id)
                    from_module_config = from_node_data.get('config_values', {})
                    if from_module_instance and isinstance(from_module_instance, IDynamicOutputSchema):
                        self.kernel.write_to_log(f"Fetching dynamic schema from '{from_module_id}'", "DEBUG")
                        dynamic_schema = from_module_instance.get_dynamic_output_schema(from_module_config)
                        for var_info in dynamic_schema:
                            incoming_vars[var_info['name']] = var_info.get('description', '')
                    from_node_manifest = module_manager.get_manifest(from_module_id)
                    if from_node_manifest and 'output_schema' in from_node_manifest:
                        for var_info in from_node_manifest['output_schema']:
                            if var_info['name'] not in incoming_vars: # (COMMENT) Avoid duplicates
                                incoming_vars[var_info['name']] = var_info.get('description', '')
        if 'data' not in incoming_vars: incoming_vars['data'] = "Main payload data (dictionary)."
        if 'history' not in incoming_vars: incoming_vars['history'] = "Payload history (list)."
        return {k: incoming_vars[k] for k in sorted(incoming_vars.keys())}
    def _copy_node_id(self):
        self.clipboard_clear()
        self.clipboard_append(self.node_id)
        self.kernel.write_to_log(f"Node ID '{self.node_id}' copied to clipboard.", "INFO")
    def _save_changes(self):
        self.canvas_manager.properties_manager.save_node_properties(self.node_id, self.property_vars, self)
        self.destroy()
