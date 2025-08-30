#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\email_sender_module_b5c6\processor.py
# JUMLAH BARIS : 127
#######################################################################

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
class EmailSenderModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "basic"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.logger("Module 'Email Sender' initialized.", "INFO") # Log dalam bahasa Inggris
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        status_updater("Preparing to send email...", "INFO")
        smtp_server = config.get('smtp_server')
        smtp_port = config.get('smtp_port', 587)
        smtp_user = config.get('smtp_username')
        smtp_pass = config.get('smtp_password')
        def get_config_value(param_name):
            mode = config.get(f'{param_name}_mode', 'manual')
            if mode == 'dynamic':
                var_path = config.get(f'{param_name}_variable')
                if not var_path:
                    raise ValueError(f"Dynamic variable for '{param_name}' is not set.")
                return get_nested_value(payload, var_path)
            else: # manual
                return config.get(param_name)
        try:
            recipient = get_config_value('recipient')
            subject = get_config_value('subject')
            body = get_config_value('body')
            if not all([smtp_server, smtp_port, smtp_user, smtp_pass, recipient, subject, body]):
                raise ValueError("One or more required email parameters are missing.")
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            status_updater(f"Connecting to {smtp_server}...", "INFO")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            text = msg.as_string()
            server.sendmail(smtp_user, recipient, text)
            server.quit()
            status_updater("Email sent successfully!", "SUCCESS")
            self.logger(f"Email sent successfully to {recipient}", "SUCCESS")
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data']['email_status'] = 'Sent successfully'
            payload['data']['recipient'] = recipient
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            error_msg = f"Failed to send email: {e}"
            self.logger(error_msg, "ERROR")
            status_updater(error_msg, "ERROR")
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
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
            manual_var = StringVar(value=config.get(param_name, ''))
            property_vars[param_name] = manual_var
            if manual_widget_type == 'textarea':
                widget = scrolledtext.ScrolledText(manual_frame, height=5)
                widget.insert("1.0", config.get(param_name, ''))
                property_vars[param_name] = widget # Special case for text area
            else:
                widget = ttk.Entry(manual_frame, textvariable=manual_var)
            widget.pack(fill='x')
            dynamic_var = StringVar(value=config.get(f'{param_name}_variable', ''))
            property_vars[f'{param_name}_variable'] = dynamic_var
            LabelledCombobox(dynamic_frame, self.loc.get('prop_path_input_key_label'), dynamic_var, list(available_vars.keys()))
            toggle_mode()
        server_frame = ttk.LabelFrame(parent_frame, text="SMTP Server Settings")
        server_frame.pack(fill='x', padx=5, pady=5)
        property_vars['smtp_server'] = StringVar(value=config.get('smtp_server', ''))
        ttk.Label(server_frame, text="Server:").pack(anchor='w', padx=10)
        ttk.Entry(server_frame, textvariable=property_vars['smtp_server']).pack(fill='x', padx=10, pady=(0,5))
        property_vars['smtp_port'] = StringVar(value=config.get('smtp_port', '587'))
        ttk.Label(server_frame, text="Port:").pack(anchor='w', padx=10)
        ttk.Entry(server_frame, textvariable=property_vars['smtp_port']).pack(fill='x', padx=10, pady=(0,5))
        property_vars['smtp_username'] = StringVar(value=config.get('smtp_username', ''))
        ttk.Label(server_frame, text="Username (Email):").pack(anchor='w', padx=10)
        ttk.Entry(server_frame, textvariable=property_vars['smtp_username']).pack(fill='x', padx=10, pady=(0,5))
        property_vars['smtp_password'] = StringVar(value=config.get('smtp_password', ''))
        ttk.Label(server_frame, text="Password:").pack(anchor='w', padx=10)
        ttk.Entry(server_frame, textvariable=property_vars['smtp_password'], show="*").pack(fill='x', padx=10, pady=(0,10))
        create_dynamic_input_frame(parent_frame, 'recipient', 'prop_recipient_mode_label')
        create_dynamic_input_frame(parent_frame, 'subject', 'prop_subject_mode_label')
        create_dynamic_input_frame(parent_frame, 'body', 'prop_body_mode_label', manual_widget_type='textarea')
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
