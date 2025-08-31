#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\set_variable_module\processor.py
# JUMLAH BARIS : 150
#######################################################################

from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
import ttkbootstrap as ttk
from tkinter import StringVar, Text, filedialog
import json
class SetVariableModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    Module to set initial values or modify multiple variables in a single step.
    [UPGRADED] Now supports variable types and a file/folder browser in its properties UI.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        status_updater("Setting dynamic variables...", "INFO")
        variables_to_set = config.get('variables', [])
        output_data = {}
        log_message = "New data set in payload:\n"
        if not variables_to_set:
            status_updater("No variables configured to set.", "INFO")
        else:
            for var_item in variables_to_set:
                var_name = var_item.get('name')
                var_value = var_item.get('value')
                if var_name:
                    output_data[var_name] = var_value
                    log_message += f"  - '{var_name}': '{str(var_value)[:100]}...'\n" # Log truncated value
        if isinstance(payload, dict):
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data'].update(output_data)
        else:
            payload = {'data': output_data, 'history': []}
        if hasattr(self, 'logger'):
            self.logger(log_message, "DETAIL")
        status_updater("Variables set successfully.", "SUCCESS")
        if mode == 'EXECUTE' and hasattr(self, 'event_bus'):
            self.publish_event("START_NODE_EXECUTED", output_data)
        return {"payload": payload, "output_name": "success"}
    def get_dynamic_output_schema(self, config):
        schema = []
        variables = config.get('variables', [])
        for var in variables:
            var_name = var.get('name')
            if var_name:
                schema.append({
                    "name": f"data.{var_name}",
                    "type": var.get('type', 'string'),
                    "description": f"Dynamic output '{var_name}' from START node."
                })
        return schema
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        property_vars = {}
        current_config = get_current_config()
        container = ttk.Frame(parent_frame)
        container.pack(fill='both', expand=True)
        header_frame = ttk.Frame(container)
        header_frame.pack(fill='x', padx=5)
        ttk.Label(header_frame, text="Variable Name", width=15).pack(side='left', padx=(0, 5))
        ttk.Label(header_frame, text="Type", width=10).pack(side='left', padx=(0, 5))
        ttk.Label(header_frame, text="Value").pack(side='left', fill='x', expand=True)
        variable_list_frame = ttk.Frame(container)
        variable_list_frame.pack(fill='both', expand=True, padx=5, pady=(5,0))
        action_frame = ttk.Frame(container)
        action_frame.pack(fill='x', pady=(10, 5), padx=5)
        variable_rows = []
        def _add_variable_row(name="", value="", var_type="text"):
            row_frame = ttk.Frame(variable_list_frame)
            row_frame.pack(fill='x', pady=3)
            name_var = StringVar(value=name)
            value_var = StringVar(value=value)
            type_var = StringVar(value=var_type)
            ttk.Entry(row_frame, textvariable=name_var, width=15).pack(side='left', padx=(0, 5))
            type_combo = ttk.Combobox(row_frame, textvariable=type_var, values=['text', 'textarea', 'file', 'folder'], state='readonly', width=8)
            type_combo.pack(side='left', padx=(0, 5))
            value_frame = ttk.Frame(row_frame)
            value_frame.pack(side='left', fill='x', expand=True)
            def _remove_row():
                row_to_remove = next((row for row in variable_rows if row['frame'] == row_frame), None)
                if row_to_remove:
                    row_frame.destroy()
                    variable_rows.remove(row_to_remove)
            delete_button = ttk.Button(row_frame, text="X", command=_remove_row, bootstyle="danger", width=2)
            delete_button.pack(side='right', padx=(5, 0))
            row_data = {'name': name_var, 'value': value_var, 'type': type_var, 'frame': row_frame, 'value_widget': None}
            variable_rows.append(row_data)
            def _update_value_widget(*args):
                for widget in value_frame.winfo_children():
                    widget.destroy()
                new_type = type_var.get()
                if new_type == 'textarea':
                    text_widget = Text(value_frame, height=3, font=("Helvetica", 9))
                    text_widget.pack(fill='x', expand=True)
                    text_widget.insert('1.0', value_var.get())
                    row_data['value_widget'] = text_widget
                elif new_type in ['file', 'folder']:
                    entry_widget = ttk.Entry(value_frame, textvariable=value_var)
                    entry_widget.pack(side='left', fill='x', expand=True)
                    def _browse():
                        path = ""
                        if new_type == 'file':
                            path = filedialog.askopenfilename(title="Select a file")
                        else: # folder
                            path = filedialog.askdirectory(title="Select a folder")
                        if path:
                            value_var.set(path)
                    browse_button = ttk.Button(value_frame, text="Browse...", command=_browse, width=10)
                    browse_button.pack(side='left', padx=(5,0))
                    row_data['value_widget'] = value_var
                else: # text
                    entry_widget = ttk.Entry(value_frame, textvariable=value_var)
                    entry_widget.pack(fill='x', expand=True)
                    row_data['value_widget'] = value_var
            type_var.trace_add('write', _update_value_widget)
            _update_value_widget()
        ttk.Button(action_frame, text="Add Variable", command=_add_variable_row, bootstyle="outline-success").pack(fill='x')
        saved_variables = current_config.get('variables', [])
        if saved_variables:
            for var_item in saved_variables:
                _add_variable_row(var_item.get('name', ''), var_item.get('value', ''), var_item.get('type', 'text'))
        else:
             _add_variable_row("prompt", "Write your initial prompt here", "text")
        class DynamicVariables:
            def get(self):
                vars_list = []
                for row in variable_rows:
                    if not row['frame'].winfo_exists(): continue
                    name = row['name'].get().strip()
                    var_type = row['type'].get()
                    value = ""
                    if var_type == 'textarea':
                        if row['value_widget'] and row['value_widget'].winfo_exists():
                            value = row['value_widget'].get("1.0", "end-1c")
                    else: # text, file, folder all use a StringVar
                        value = row['value'].get()
                    if name:
                        vars_list.append({'name': name, 'value': value, 'type': var_type})
                return vars_list
        property_vars['variables'] = DynamicVariables()
        return property_vars
    def get_data_preview(self, config: dict):
        variables_to_set = config.get('variables', [])
        preview_data = {var.get('name'): var.get('value') for var in variables_to_set if var.get('name')}
        return preview_data
