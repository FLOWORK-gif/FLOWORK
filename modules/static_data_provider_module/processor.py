#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\static_data_provider_module\processor.py
# JUMLAH BARIS : 173
#######################################################################

from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import StringVar, Text, filedialog, scrolledtext
import json
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema, IDynamicPorts
from flowork_kernel.ui_shell import shared_properties
class StaticDataProviderModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema, IDynamicPorts):
    """
    Module to inject various static data types into a workflow.
    Serves as a powerful starting point or testing tool.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        status_updater("Injecting static data...", "INFO") # English Log
        variables_to_set = config.get('variables_to_set', [])
        output_data = {}
        log_message = "Injecting static data into payload:\n" # English Log
        if not variables_to_set:
            status_updater("No data configured to inject.", "INFO") # English Log
        else:
            for var_item in variables_to_set:
                var_name = var_item.get('name')
                var_value = var_item.get('value')
                if var_name:
                    output_data[var_name] = var_value
                    log_message += f"  - '{var_name}': '{str(var_value)[:100]}...'\n"
        if isinstance(payload, dict):
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data'].update(output_data)
        else:
            payload = {'data': output_data, 'history': []}
        self.logger(log_message, "DETAIL")
        status_updater("Data injected successfully.", "SUCCESS") # English Log
        return payload
    def get_dynamic_output_schema(self, config):
        schema = []
        variables = config.get('variables_to_set', [])
        for var in variables:
            var_name = var.get('name')
            if var_name:
                schema.append({
                    "name": f"data.{var_name}",
                    "type": "string",
                    "description": f"Static data for '{var_name}'."
                })
        return schema
    def get_dynamic_ports(self, config):
        ports = []
        variables = config.get('variables_to_set', [])
        for var in variables:
            var_name = var.get('name')
            if var_name:
                ports.append({
                    "name": var_name,
                    "display_name": var_name,
                    "tooltip": f"Outputs the entire payload, specifically for the '{var_name}' data path."
                })
        return ports
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        property_vars = {}
        current_config = get_current_config()
        type_options_map = {
            "type_text": "Text", "type_code": "Code", "type_image_path": "Image Path",
            "type_audio_path": "Audio Path", "type_video_path": "Video Path",
            "type_file_path": "File Path", "type_folder_path": "Folder Path"
        }
        display_to_internal_map = {self.loc.get(key): val for key, val in type_options_map.items()}
        internal_to_display_map = {val: self.loc.get(key) for key, val in type_options_map.items()}
        container = ttk.Frame(parent_frame)
        container.pack(fill='both', expand=True)
        header_frame = ttk.Frame(container)
        header_frame.pack(fill='x', padx=5)
        ttk.Label(header_frame, text=self.loc.get('prop_header_name'), width=20).pack(side='left', padx=(0, 5))
        ttk.Label(header_frame, text=self.loc.get('prop_header_type'), width=20).pack(side='left', padx=(0, 5))
        ttk.Label(header_frame, text=self.loc.get('prop_header_value')).pack(side='left', fill='x', expand=True)
        variable_list_frame = ttk.Frame(container)
        variable_list_frame.pack(fill='both', expand=True, padx=5, pady=(5,0))
        action_frame = ttk.Frame(container)
        action_frame.pack(fill='x', pady=(10, 5), padx=5)
        variable_rows = []
        def _add_variable_row(name="", value="", var_type="Text"):
            row_frame = ttk.Frame(variable_list_frame)
            row_frame.pack(fill='x', pady=3)
            name_var = StringVar(value=name)
            type_var = StringVar()
            ttk.Entry(row_frame, textvariable=name_var, width=20).pack(side='left', padx=(0, 5))
            type_display_options = list(display_to_internal_map.keys())
            type_combo = ttk.Combobox(row_frame, textvariable=type_var, values=type_display_options, state="readonly", width=18)
            type_combo.pack(side='left', padx=(0, 5))
            type_var.set(internal_to_display_map.get(var_type, self.loc.get("type_text")))
            value_frame = ttk.Frame(row_frame)
            value_frame.pack(side='left', fill='x', expand=True)
            row_data = {'name_var': name_var, 'type_var': type_var, 'frame': row_frame, 'value_widget': None}
            variable_rows.append(row_data)
            def _update_value_widget(*args):
                for widget in value_frame.winfo_children(): widget.destroy()
                selected_display_type = type_var.get()
                internal_type_key = display_to_internal_map.get(selected_display_type, "Text")
                widget = None
                if internal_type_key == 'Code':
                    widget = scrolledtext.ScrolledText(value_frame, height=4, font=("Consolas", 9))
                    widget.pack(fill='x', expand=True)
                    widget.insert('1.0', value)
                elif "Path" in internal_type_key:
                    path_var = StringVar(value=value)
                    entry_frame = ttk.Frame(value_frame)
                    entry_frame.pack(fill='x', expand=True)
                    ttk.Entry(entry_frame, textvariable=path_var).pack(side='left', fill='x', expand=True)
                    def _browse():
                        path = ""
                        if internal_type_key == 'Image Path': path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
                        elif internal_type_key == 'Audio Path': path = filedialog.askopenfilename(title="Select an Audio File", filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
                        elif internal_type_key == 'Video Path': path = filedialog.askopenfilename(title="Select a Video File", filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
                        elif internal_type_key == 'Folder Path': path = filedialog.askdirectory(title="Select a Folder")
                        else: path = filedialog.askopenfilename(title="Select a File")
                        if path: path_var.set(path)
                    ttk.Button(entry_frame, text=self.loc.get('prop_browse_button'), command=_browse, width=10).pack(side='left', padx=(5,0))
                    widget = path_var
                else: # Text
                    text_var = StringVar(value=value)
                    ttk.Entry(value_frame, textvariable=text_var).pack(fill='x', expand=True)
                    widget = text_var
                row_data['value_widget'] = widget
            type_var.trace_add('write', _update_value_widget)
            _update_value_widget()
            def _remove_row():
                row_frame.destroy()
                variable_rows.remove(row_data)
            delete_button = ttk.Button(row_frame, text="X", command=_remove_row, bootstyle="danger", width=2)
            delete_button.pack(side='right', padx=(5, 0))
        ttk.Button(action_frame, text=self.loc.get('prop_add_button'), command=_add_variable_row, bootstyle="outline-success").pack(fill='x')
        saved_variables = current_config.get('variables_to_set', [])
        if saved_variables:
            for var_item in saved_variables:
                _add_variable_row(var_item.get('name', ''), var_item.get('value', ''), var_item.get('type', 'Text'))
        else:
             _add_variable_row("prompt", "A cinematic photo of a raccoon astronaut, 8k", "Text")
        class DynamicVariables:
            def get(self):
                vars_list = []
                for row in variable_rows:
                    if not row['frame'].winfo_exists(): continue
                    name = row['name_var'].get().strip()
                    display_type = row['type_var'].get()
                    internal_type = display_to_internal_map.get(display_type, "Text")
                    value = ""
                    widget = row['value_widget']
                    if widget:
                        try:
                            if isinstance(widget, (Text, scrolledtext.ScrolledText)): value = widget.get("1.0", "end-1c")
                            elif hasattr(widget, 'get'): value = widget.get()
                        except Exception: pass
                    if name:
                        vars_list.append({'name': name, 'value': value, 'type': internal_type})
                return vars_list
        property_vars['variables_to_set'] = DynamicVariables()
        return property_vars
    def get_data_preview(self, config: dict):
        variables_to_set = config.get('variables_to_set', [])
        preview_data = {var.get('name'): var.get('value') for var in variables_to_set if var.get('name')}
        return preview_data
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
