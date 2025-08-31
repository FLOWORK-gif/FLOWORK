#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\prompt_receiver_module\processor.py
# JUMLAH BARIS : 89
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI
from flowork_kernel.api_contract import IDataPreviewer
class PromptReceiverModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    Listens for a specific event containing a prompt and then triggers the
    workflow execution from this node onwards.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.parent_frame_for_clipboard = None
        self.node_instance_id = None
    def on_canvas_load(self, node_id: str):
        """
        Called by the CanvasManager right after this node is placed on the canvas.
        This is the perfect moment to start listening for events.
        """
        self.node_instance_id = node_id
        event_name = f"PROMPT_FROM_WIDGET_{self.node_instance_id}"
        subscriber_id = f"prompt_receiver_{self.node_instance_id}"
        self.event_bus.subscribe(
            event_name=event_name,
            subscriber_id=subscriber_id,
            callback=self._handle_prompt_event
        )
        self.logger(f"Receiver node '{self.node_instance_id}' is now listening for event '{event_name}'.", "SUCCESS")
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        """
        When this node is triggered, it simply passes the received payload
        to its output port to continue the flow.
        """
        self.node_instance_id = config.get('__internal_node_id', self.node_instance_id or self.module_id)
        status_updater(f"Passing data through...", "INFO")
        status_updater("Data received and passed.", "SUCCESS")
        return {"payload": payload, "output_name": "output"}
    def _handle_prompt_event(self, event_data):
        """
        This is the callback that gets triggered by the Event Bus.
        It starts the workflow execution from this node.
        """
        prompt = event_data.get("prompt")
        self.logger(f"Received prompt for node '{self.node_instance_id}': '{prompt[:50]}...'", "INFO")
        new_payload = {
            "data": {"prompt": prompt},
            "history": []
        }
        if self.kernel:
            self.kernel.trigger_workflow_from_node(self.node_instance_id, new_payload)
    def _copy_node_id_to_clipboard(self, node_id):
        """Copies the node ID to the clipboard."""
        if self.parent_frame_for_clipboard:
            self.parent_frame_for_clipboard.clipboard_clear()
            self.parent_frame_for_clipboard.clipboard_append(node_id)
            self.logger(f"Receiver ID '{node_id}' copied to clipboard.", "SUCCESS")
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        """Creates the UI for the properties popup."""
        config = get_current_config()
        self.parent_frame_for_clipboard = parent_frame
        node_id = self.node_instance_id
        info_frame = ttk.LabelFrame(parent_frame, text="Receiver Info", padding=10)
        info_frame.pack(fill='x', padx=5, pady=10)
        id_info_text = f"This node listens for prompts sent to its unique ID. Copy this ID and paste it into a 'Prompt Sender' widget.\n\nID: {node_id}"
        ttk.Label(info_frame, text=id_info_text, wraplength=350, justify="left").pack(anchor='w', fill='x', expand=True, pady=(0, 10))
        copy_button = ttk.Button(
            info_frame,
            text="Copy ID",
            command=lambda: self._copy_node_id_to_clipboard(node_id),
            bootstyle="info-outline"
        )
        copy_button.pack(anchor='e')
        return {}
    def get_data_preview(self, config: dict):
        """
        TODO: Implement the data preview logic for this module.
        This method should return a small, representative sample of the data
        that the 'execute' method would produce.
        It should run quickly and have no side effects.
        """
        self.logger(f"'get_data_preview' is not yet implemented for {self.module_id}", 'WARN')
        return [{'status': 'preview not implemented'}]
