#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\separator.py
# JUMLAH BARIS : 28
#######################################################################

import ttkbootstrap as ttk
from .base_component import BaseGeneratorComponent
class SeparatorComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_separator', fallback="Separator")
    def get_component_type(self) -> str:
        return 'separator'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label = ttk.Separator(parent_frame, orient='horizontal')
        label.pack(fill='x', pady=10, padx=5)
        return label
    def create_properties_ui(self, parent_frame, config):
        ttk.Label(parent_frame, text=self.loc.get('generator_no_props', fallback="No properties to configure."), bootstyle="secondary").pack(pady=10)
        return {} # No properties
    def generate_manifest_entry(self, config) -> dict:
        return None # Separator doesn't create a manifest property
    def generate_processor_ui_code(self, config) -> list:
        return [
            "        ttk.Separator(parent_frame).pack(fill='x', pady=10, padx=5)",
            ""
        ]
