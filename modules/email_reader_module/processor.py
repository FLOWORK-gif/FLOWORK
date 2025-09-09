#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\email_reader_module\processor.py
# JUMLAH BARIS : 170
#######################################################################

from flowork_kernel.core import build_security
import imaplib
import email
import re
from email.header import decode_header
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
class EmailReaderModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema):
    TIER = "pro"
    """
    Connects to an IMAP email server to find and read emails.
    (MODIFIED) Now uses unified global variables: EMAIL_ADDRESS and EMAIL_PASSWORD.
    (REFACTORED) Implemented dynamic/manual input modes for search criteria.
    (REFACTORED) Replaced initial exceptions with error payload returns.
    """
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
        self.variable_manager = services.get("variable_manager_service")
    def _error_payload(self, payload, error_message, status_updater):
        status_updater(error_message, "ERROR")
        self.logger(f"Email Reader failed: {error_message}", "ERROR")
        payload['error'] = error_message
        return {"payload": payload, "output_name": "error"}
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not self.variable_manager:
            return self._error_payload(payload, "VariableManager service is not available.", status_updater)
        imap_server = self.variable_manager.get_variable("IMAP_HOST")
        email_user = self.variable_manager.get_variable("EMAIL_ADDRESS")
        email_pass = self.variable_manager.get_variable("EMAIL_PASSWORD")
        if not all([imap_server, email_user, email_pass]):
            return self._error_payload(payload, "Email credentials (IMAP_HOST, EMAIL_ADDRESS, EMAIL_PASSWORD) are not fully configured in Settings > Variable Management.", status_updater)
        search_from = self._resolve_value(config, payload, 'from')
        search_subject = self._resolve_value(config, payload, 'subject')
        mark_as_read = config.get('mark_as_read', True)
        delete_after_read = config.get('delete_after_read', False)
        status_updater(f"Connecting to {imap_server}...", "INFO")
        try:
            with imaplib.IMAP4_SSL(imap_server) as M:
                M.login(email_user, email_pass)
                M.select("inbox")
                search_criteria = ['(UNSEEN)'] if mark_as_read else ['(ALL)']
                if search_from:
                    search_criteria.append(f'(FROM "{search_from}")')
                if search_subject:
                    search_criteria.append(f'(SUBJECT "{search_subject}")')
                search_query = " ".join(search_criteria)
                status_updater(f"Searching inbox with query: {search_query}", "INFO")
                typ, data = M.search(None, search_query)
                if typ != 'OK':
                    return self._error_payload(payload, "IMAP search command failed.", status_updater)
                mail_ids = data[0].split()
                if not mail_ids:
                    status_updater("No matching emails found.", "WARN")
                    return {"payload": payload, "output_name": "not_found"}
                latest_email_id = mail_ids[-1]
                status_updater(f"Found email. Fetching content...", "INFO")
                typ, msg_data = M.fetch(latest_email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                email_body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                email_body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                                break
                            except:
                                continue
                else:
                    try:
                        email_body = msg.get_payload(decode=True).decode('utf-8', 'ignore')
                    except:
                        email_body = "Could not decode email body."
                if not email_body:
                    self.logger("Could not extract plain text body from the email. It might be HTML only.", "WARN")
                    for part in msg.walk():
                        if "text" in part.get_content_type():
                            try:
                                email_body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                                if email_body:
                                    break
                            except:
                                continue
                if not email_body:
                     return self._error_payload(payload, "Could not extract any text body from the email.", status_updater)
                if 'data' not in payload or not isinstance(payload.get('data'), dict):
                    payload['data'] = {}
                payload['data']['email_body'] = email_body.strip()
                if delete_after_read:
                    M.store(latest_email_id, '+FLAGS', '\\Deleted')
                    M.expunge()
                    status_updater("Extracted and deleted email.", "SUCCESS")
                elif mark_as_read:
                    M.store(latest_email_id, '+FLAGS', '\\Seen')
                    status_updater("Extracted and marked as read.", "SUCCESS")
                return {"payload": payload, "output_name": "success"}
        except Exception as e:
            return self._error_payload(payload, str(e), status_updater)
    def _resolve_value(self, config, payload, param_name):
        mode = config.get(f'{param_name}_source_mode', 'manual')
        if mode == 'dynamic':
            var_path = config.get(f'{param_name}_source_variable')
            return get_nested_value(payload, var_path)
        else: # manual
            return config.get(f'manual_{param_name}')
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        info_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_email_reader_creds_title'))
        info_frame.pack(fill='x', padx=5, pady=10)
        ttk.Label(info_frame, text=self.loc.get('prop_email_reader_creds_info'), wraplength=400, justify='left', bootstyle='info').pack(padx=5, pady=5)
        def _create_dynamic_input(parent, title_key, param_name):
            frame = ttk.LabelFrame(parent, text=self.loc.get(title_key))
            frame.pack(fill='x', padx=5, pady=5, expand=True)
            mode_var = StringVar(value=config.get(f'{param_name}_source_mode', 'manual'))
            property_vars[f'{param_name}_source_mode'] = mode_var
            manual_frame = ttk.Frame(frame)
            dynamic_frame = ttk.Frame(frame)
            def toggle_mode():
                if mode_var.get() == 'manual':
                    dynamic_frame.pack_forget()
                    manual_frame.pack(fill='x', padx=10, pady=5)
                else:
                    manual_frame.pack_forget()
                    dynamic_frame.pack(fill='x', padx=10, pady=5)
            ttk.Radiobutton(frame, text=self.loc.get('prop_mode_manual'), variable=mode_var, value='manual', command=toggle_mode).pack(anchor='w', padx=10)
            ttk.Radiobutton(frame, text=self.loc.get('prop_mode_dynamic'), variable=mode_var, value='dynamic', command=toggle_mode).pack(anchor='w', padx=10)
            manual_var = StringVar(value=config.get(f'manual_{param_name}', ''))
            property_vars[f'manual_{param_name}'] = manual_var
            ttk.Entry(manual_frame, textvariable=manual_var).pack(fill='x')
            dynamic_var = StringVar(value=config.get(f'{param_name}_source_variable', ''))
            property_vars[f'{param_name}_source_variable'] = dynamic_var
            LabelledCombobox(dynamic_frame, self.loc.get('prop_path_input_key_label'), dynamic_var, list(available_vars.keys()))
            toggle_mode()
        search_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_email_reader_search_title'))
        search_frame.pack(fill='x', padx=5, pady=5)
        _create_dynamic_input(search_frame, "prop_email_from_source", 'from')
        _create_dynamic_input(search_frame, "prop_email_subject_source", 'subject')
        options_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_email_reader_options_title'))
        options_frame.pack(fill='x', padx=5, pady=5)
        property_vars['mark_as_read'] = BooleanVar(value=config.get('mark_as_read', True))
        ttk.Checkbutton(options_frame, text=self.loc.get('prop_email_reader_mark_read_label'), variable=property_vars['mark_as_read']).pack(anchor='w', padx=5)
        property_vars['delete_after_read'] = BooleanVar(value=config.get('delete_after_read', False))
        ttk.Checkbutton(options_frame, text=self.loc.get('prop_email_reader_delete_label'), variable=property_vars['delete_after_read']).pack(anchor='w', padx=5)
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_dynamic_output_schema(self, config):
        return [
            {
                "name": "data.email_body",
                "type": "string",
                "description": "The entire plain text content of the found email."
            }
        ]
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Cannot safely connect to an email server for a live preview.'}]
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
