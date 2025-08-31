#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\base_component.py
# JUMLAH BARIS : 49
#######################################################################

from abc import ABC, abstractmethod
class BaseGeneratorComponent(ABC):
    """
    The abstract contract that all UI component definitions for the Generator must implement.
    Each component knows how to draw itself and generate its own code snippets.
    """
    def __init__(self, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
    @abstractmethod
    def get_toolbox_label(self) -> str:
        """Returns the text for the button in the toolbox."""
        pass
    @abstractmethod
    def get_component_type(self) -> str:
        """Returns the unique string identifier for this component type (e.g., 'text_input')."""
        pass
    @abstractmethod
    def create_canvas_widget(self, parent_frame, component_id, config):
        """Creates and returns the visual representation of the component on the design canvas."""
        pass
    @abstractmethod
    def create_properties_ui(self, parent_frame, config):
        """Creates the specific UI for the properties panel and returns a dict of tk.Vars."""
        pass
    @abstractmethod
    def generate_manifest_entry(self, config) -> dict:
        """Generates the dictionary entry for this property for the manifest.json file."""
        pass
    @abstractmethod
    def generate_processor_ui_code(self, config) -> list:
        """
        Generates a list of strings, where each string is a line of Python code
        for creating the properties UI in the final processor.py file.
        """
        pass
    def get_required_imports(self) -> set:
        """
        Returns a set of import strings required by this component.
        e.g., {"from tkinter import filedialog"}
        """
        return set()
