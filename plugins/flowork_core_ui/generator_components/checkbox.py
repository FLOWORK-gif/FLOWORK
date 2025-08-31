#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\checkbox.py
# JUMLAH BARIS : 52
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
from .base_component import BaseGeneratorComponent
class CheckboxComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_checkbox', fallback="Checkbox")
    def get_component_type(self) -> str:
        return 'checkbox'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My Checkbox")
        label = ttk.Checkbutton(parent_frame, text=label_text)
        label.pack(anchor='w')
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        default_value = config.get('default', False)
        if not isinstance(default_value, bool):
            default_value = str(default_value).lower() in ['true', '1', 'yes']
        prop_vars['default'] = BooleanVar(value=default_value)
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Checkbutton(parent_frame, text=self.loc.get('generator_comp_prop_checked_by_default', fallback="Checked by default?"), variable=prop_vars['default']).pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "boolean",
            "label": config['label'],
            "default": config.get('default', False)
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        return [
            f"        # --- {comp_label} ---",
            f"        property_vars['{comp_id}'] = BooleanVar(value=config.get('{comp_id}'))",
            f"        ttk.Checkbutton(parent_frame, text=\"{comp_label}\", variable=property_vars['{comp_id}']).pack(anchor='w', padx=5, pady=5)",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import BooleanVar, StringVar"}
