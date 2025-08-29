#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\text_to_json_converter_module\processor.py
# JUMLAH BARIS : 95
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
class TextToJsonConverterModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    Module to convert a delimited text string into a structured list of JSON objects.
    [FIXED V2] Correctly handles single-column data where value_delimiter is not present.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        source_variable = config.get('source_text_variable')
        line_delimiter = config.get('line_delimiter', '\\n').replace('\\n', '\n')
        value_delimiter = config.get('value_delimiter', ',')
        key_names_str = config.get('key_names', '')
        if not all([source_variable, line_delimiter, key_names_str]):
            raise ValueError("Configuration for Source, Line Delimiter, and Key Names is required.")
        source_text = get_nested_value(payload, source_variable)
        if not source_text or not isinstance(source_text, str):
            raise ValueError(f"Source text not found or is not a string at payload path: '{source_variable}'")
        status_updater("Converting text to JSON...", "INFO")
        try:
            keys = [key.strip() for key in key_names_str.split(',') if key.strip()]
            lines = [line.strip() for line in source_text.strip().split(line_delimiter)]
            json_list = []
            for line in lines:
                if not line:
                    continue
                if len(keys) == 1:
                    values = [line]
                else:
                    values = [val.strip() for val in line.split(value_delimiter)]
                record = dict(zip(keys, values))
                json_list.append(record)
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data']['json_data'] = json_list
            status_updater(f"Successfully converted {len(json_list)} records.", "SUCCESS")
            self.logger(f"Converted text to JSON with {len(json_list)} records. Sample: {json_list[0] if json_list else '[]'}", "INFO")
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            self.logger(f"Failed to convert text to JSON: {e}", "ERROR")
            status_updater(f"Error: {e}", "ERROR")
            payload['error'] = str(e)
            return {"payload": payload, "output_name": "error"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        input_frame = ttk.LabelFrame(parent_frame, text="Input Configuration")
        input_frame.pack(fill='x', padx=5, pady=5, expand=True)
        property_vars['source_text_variable'] = StringVar(value=config.get('source_text_variable', 'data.raw_text'))
        LabelledCombobox(
            parent=input_frame,
            label_text=self.loc.get('prop_source_text_label', fallback="Source Text Variable:"),
            variable=property_vars['source_text_variable'],
            values=list(available_vars.keys())
        )
        delimiter_frame = ttk.LabelFrame(parent_frame, text="Delimiter Settings")
        delimiter_frame.pack(fill='x', padx=5, pady=5, expand=True)
        ttk.Label(delimiter_frame, text=self.loc.get('prop_line_delimiter_label', fallback="Line Delimiter:")).pack(fill='x', padx=5, pady=(5,0))
        property_vars['line_delimiter'] = StringVar(value=config.get('line_delimiter', '\\n'))
        ttk.Entry(delimiter_frame, textvariable=property_vars['line_delimiter']).pack(fill='x', padx=5, pady=(0, 5))
        ttk.Label(delimiter_frame, text=self.loc.get('prop_value_delimiter_label', fallback="Value Delimiter:")).pack(fill='x', padx=5, pady=(5,0))
        property_vars['value_delimiter'] = StringVar(value=config.get('value_delimiter', ','))
        ttk.Entry(delimiter_frame, textvariable=property_vars['value_delimiter']).pack(fill='x', padx=5, pady=(0, 5))
        keys_frame = ttk.LabelFrame(parent_frame, text="JSON Structure")
        keys_frame.pack(fill='x', padx=5, pady=5, expand=True)
        ttk.Label(keys_frame, text=self.loc.get('prop_key_names_label', fallback="Key Names (comma-separated):")).pack(fill='x', padx=5, pady=(5,0))
        property_vars['key_names'] = StringVar(value=config.get('key_names', 'column1,column2'))
        ttk.Entry(keys_frame, textvariable=property_vars['key_names']).pack(fill='x', padx=5, pady=(0, 5))
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_dynamic_output_schema(self, config):
        return [
            {
                "name": "data.json_data",
                "type": "list",
                "description": "The resulting list of JSON objects after conversion."
            }
        ]
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Data conversion depends on dynamic input from payload.'}]
