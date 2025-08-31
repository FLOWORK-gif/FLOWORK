#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\email_reader_module\processor.py
# JUMLAH BARIS : 136
#######################################################################

import imaplib
import email
import re
from email.header import decode_header
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar, scrolledtext
class EmailReaderModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "pro"
    """
    Connects to an IMAP email server to find and read emails.
    (MODIFIED) Now uses unified global variables: EMAIL_ADDRESS and EMAIL_PASSWORD.
    """
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.variable_manager = services.get("variable_manager_service")
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not self.variable_manager:
            raise RuntimeError("VariableManager service is required for this module.")
        imap_server = self.variable_manager.get_variable("IMAP_HOST")
        email_user = self.variable_manager.get_variable("EMAIL_ADDRESS") # Changed from IMAP_USER
        email_pass = self.variable_manager.get_variable("EMAIL_PASSWORD") # Changed from IMAP_PASS
        if not all([imap_server, email_user, email_pass]):
            raise ValueError("Email credentials (IMAP_HOST, EMAIL_ADDRESS, EMAIL_PASSWORD) are not fully configured in Settings > Variable Management.")
        search_from = self._resolve_value(config.get('search_from', ''), payload)
        search_subject = self._resolve_value(config.get('search_subject', ''), payload)
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
                    raise Exception("IMAP search command failed.")
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
                    self.logger("Could not extract plain text body from the email. It might be HTML only.", "WARN") # English Log
                    for part in msg.walk():
                        if "text" in part.get_content_type():
                            try:
                                email_body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                                if email_body:
                                    break
                            except:
                                continue
                if not email_body:
                     raise Exception("Could not extract any text body from the email.")
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
            self.logger(f"Email Reader failed: {e}", "ERROR")
            payload['error'] = str(e)
            return {"payload": payload, "output_name": "error"}
    def _resolve_value(self, value_str, payload):
        if not isinstance(value_str, str):
            return value_str
        matches = re.findall(r"\{\{([\w\.]+)\}\}", value_str)
        if not matches:
            return value_str
        resolved_value = get_nested_value(payload, matches[0])
        return resolved_value if resolved_value is not None else value_str
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        info_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_email_reader_creds_title'))
        info_frame.pack(fill='x', padx=5, pady=10)
        ttk.Label(info_frame, text=self.loc.get('prop_email_reader_creds_info'), wraplength=400, justify='left', bootstyle='info').pack(padx=5, pady=5)
        search_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_email_reader_search_title'))
        search_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(search_frame, text=self.loc.get('prop_email_reader_from_label')).pack(anchor='w', padx=5)
        property_vars['search_from'] = StringVar(value=config.get('search_from', ''))
        ttk.Entry(search_frame, textvariable=property_vars['search_from']).pack(fill='x', padx=5, pady=(0,5))
        ttk.Label(search_frame, text=self.loc.get('prop_email_reader_subject_label')).pack(anchor='w', padx=5)
        property_vars['search_subject'] = StringVar(value=config.get('search_subject', ''))
        ttk.Entry(search_frame, textvariable=property_vars['search_subject']).pack(fill='x', padx=5, pady=(0,5))
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
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Cannot safely connect to an email server for a live preview.'}]
