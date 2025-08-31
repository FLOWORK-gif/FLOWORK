#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_components\properties_manager.py
# JUMLAH BARIS : 84
#######################################################################

import json
from tkinter import messagebox, Text, TclError, Listbox
from tkinter import scrolledtext
from flowork_kernel.api_contract import EnumVarWrapper
from ..properties_popup import PropertiesPopup
class PropertiesManager:
    """
    Handles all logic related to the Node Properties window, including opening, validating, and saving data.
    (FIXED V2) Now safely handles nodes without a 'main_label' widget.
    """
    def __init__(self, canvas_manager, kernel):
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
    def open_properties_popup(self, node_id):
        """Opens a Toplevel window for node properties."""
        if node_id in self.canvas_manager.canvas_nodes:
            PropertiesPopup(self.canvas_manager, node_id)
    def save_node_properties(self, node_id, property_vars, popup_window):
        """
        Saves data from the properties popup to the node's state after validation.
        """
        canvas_nodes = self.canvas_manager.canvas_nodes
        if node_id not in canvas_nodes:
            return
        node_data = canvas_nodes[node_id]
        old_name = node_data.get('name', node_id)
        new_name = property_vars.get('name').get() if 'name' in property_vars else old_name
        new_description = ""
        new_config_values = {}
        for key, var_obj in property_vars.items():
            try:
                value_to_save = None
                if isinstance(var_obj, (Text, scrolledtext.ScrolledText)):
                    value_to_save = var_obj.get('1.0', 'end-1c').strip()
                elif isinstance(var_obj, (Listbox, EnumVarWrapper)):
                    value_to_save = var_obj.get()
                elif hasattr(var_obj, 'get'):
                    value_to_save = var_obj.get()
                else:
                    continue
                if key == 'description':
                    new_description = value_to_save
                elif key == 'name':
                    pass
                else:
                    new_config_values[key] = value_to_save
            except (TclError, AttributeError) as e:
                pass # (COMMENT) It's better to ignore this minor error
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager: return
        module_instance = module_manager.get_instance(node_data.get("module_id"))
        if module_instance and hasattr(module_instance, 'validate'):
            connected_inputs = [
                conn['source_port_name']
                for conn in self.canvas_manager.canvas_connections.values()
                if conn.get('to') == node_id
            ]
            is_valid, error_message = module_instance.validate(new_config_values, connected_inputs)
            if not is_valid:
                messagebox.showerror(
                    self.loc.get('error_title', fallback="Configuration Error"),
                    error_message,
                    parent=popup_window
                )
                return
        node_data['name'] = new_name
        node_data['description'] = new_description
        node_data["config_values"] = new_config_values
        main_label_widget = node_data.get('main_label')
        if main_label_widget and main_label_widget.winfo_exists():
            main_label_widget.config(text=new_name)
        if node_id in self.canvas_manager.tooltips:
            self.canvas_manager.tooltips[node_id].update_text(new_description)
        self.kernel.write_to_log(f"Properties for node '{new_name}' were updated.", "SUCCESS")
        self.canvas_manager.node_manager.update_node_ports(node_id)
        self.canvas_manager.node_manager.update_node_visual_info(node_id)
