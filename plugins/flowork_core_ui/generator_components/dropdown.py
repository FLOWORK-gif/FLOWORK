#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\dropdown.py
# JUMLAH BARIS : 60
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, Text
from .base_component import BaseGeneratorComponent
class DropdownComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_dropdown', fallback="Dropdown")
    def get_component_type(self) -> str:
        return 'dropdown'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My Dropdown")
        options = config.get('options', ['Option 1', 'Option 2'])
        label = ttk.Label(parent_frame, text=label_text)
        label.pack(anchor='w')
        ttk.Combobox(parent_frame, values=options).pack(fill='x')
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        prop_vars['default'] = StringVar(value=config.get('default', ''))
        options_text = Text(parent_frame, height=4, font=("Helvetica", 9))
        options_text.insert('1.0', "\n".join(config.get('options', [])))
        prop_vars['options'] = options_text
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_default', fallback="Default Value:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['default']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_options', fallback="Options (one per line):")).pack(fill='x', anchor='w')
        options_text.pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "enum",
            "label": config['label'],
            "default": config['default'],
            "options": config.get('options', [])
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        options = config.get('options', [])
        return [
            f"        # --- {comp_label} ---",
            f"        property_vars['{comp_id}'] = StringVar(value=config.get('{comp_id}'))",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\").pack(fill='x', padx=5, pady=(5,0))",
            f"        ttk.Combobox(parent_frame, textvariable=property_vars['{comp_id}'], values={options}, state='readonly').pack(fill='x', padx=5, pady=(0, 5))",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import StringVar, Text"}
