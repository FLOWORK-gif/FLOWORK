#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\textarea.py
# JUMLAH BARIS : 59
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext
from .base_component import BaseGeneratorComponent
class TextAreaComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_textarea', fallback="Text Area")
    def get_component_type(self) -> str:
        return 'textarea'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My Text Area")
        label = ttk.Label(parent_frame, text=label_text)
        label.pack(anchor='w')
        text_widget = scrolledtext.ScrolledText(parent_frame, height=3, font=("Helvetica", 9))
        text_widget.pack(fill='x')
        text_widget.insert('1.0', str(config.get('default', '')))
        text_widget.config(state='disabled')
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        default_text = scrolledtext.ScrolledText(parent_frame, height=4, font=("Helvetica", 9))
        default_text.insert('1.0', str(config.get('default', '')))
        prop_vars['default'] = default_text
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_default', fallback="Default Value:")).pack(fill='x', anchor='w')
        default_text.pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "textarea",
            "label": config['label'],
            "default": config['default']
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        return [
            f"        # --- {comp_label} ---",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\").pack(fill='x', padx=5, pady=(5,0))",
            f"        {comp_id}_widget = scrolledtext.ScrolledText(parent_frame, height=8, font=(\"Consolas\", 10))",
            f"        {comp_id}_widget.pack(fill=\"both\", expand=True, padx=5, pady=(0, 5))",
            f"        {comp_id}_widget.insert('1.0', config.get('{comp_id}', ''))",
            f"        property_vars['{comp_id}'] = {comp_id}_widget",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import scrolledtext, StringVar"}
