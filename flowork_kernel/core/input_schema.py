#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\core\input_schema.py
# (This is a new file to be created)
#######################################################################

from typing import Dict, Any

class InputVar:
    """Defines a single expected input variable for a module's payload."""
    def __init__(self, display_name: str, var_type: str, required: bool = False, description: str = ""):
        self.display_name = display_name
        self.var_type = var_type
        self.required = required
        self.description = description

class InputSchema:
    """Manages the collection of input variables for a module."""
    def __init__(self, variables: Dict[str, InputVar]):
        self.variables = variables

    def get_var(self, key: str, payload: Dict[str, Any]) -> Any:
        """Safely retrieves a variable's value from a payload."""
        # This is a simplified getter. A real implementation might use payload_helper.
        return payload.get('data', {}).get(key)

def create_input_schema(**kwargs: InputVar) -> InputSchema:
    """Factory function to easily create an InputSchema instance."""
    return InputSchema(kwargs)