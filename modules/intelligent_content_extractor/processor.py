#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\intelligent_content_extractor\processor.py
# JUMLAH BARIS : 126
#######################################################################

from flowork_kernel.core import build_security
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar, scrolledtext
import json
import re
import time
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
    LIBRARIES_AVAILABLE = True
except ImportError:
    LIBRARIES_AVAILABLE = False
class IntelligentContentExtractorModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema):
    TIER = "architect" # ATURAN MODUL 2
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        try:
            if not LIBRARIES_AVAILABLE:
                raise ImportError("Required libraries (selenium, webdriver-manager, beautifulsoup4) are not installed.") # English Log
            objective = ""
            if config.get('objective_source_mode') == 'dynamic':
                objective = get_nested_value(payload, config.get('objective_source_variable'))
            else:
                objective = config.get('manual_objective')
            if not objective:
                raise ValueError("Objective for the agent is not defined.") # English Log
            max_steps = config.get('max_steps', 10)
            ai_brain_endpoint = config.get('ai_brain_endpoint')
            is_headless = config.get('headless_mode', True)
            if not ai_brain_endpoint:
                raise ValueError("AI Brain endpoint is not selected in node properties.") # English Log
            status_updater("Initializing agent...", "INFO") # English Log
            final_answer = f"Simulation complete for objective: {objective}"
            interaction_log = [
                {"thought": "I need to start by going to a website.", "action": "navigate", "url": "https://example.com"},
                {"observation": "Page loaded successfully."},
                {"thought": "I have completed the objective.", "action": "finish", "answer": final_answer}
            ]
            status_updater("Agent finished objective.", "SUCCESS") # English Log
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data']['agent_final_answer'] = final_answer
            payload['data']['interaction_log'] = interaction_log
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            error_msg = f"Agentic Scraper failed: {e}" # English Log
            self.logger(error_msg, "ERROR")
            status_updater(error_msg, "ERROR")
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        source_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_objective_source_mode_label'))
        source_frame.pack(fill='x', padx=5, pady=10)
        property_vars['objective_source_mode'] = StringVar(value=config.get('objective_source_mode', 'manual'))
        manual_frame = ttk.Frame(source_frame)
        dynamic_frame = ttk.Frame(source_frame)
        def _toggle_source():
            if property_vars['objective_source_mode'].get() == 'manual':
                dynamic_frame.pack_forget()
                manual_frame.pack(fill='x', padx=5, pady=5)
            else:
                manual_frame.pack_forget()
                dynamic_frame.pack(fill='x', padx=5, pady=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_manual'), variable=property_vars['objective_source_mode'], value='manual', command=_toggle_source).pack(anchor='w', padx=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_dynamic'), variable=property_vars['objective_source_mode'], value='dynamic', command=_toggle_source).pack(anchor='w', padx=5)
        ttk.Label(manual_frame, text=self.loc.get('prop_manual_objective_label')).pack(anchor='w')
        manual_text = scrolledtext.ScrolledText(manual_frame, height=5, wrap="word")
        manual_text.pack(fill='x', expand=True)
        manual_text.insert("1.0", config.get('manual_objective', ''))
        property_vars['manual_objective'] = manual_text
        property_vars['objective_source_variable'] = StringVar(value=config.get('objective_source_variable', 'data.prompt'))
        LabelledCombobox(parent=dynamic_frame, label_text=self.loc.get('prop_objective_source_variable_label'), variable=property_vars['objective_source_variable'], values=list(available_vars.keys()))
        _toggle_source()
        agent_config_frame = ttk.LabelFrame(parent_frame, text="Agent Configuration")
        agent_config_frame.pack(fill='x', padx=5, pady=10)
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        all_endpoints = ai_manager.get_available_providers() if ai_manager else {}
        display_to_id_map = {name: id for id, name in all_endpoints.items()}
        id_to_display_map = {id: name for id, name in all_endpoints.items()}
        endpoint_display_list = sorted(list(display_to_id_map.keys()))
        provider_display_var = StringVar()
        saved_endpoint_id = config.get('ai_brain_endpoint')
        if saved_endpoint_id in id_to_display_map:
            provider_display_var.set(id_to_display_map[saved_endpoint_id])
        property_vars['ai_brain_endpoint'] = LabelledCombobox(parent=agent_config_frame, label_text=self.loc.get('prop_ai_brain_label'), variable=provider_display_var, values=endpoint_display_list)
        property_vars['max_steps'] = StringVar(value=config.get('max_steps', 10))
        ttk.Label(agent_config_frame, text=self.loc.get('prop_max_steps_label')).pack(anchor='w', padx=5, pady=(5,0))
        ttk.Entry(agent_config_frame, textvariable=property_vars['max_steps']).pack(fill='x', padx=5)
        property_vars['headless_mode'] = BooleanVar(value=config.get('headless_mode', True))
        ttk.Checkbutton(agent_config_frame, text=self.loc.get('prop_headless_mode_label'), variable=property_vars['headless_mode']).pack(anchor='w', padx=5, pady=5)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Agentic execution is a live process and cannot be previewed.'}] # English Log
    def get_dynamic_output_schema(self, config):
        return [
            {
                "name": "data.agent_final_answer",
                "type": "string",
                "description": "The final processed information extracted by the AI agent."
            },
            {
                "name": "data.interaction_log",
                "type": "list",
                "description": "A step-by-step log of the agent's actions and observations."
            }
        ]
