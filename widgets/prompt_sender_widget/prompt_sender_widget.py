#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\widgets\prompt_sender_widget\prompt_sender_widget.py
# JUMLAH BARIS : 52
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext, messagebox
from flowork_kernel.api_contract import BaseDashboardWidget
class PromptSenderWidget(BaseDashboardWidget):
    """
    A UI widget to send a text prompt to a specific 'Prompt Receiver' node on the canvas.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str, **kwargs):
        super().__init__(parent, coordinator_tab, kernel, widget_id, **kwargs)
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)
        self.target_node_id_var = StringVar(value="receiver-node-1")
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(id_frame, text=self.loc.get('prompt_sender_target_id_label', fallback="Target Node ID:")).pack(side="left")
        id_entry = ttk.Entry(id_frame, textvariable=self.target_node_id_var)
        id_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.prompt_text = scrolledtext.ScrolledText(main_frame, height=4, wrap="word", font=("Segoe UI", 10))
        self.prompt_text.pack(fill="both", expand=True, pady=(0, 5))
        send_button = ttk.Button(
            main_frame,
            text=self.loc.get('prompt_sender_send_button', fallback="Send Prompt"),
            command=self._send_prompt,
            bootstyle="primary"
        )
        send_button.pack(fill="x")
    def _send_prompt(self):
        target_node_id = self.target_node_id_var.get().strip()
        prompt_content = self.prompt_text.get("1.0", "end-1c").strip()
        if not target_node_id or not prompt_content:
            messagebox.showwarning(
                self.loc.get('prompt_sender_warning_title', fallback="Input Required"),
                self.loc.get('prompt_sender_warning_message', fallback="Please provide both a target node ID and a prompt.")
            )
            return
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_name = f"PROMPT_FROM_WIDGET_{target_node_id}"
            event_data = {
                "prompt": prompt_content,
                "sender_widget_id": self.widget_id
            }
            event_bus.publish(event_name, event_data, publisher_id=self.widget_id)
            self.kernel.write_to_log(f"Prompt sent to event '{event_name}'.", "SUCCESS")
            self.prompt_text.delete("1.0", "end")
