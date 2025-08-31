#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\file_path.py
# JUMLAH BARIS : 61
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, filedialog
from .base_component import BaseGeneratorComponent
class FilePathComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_file_path', fallback="File/Folder Path")
    def get_component_type(self) -> str:
        return 'file_path'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My File Path")
        label = ttk.Label(parent_frame, text=label_text)
        label.pack(anchor='w')
        path_frame = ttk.Frame(parent_frame)
        path_frame.pack(fill='x')
        ttk.Entry(path_frame).pack(side='left', fill='x', expand=True)
        ttk.Button(path_frame, text="...").pack(side='left')
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        prop_vars['default'] = StringVar(value=config.get('default', ''))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_default', fallback="Default Path:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['default']).pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "filepath",
            "label": config['label'],
            "default": config['default']
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        return [
            f"        # --- {comp_label} ---",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\").pack(fill='x', padx=5, pady=(5,0))",
            f"        path_frame_{comp_id} = ttk.Frame(parent_frame)",
            f"        path_frame_{comp_id}.pack(fill='x', padx=5, pady=(0, 5))",
            f"        property_vars['{comp_id}'] = StringVar(value=config.get('{comp_id}'))",
            f"        ttk.Entry(path_frame_{comp_id}, textvariable=property_vars['{comp_id}']).pack(side='left', fill='x', expand=True)",
            f"        def _browse_{comp_id}():",
            f"            path = filedialog.askdirectory() # or askopenfilename()",
            f"            if path: property_vars['{comp_id}'].set(path)",
            f"        ttk.Button(path_frame_{comp_id}, text='...', command=_browse_{comp_id}, width=4).pack(side='left', padx=(5,0))",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import filedialog", "from tkinter import StringVar"}
