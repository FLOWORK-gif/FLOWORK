#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\email_sender_module_b5c6\processor.py
# JUMLAH BARIS : 149
#######################################################################

from flowork_kernel.core import build_security
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
class EmailSenderModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema):
    TIER = "basic"
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
        self.logger("Module 'Email Sender' initialized.", "INFO") # English Log
    def _error_payload(self, payload, error_message, status_updater):
        self.logger(f"Email Sender failed: {error_message}", "ERROR")
        status_updater(error_message, "ERROR")
        if 'data' not in payload or not isinstance(payload['data'], dict):
            payload['data'] = {}
        payload['data']['error'] = error_message
        return {"payload": payload, "output_name": "error"}
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        try:
            status_updater("Preparing to send email...", "INFO") # English Log
            variable_manager = self.kernel.get_service("variable_manager_service")
            if not variable_manager:
                return self._error_payload(payload, "VariableManager service is not available.", status_updater)
            smtp_server = variable_manager.get_variable("SMTP_HOST")
            smtp_port = variable_manager.get_variable("SMTP_PORT")
            smtp_user = variable_manager.get_variable("EMAIL_ADDRESS")
            smtp_pass = variable_manager.get_variable("EMAIL_PASSWORD")
            if not all([smtp_server, smtp_port, smtp_user, smtp_pass]):
                return self._error_payload(payload, "SMTP credentials are not fully configured in Settings.", status_updater)
            try:
                smtp_port = int(smtp_port)
            except (ValueError, TypeError):
                return self._error_payload(payload, "SMTP_PORT variable must be a valid number.", status_updater)
            def get_config_value(param_name):
                mode = config.get(f'{param_name}_mode', 'manual')
                if mode == 'dynamic':
                    var_path = config.get(f'{param_name}_variable')
                    if not var_path:
                        return None, f"Dynamic variable for '{param_name}' is not set."
                    value = get_nested_value(payload, var_path)
                    return value, None
                else: # manual
                    return config.get(param_name), None
            recipient, recipient_error = get_config_value('recipient')
            if recipient_error: return self._error_payload(payload, recipient_error, status_updater)
            subject, subject_error = get_config_value('subject')
            if subject_error: return self._error_payload(payload, subject_error, status_updater)
            body, body_error = get_config_value('body')
            if body_error: return self._error_payload(payload, body_error, status_updater)
            if not all([recipient, subject, body]):
                return self._error_payload(payload, "Recipient, Subject, and Body cannot be empty.", status_updater)
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            status_updater(f"Connecting to {smtp_server}...", "INFO") # English Log
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            text = msg.as_string()
            server.sendmail(smtp_user, recipient, text)
            server.quit()
            status_updater("Email sent successfully!", "SUCCESS") # English Log
            self.logger(f"Email sent successfully to {recipient}", "SUCCESS") # English Log
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data']['email_status'] = 'Sent successfully'
            payload['data']['recipient'] = recipient
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            return self._error_payload(payload, f"Failed to send email: {e}", status_updater)
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        def create_dynamic_input_frame(parent, param_name, title_key, manual_widget_type='entry'):
            frame = ttk.LabelFrame(parent, text=self.loc.get(title_key, fallback=f"{param_name.replace('_', ' ').title()} Source"))
            frame.pack(fill='x', padx=5, pady=5, expand=True)
            mode_var = StringVar(value=config.get(f'{param_name}_mode', 'manual'))
            property_vars[f'{param_name}_mode'] = mode_var
            manual_frame = ttk.Frame(frame)
            dynamic_frame = ttk.Frame(frame)
            def toggle_mode():
                if mode_var.get() == 'manual':
                    dynamic_frame.pack_forget()
                    manual_frame.pack(fill='x', padx=10, pady=5)
                else:
                    manual_frame.pack_forget()
                    dynamic_frame.pack(fill='x', padx=10, pady=5)
            ttk.Radiobutton(frame, text=self.loc.get('prop_mode_manual'), variable=mode_var, value='manual', command=toggle_mode).pack(anchor='w', padx=10, pady=(5,0))
            ttk.Radiobutton(frame, text=self.loc.get('prop_mode_dynamic'), variable=mode_var, value='dynamic', command=toggle_mode).pack(anchor='w', padx=10)
            manual_var_value = config.get(param_name, '')
            if manual_widget_type == 'textarea':
                widget = scrolledtext.ScrolledText(manual_frame, height=5)
                widget.insert("1.0", manual_var_value)
                property_vars[param_name] = widget
            else:
                manual_var = StringVar(value=manual_var_value)
                property_vars[param_name] = manual_var
                widget = ttk.Entry(manual_frame, textvariable=manual_var)
            widget.pack(fill='x')
            dynamic_var = StringVar(value=config.get(f'{param_name}_variable', ''))
            property_vars[f'{param_name}_variable'] = dynamic_var
            LabelledCombobox(dynamic_frame, self.loc.get('prop_path_input_key_label'), dynamic_var, list(available_vars.keys()))
            toggle_mode()
        server_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_smtp_title'))
        server_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(server_frame, text=self.loc.get('prop_smtp_auto_fetch_info'), wraplength=400, justify='left', bootstyle='info').pack(padx=5, pady=5)
        create_dynamic_input_frame(parent_frame, 'recipient', 'prop_recipient_source_label')
        create_dynamic_input_frame(parent_frame, 'subject', 'prop_subject_source_label')
        create_dynamic_input_frame(parent_frame, 'body', 'prop_body_source_label', manual_widget_type='textarea')
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        return {
            'action': 'Send Email',
            'to': config.get('recipient', 'N/A'),
            'subject': config.get('subject', 'N/A'),
            'status': 'This is a preview. No email will be sent.'
        }
    def get_dynamic_output_schema(self, config):
        return [
            {
                "name": "data.email_status",
                "type": "string",
                "description": "The status of the email sending operation, e.g., 'Sent successfully'."
            },
            {
                "name": "data.recipient",
                "type": "string",
                "description": "The email address the email was sent to."
            }
        ]
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
