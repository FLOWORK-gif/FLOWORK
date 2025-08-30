#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\email_sender_tools\processor.py
# JUMLAH BARIS : 136
#######################################################################

import smtplib
import os
import tempfile
import re # (ADDED) Import regex for placeholder matching
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
class EmailSenderModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    (REMASTERED V6) Sends an email based on explicit instructions from the payload,
    and can now resolve payload variables within attachment content for maximum efficiency.
    """
    TIER = "basic"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.variable_manager = self.kernel.get_service("variable_manager")
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not self.variable_manager:
            raise RuntimeError("VariableManager service is not available.")
        smtp_host = self.variable_manager.get_variable("SMTP_HOST")
        smtp_port = self.variable_manager.get_variable("SMTP_PORT")
        email_address = self.variable_manager.get_variable("EMAIL_ADDRESS")
        email_password = self.variable_manager.get_variable("EMAIL_PASSWORD")
        if not all([smtp_host, smtp_port, email_address, email_password]):
            raise ValueError("SMTP credentials are not fully configured in Settings -> Variable Management.")
        try:
            smtp_port = int(smtp_port)
        except (ValueError, TypeError):
            raise ValueError("SMTP_PORT must be a valid number.")
        payload_data = payload.get('data', {})
        recipient_to = payload_data.get('recipient_to') or config.get('recipient_to')
        subject = payload_data.get('subject') or config.get('subject')
        body = payload_data.get('body') or config.get('body')
        if not recipient_to or not subject or not body:
            raise ValueError("Required fields (recipient, subject, body) are empty in both payload and config.")
        status_updater(f"Preparing to send email to {recipient_to}...", "INFO")
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = recipient_to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        attachments = payload_data.get('attachments', [])
        if isinstance(attachments, list):
            for item in attachments:
                if isinstance(item, str) and os.path.isfile(item):
                    self._attach_file(msg, item)
                    status_updater(f"Attaching file: {os.path.basename(item)}", "INFO")
                elif isinstance(item, dict) and 'filename' in item and 'content' in item:
                    content_value = item.get('content', '')
                    placeholder_match = re.match(r"\{\{([\w\.]+)\}\}", str(content_value))
                    if placeholder_match:
                        variable_path = placeholder_match.group(1)
                        self.logger(f"Found payload variable '{variable_path}' in attachment content.", "DEBUG")
                        content_from_payload = get_nested_value(payload, variable_path)
                        if content_from_payload:
                            self._create_and_attach_temp_file(msg, item['filename'], str(content_from_payload))
                            status_updater(f"Creating and attaching '{item['filename']}' from payload.", "INFO")
                        else:
                             self.logger(f"Variable '{variable_path}' not found in payload. Skipping attachment.", "WARN")
                    elif content_value: # (MODIFIED) Check if content is not empty
                        self._create_and_attach_temp_file(msg, item['filename'], str(content_value))
                        status_updater(f"Creating and attaching: {item['filename']}", "INFO")
                    else:
                        self.logger(f"Skipping attachment '{item['filename']}' because its content is empty.", "WARN")
                else:
                    self.logger(f"Could not process attachment item: {item}. It is not a valid path or a valid content object.", "WARN")
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(email_address, email_password)
                server.send_message(msg)
            status_updater("Email sent successfully.", "SUCCESS")
            self.logger(f"Email successfully sent to {recipient_to}", "SUCCESS")
            if 'data' not in payload: payload['data'] = {}
            payload['data']['email_status'] = 'Sent successfully'
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            error_msg = f"Failed to send email: {e}"
            self.logger(error_msg, "ERROR")
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
    def _attach_file(self, msg, file_path):
        try:
            with open(file_path, "rb") as attachment_file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(file_path)}",
            )
            msg.attach(part)
            self.logger(f"Successfully attached file: {os.path.basename(file_path)}", "INFO")
        except Exception as e:
            self.logger(f"Could not attach file '{file_path}': {e}", "WARN")
    def _create_and_attach_temp_file(self, msg, filename, content):
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=f"_{filename}", encoding='utf-8') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            self._attach_file(msg, tmp_path)
            os.unlink(tmp_path)
        except Exception as e:
            self.logger(f"Could not create or attach temporary file '{filename}': {e}", "ERROR")
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        main_frame = ttk.LabelFrame(parent_frame, text="Email Details (Fallbacks for Agent)")
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        ttk.Label(main_frame, text=self.loc.get('prop_recipient_manual_label')).pack(anchor='w', padx=5)
        property_vars['recipient_to'] = StringVar(value=config.get('recipient_to', ''))
        ttk.Entry(main_frame, textvariable=property_vars['recipient_to']).pack(fill='x', padx=5, pady=(0, 5))
        ttk.Label(main_frame, text=self.loc.get('prop_subject_manual_label')).pack(anchor='w', padx=5)
        property_vars['subject'] = StringVar(value=config.get('subject', ''))
        ttk.Entry(main_frame, textvariable=property_vars['subject']).pack(fill='x', padx=5, pady=(0, 5))
        ttk.Label(main_frame, text=self.loc.get('prop_body_manual_label')).pack(anchor='w', padx=5)
        body_editor = scrolledtext.ScrolledText(main_frame, height=8)
        body_editor.pack(fill='both', expand=True, padx=5, pady=5)
        body_editor.insert("1.0", config.get('body', ''))
        property_vars['body'] = body_editor
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Email sending is a live action.'}]
