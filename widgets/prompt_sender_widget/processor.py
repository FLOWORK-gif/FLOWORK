#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\widgets\prompt_sender_widget\processor.py
# JUMLAH BARIS : 81
#######################################################################

from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext, messagebox, filedialog
import os
from flowork_kernel.api_contract import BaseDashboardWidget
class PromptSenderWidget(BaseDashboardWidget):
    """
    A UI widget to send a text prompt and an optional file path to a specific 'Prompt Receiver' node on the canvas.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str, **kwargs):
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id, **kwargs)
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)
        self.target_node_id_var = StringVar(value="receiver-node-1")
        self.file_path_var = StringVar()
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(id_frame, text=self.loc.get('prompt_sender_target_id_label', fallback="Target Node ID:")).pack(side="left")
        id_entry = ttk.Entry(id_frame, textvariable=self.target_node_id_var)
        id_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(file_frame, text=self.loc.get('prompt_sender_attachment_label', fallback="File Attachment:")).pack(side="left") # ENGLISH HARDCODE
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        browse_button = ttk.Button(file_frame, text=self.loc.get('prompt_sender_browse_button', fallback="Browse..."), command=self._browse_for_file) # ENGLISH HARDCODE
        browse_button.pack(side="left")
        self.prompt_text = scrolledtext.ScrolledText(main_frame, height=4, wrap="word", font=("Segoe UI", 10))
        self.prompt_text.pack(fill="both", expand=True, pady=(0, 5))
        send_button = ttk.Button(
            main_frame,
            text=self.loc.get('prompt_sender_send_button', fallback="Send Prompt"),
            command=self._send_prompt,
            bootstyle="primary"
        )
        send_button.pack(fill="x")
    def _browse_for_file(self):
        """Opens a file dialog for the user to select any file."""
        filepath = filedialog.askopenfilename(
            title=self.loc.get('prompt_sender_browse_title', fallback="Select a File to Send"), # ADDED: Localization
            filetypes=[("All files", "*.*")]
        )
        if filepath:
            self.file_path_var.set(filepath)
    def _send_prompt(self):
        target_node_id = self.target_node_id_var.get().strip()
        prompt_content = self.prompt_text.get("1.0", "end-1c").strip()
        file_path = self.file_path_var.get().strip()
        if not target_node_id:
            messagebox.showwarning(
                self.loc.get('prompt_sender_warning_title', fallback="Input Required"),
                self.loc.get('prompt_sender_warning_message_no_id', fallback="Please provide a target node ID.")
            )
            return
        if not prompt_content and not file_path:
             messagebox.showwarning(
                self.loc.get('prompt_sender_warning_title', fallback="Input Required"),
                self.loc.get('prompt_sender_warning_message_no_content', fallback="Please provide a prompt or select a file to send.")
            )
             return
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_name = f"PROMPT_FROM_WIDGET_{target_node_id}"
            event_data = {
                "prompt": prompt_content,
                "file_path": file_path,
                "sender_widget_id": self.widget_id
            }
            event_bus.publish(event_name, event_data, publisher_id=self.widget_id)
            self.kernel.write_to_log(f"Prompt and file path sent to event '{event_name}'.", "SUCCESS")
            self.prompt_text.delete("1.0", "end")
            self.file_path_var.set("")
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
