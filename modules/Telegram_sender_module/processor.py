#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\Telegram_sender_module\processor.py
# JUMLAH BARIS : 140
#######################################################################

import telegram
import os
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
from flowork_kernel.ui_shell.components.InfoLabel import InfoLabel
import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext
class TelegramSenderModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "basic"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.variable_manager = services.get("variable_manager_service")
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not self.variable_manager:
            return self.error_payload("VariableManager service is not available.")
        bot_token = self.variable_manager.get_variable("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return self.error_payload("TELEGRAM_BOT_TOKEN is not configured in Settings > Variables.")
        def _resolve_content_value(param_name):
            mode = config.get(f'{param_name}_source', 'dynamic')
            if mode == 'dynamic':
                var_path = config.get(f'dynamic_{param_name}_variable')
                if not var_path:
                    raise ValueError(f"Dynamic variable for '{param_name}' is not set.")
                return get_nested_value(payload, var_path)
            else: # manual
                return config.get(f'manual_{param_name}')
        try:
            override_variable = config.get('recipient_override_variable')
            chat_id = get_nested_value(payload, override_variable) if override_variable else None
            if not chat_id:
                chat_id = self.variable_manager.get_variable("TELEGRAM_CHAT_ID")
                if chat_id:
                    status_updater("Using global Chat ID from Settings.", "DEBUG")
            else:
                status_updater(f"Using override Chat ID from payload variable '{override_variable}'.", "INFO")
            if not chat_id:
                return self.error_payload("Telegram Chat ID is not set. Please configure it in Settings > Variables, or provide an override in the node properties.")
            content = _resolve_content_value('content') or ""
            file_path = get_nested_value(payload, config.get('file_path_variable', '')) if config.get('file_path_variable') else None
            if not content and (not file_path or not os.path.exists(file_path)):
                 return self.error_payload("No content or valid file path provided to send.")
            bot = telegram.Bot(token=bot_token)
            sent_message = None
            if file_path and os.path.exists(file_path):
                status_updater(f"Sending file: {os.path.basename(file_path)} to {chat_id}...", "INFO")
                file_type = self._get_file_type(file_path)
                with open(file_path, 'rb') as f:
                    if file_type == 'photo':
                        sent_message = bot.send_photo(chat_id=chat_id, photo=f, caption=content)
                    elif file_type == 'audio':
                        sent_message = bot.send_audio(chat_id=chat_id, audio=f, caption=content)
                    else: # document
                        sent_message = bot.send_document(chat_id=chat_id, document=f, caption=content)
            elif content:
                status_updater(f"Sending text message to {chat_id}...", "INFO")
                sent_message = bot.send_message(chat_id=chat_id, text=content)
            status_updater("Message sent successfully!", "SUCCESS")
            if 'data' not in payload: payload['data'] = {}
            payload['data']['telegram_message_id'] = sent_message.message_id
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            return self.error_payload(f"Failed to send Telegram message: {e}")
    def _get_file_type(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            return 'photo'
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a']:
            return 'audio'
        else:
            return 'document'
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        InfoLabel(
            parent_frame,
            text=self.loc.get('prop_telegram_info_text', fallback="This module uses the TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from your global Settings. You can optionally override the recipient below."),
            bootstyle="info"
        )
        override_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_recipient_override_title', fallback="Recipient Override (Optional)"))
        override_frame.pack(fill='x', padx=5, pady=10)
        property_vars['recipient_override_variable'] = StringVar(value=config.get('recipient_override_variable', ''))
        LabelledCombobox(
            parent=override_frame,
            label_text=self.loc.get('prop_recipient_override_label', fallback="Get Recipient from Variable:"),
            variable=property_vars['recipient_override_variable'],
            values=[''] + list(available_vars.keys())
        )
        def _create_dynamic_input(parent, param_name, title_key, manual_widget_type='entry', default_var_path=''):
            frame = ttk.LabelFrame(parent, text=self.loc.get(title_key))
            frame.pack(fill='x', padx=5, pady=5, expand=True)
            mode_var = StringVar(value=config.get(f'{param_name}_source', 'dynamic'))
            property_vars[f'{param_name}_source'] = mode_var
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
            if manual_widget_type == 'textarea':
                widget = scrolledtext.ScrolledText(manual_frame, height=4)
                widget.insert("1.0", config.get(f'manual_{param_name}', ''))
                property_vars[f'manual_{param_name}'] = widget
            else: # entry
                manual_var = StringVar(value=config.get(f'manual_{param_name}', ''))
                property_vars[f'manual_{param_name}'] = manual_var
                widget = ttk.Entry(manual_frame, textvariable=manual_var)
            widget.pack(fill='x', pady=(2,5))
            dynamic_var = StringVar(value=config.get(f'dynamic_{param_name}_variable', default_var_path))
            property_vars[f'dynamic_{param_name}_variable'] = dynamic_var
            LabelledCombobox(dynamic_frame, self.loc.get(f'prop_dynamic_{param_name}_label'), dynamic_var, list(available_vars.keys()))
            toggle_mode()
        _create_dynamic_input(parent_frame, 'content', 'prop_content_source_label', manual_widget_type='textarea', default_var_path='data.message')
        file_frame = ttk.LabelFrame(parent_frame, text="Attachment (Optional)")
        file_frame.pack(fill='x', padx=5, pady=5, expand=True)
        property_vars['file_path_variable'] = StringVar(value=config.get('file_path_variable', 'data.file_path'))
        LabelledCombobox(file_frame, self.loc.get('prop_file_path_label'), property_vars['file_path_variable'], [''] + list(available_vars.keys()))
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'This action sends a live message to Telegram and cannot be previewed.'}]
    def error_payload(self, error_message: str):
        self.logger(error_message, "ERROR")
        return {"payload": {"error": error_message}, "output_name": "error"}
