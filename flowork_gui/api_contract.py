#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\api_contract.py
# JUMLAH BARIS : 93
#######################################################################

import ttkbootstrap as ttk
from typing import Dict, Any, List
from tkinter import StringVar
from abc import ABC, abstractmethod
class FloworkException(Exception):
    """Base exception for all custom errors in the application."""
    pass
class PermissionDeniedError(FloworkException):
    """Raised when an action is attempted without the required license tier or permission."""
    pass
class BaseDashboardWidget(ttk.Frame):
    """
    Client-side base class for all dashboard widgets.
    Provides a consistent structure and initialization.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.coordinator_tab = coordinator_tab
        self.kernel = kernel
        self.loc = self.kernel.loc
        self.api_client = self.kernel.api_client
        self.widget_id = widget_id
    def on_widget_load(self):
        """Called by DashboardManager when the widget is created and displayed."""
        pass
    def on_widget_destroy(self):
        """Called by DashboardManager just before the widget is destroyed."""
        pass
    def refresh_content(self):
        """Called when a global UI refresh is requested."""
        pass
class IDataPreviewer(ABC):
    """
    An optional interface for modules that can provide a real-time preview
    of their potential output data based on their current configuration.
    This is the foundation for the "Data Canvas" feature.
    """
    @abstractmethod
    def get_data_preview(self, config: Dict[str, Any]) -> Any:
        """
        Executes a limited, sample version of the module's logic to return a data preview.
        This method MUST NOT have side effects and should return quickly.
        Args:
            config: The current configuration values from the properties UI.
        Returns:
            A sample of the data the module would produce (e.g., a list of dicts, a string).
        """
        raise NotImplementedError
class LoopConfig:
    """
    Data structure for defining looping configuration for a step.
    This is used within module properties or as part of the node data.
    """
    LOOP_TYPE_COUNT = "count"
    LOOP_TYPE_CONDITION = "condition"
    def __init__(self, loop_type: str = LOOP_TYPE_COUNT, iterations: int = 1, condition_var: str = None, condition_op: str = None, condition_val: Any = None,
                 enable_sleep: bool = False, sleep_type: str = "static", static_duration: int = 1, random_min: int = 1, random_max: int = 5):
        self.loop_type = loop_type
        self.iterations = iterations
        self.condition_var = condition_var
        self.condition_op = condition_op
        self.condition_val = condition_val
        self.enable_sleep = enable_sleep
        self.sleep_type = sleep_type
        self.static_duration = static_duration
        self.random_min = random_min
        self.random_max = random_max
class EnumVarWrapper:
    """
    Wrapper for a StringVar that handles conversion between UI labels (which are localized)
    and internal values for enum-type properties.
    """
    def __init__(self, string_var: StringVar, label_to_value_map: Dict[str, str], value_to_label_map: Dict[str, str]):
        self.sv = string_var
        self.label_to_value_map = label_to_value_map
        self.value_to_label_map = value_to_label_map
    def get(self):
        """Returns the actual internal value."""
        return self.label_to_value_map.get(self.sv.get(), self.sv.get())
    def set(self, value):
        """Sets the StringVar based on the provided internal value."""
        self.sv.set(self.value_to_label_map.get(value, value))
    def trace_add(self, mode, callback):
        """Passes the trace call to the underlying StringVar."""
        self.sv.trace_add(mode, callback)
