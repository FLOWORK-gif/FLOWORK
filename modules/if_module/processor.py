#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\if_module\processor.py
# JUMLAH BARIS : 94
#######################################################################

from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.ui_shell.shared_properties import create_debug_and_reliability_ui, create_loop_settings_ui
from flowork_kernel.api_contract import EnumVarWrapper
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
from flowork_kernel.ui_shell.components.PropertyField import PropertyField
from flowork_kernel.ui_shell.components.InfoLabel import InfoLabel
from flowork_kernel.ui_shell.components.Separator import Separator
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.utils.condition_evaluator import evaluate_condition
class IfModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        variable_path = config.get("variable_to_check", "")
        operator = config.get("comparison_operator", "==")
        compare_value_str = str(config.get("value_to_compare", ""))
        actual_value = get_nested_value(payload, variable_path)
        if actual_value is None:
            status_updater(self.loc.get("if_module_status_var_not_found", variable_path=variable_path, fallback=f"Variable '{variable_path}' not found."), "ERROR")
            return {"payload": payload, "output_name": "false"}
        condition_met = evaluate_condition(actual_value, operator, compare_value_str)
        status_updater(self.loc.get("if_module_status_result", condition_met=condition_met, fallback=f"Result: {condition_met}"), "INFO")
        return {"payload": payload, "output_name": "true" if condition_met else "false"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        property_vars = {}
        current_config = get_current_config()
        if not available_vars:
            InfoLabel(
                parent=parent_frame,
                text=self.loc.get("if_module_needs_connection_info", fallback="THIS MODULE NEEDS TO BE CONNECTED:\nPlease connect an input from another node to automatically detect variables.")
            )
        else:
            property_vars['variable_to_check'] = StringVar(value=current_config.get('variable_to_check', ''))
            LabelledCombobox(
                parent=parent_frame,
                label_text=self.loc.get('prop_if_variable_label', fallback="Variable to Check:"),
                variable=property_vars['variable_to_check'],
                values=list(available_vars.keys())
            )
            OPERATOR_MAP = [
                {"label": self.loc.get("operator_equals_full", fallback="Equals (==)"), "value": "=="},
                {"label": self.loc.get("operator_not_equals_full", fallback="Not Equals (!=)"), "value": "!="},
                {"label": self.loc.get("operator_contains_text", fallback="Contains Text"), "value": "contains"},
                {"label": self.loc.get("operator_not_contains_text", fallback="Does Not Contain Text"), "value": "not contains"},
                {"label": self.loc.get("operator_greater_than_full", fallback="Greater Than (>)"), "value": ">"},
                {"label": self.loc.get("operator_less_than_full", fallback="Less Than (<)"), "value": "<"},
                {"label": self.loc.get("operator_greater_than_or_equals_full", fallback="Greater / Equal (>=)"), "value": ">="},
                {"label": self.loc.get("operator_less_than_or_equals_full", fallback="Less / Equal (<=)"), "value": "<="},
                {"label": self.loc.get("operator_starts_with", fallback="Starts With"), "value": "starts_with"},
                {"label": self.loc.get("operator_ends_with", fallback="Ends With"), "value": "ends_with"},
                {"label": self.loc.get("operator_is_empty", fallback="Is Empty"), "value": "is empty"},
                {"label": self.loc.get("operator_is_not_empty", fallback="Is Not Empty"), "value": "is not empty"},
                {"label": self.loc.get("operator_is_number", fallback="Is Number"), "value": "is number"},
                {"label": self.loc.get("operator_is_not_number", fallback="Is Not Number"), "value": "is not number"}
            ]
            label_to_value = {item['label']: item['value'] for item in OPERATOR_MAP}
            value_to_label = {item['value']: item['label'] for item in OPERATOR_MAP}
            operator_string_var = StringVar()
            operator_wrapper = EnumVarWrapper(operator_string_var, label_to_value, value_to_label)
            operator_wrapper.set(current_config.get('comparison_operator', '=='))
            property_vars['comparison_operator'] = operator_wrapper
            LabelledCombobox(
                parent=parent_frame,
                label_text=self.loc.get('prop_if_operator_label', fallback="Comparison Operator:"),
                variable=operator_string_var,
                values=list(label_to_value.keys())
            )
            property_vars['value_to_compare'] = StringVar(value=current_config.get('value_to_compare', ''))
            PropertyField(
                parent=parent_frame,
                label_text=self.loc.get('prop_if_value_label', fallback="Comparison Value:"),
                variable=property_vars['value_to_compare']
            )
        Separator(parent=parent_frame)
        debug_vars = create_debug_and_reliability_ui(parent_frame, current_config, self.loc)
        property_vars.update(debug_vars)
        loop_vars = create_loop_settings_ui(parent_frame, current_config, self.loc, available_vars)
        property_vars.update(loop_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        """
        Provides a sample of what this module might output for the Data Canvas.
        """
        return [{'status': 'condition_check', 'outcome': 'true/false'}]
