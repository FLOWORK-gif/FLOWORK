#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\text_input.py
# JUMLAH BARIS : 55
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from .base_component import BaseGeneratorComponent
class TextInputComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_text_input', fallback="Text Input")
    def get_component_type(self) -> str:
        return 'text_input'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My Text Input")
        label = ttk.Label(parent_frame, text=label_text)
        label.pack(anchor='w')
        ttk.Entry(parent_frame).pack(fill='x')
        return label # Return the primary widget for label updates
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        prop_vars['default'] = StringVar(value=config.get('default', ''))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_default', fallback="Default Value:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['default']).pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "string", # Text input produces a string
            "label": config['label'],
            "default": config['default']
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        return [
            f"        # --- {comp_label} ---",
            f"        property_vars['{comp_id}'] = StringVar(value=config.get('{comp_id}'))",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\").pack(fill='x', padx=5, pady=(5,0))",
            f"        ttk.Entry(parent_frame, textvariable=property_vars['{comp_id}']).pack(fill='x', padx=5, pady=(0, 5))",
            "" # Add a blank line for spacing
        ]
    def get_required_imports(self) -> set:
        """
        Declares that this component requires 'StringVar' from tkinter.
        """
        return {"from tkinter import StringVar"}
