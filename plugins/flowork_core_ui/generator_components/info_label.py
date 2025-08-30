#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\info_label.py
# JUMLAH BARIS : 37
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from .base_component import BaseGeneratorComponent
class InfoLabelComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_info_label', fallback="Info Label")
    def get_component_type(self) -> str:
        return 'info_label'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "This is an informational message.")
        label = ttk.Label(parent_frame, text=label_text, bootstyle="secondary", wraplength=200)
        label.pack(anchor='w', pady=5)
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_info_text', fallback="Informational Text:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return None # InfoLabel doesn't create a manifest property
    def generate_processor_ui_code(self, config) -> list:
        comp_label = config['label']
        return [
            f"        # --- Info Label ---",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\", wraplength=400, justify='left', bootstyle='secondary').pack(fill='x', padx=5, pady=5)",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import StringVar"}
