#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\intelligent_content_extractor\processor.py
# JUMLAH BARIS : 148
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar, IntVar, scrolledtext
import os
import time
import re
import json
import urllib.parse
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    UNDETECTED_CHROME_AVAILABLE = False
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_EXTRAS_AVAILABLE = True
except ImportError:
    SELENIUM_EXTRAS_AVAILABLE = False
class IntelligentContentExtractorModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "architect"
    VERSION = "9.0"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        if not UNDETECTED_CHROME_AVAILABLE or not BS4_AVAILABLE:
            self.logger("FATAL: 'undetected-chromedriver' and 'beautifulsoup4' libraries are required.", "CRITICAL")
        if not SELENIUM_EXTRAS_AVAILABLE:
            self.logger("FATAL: Core Selenium components are missing. Please ensure 'selenium' is installed correctly.", "CRITICAL")
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not UNDETECTED_CHROME_AVAILABLE or not BS4_AVAILABLE or not SELENIUM_EXTRAS_AVAILABLE:
            raise RuntimeError("Required libraries are not installed correctly.")
        objective_source_variable = config.get('objective_source_variable', 'data.prompt')
        manual_objective = config.get('manual_objective', '')
        user_objective = get_nested_value(payload, objective_source_variable)
        if not user_objective:
            self.logger(f"Objective not found in payload variable '{objective_source_variable}', falling back to manual objective.", "DEBUG") # English log
            user_objective = manual_objective
        if not user_objective:
            raise ValueError("User Objective is empty. Please provide an objective in the payload or in the node's properties.")
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        if not ai_manager: raise RuntimeError("AIProviderManagerService is not available.")
        driver = None
        interaction_log = []
        try:
            status_updater("AI is formulating the best Google search query...", "INFO")
            prompt_for_query = f"""
You are a Google Search expert. Convert the user's request into an optimal Google search query.
- If a specific website is mentioned (e.g., 'detik.com'), use the `site:` operator.
- If NO specific website is mentioned, create a general but effective search query.
User request: "{user_objective}"
Optimal Google search query (provide ONLY the query string):
"""
            query_response = ai_manager.query_ai_by_task('text', prompt_for_query)
            if "error" in query_response: raise ValueError(f"AI failed to generate search query: {query_response['error']}")
            search_query = query_response.get('data', user_objective).strip().split('\n')[0].replace("`", "").replace('"', '')
            interaction_log.append({'step': 1, 'action': 'GENERATE_QUERY', 'result': search_query})
            self.logger(f"AI generated Google query: '{search_query}'", "SUCCESS")
            status_updater(f"Searching Google for: '{search_query}'...", "INFO")
            search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(search_query)}"
            interaction_log.append({'step': 2, 'action': 'SEARCH_GOOGLE', 'url': search_url})
            options = uc.ChromeOptions()
            driver = uc.Chrome(options=options) # Otomatis deteksi versi Chrome
            driver.get(search_url)
            status_updater("Finding the first relevant search result...", "INFO")
            first_result_link_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "(//div[@id='search']//a[h3])[1]"))
            )
            target_article_url = first_result_link_element.get_attribute('href')
            interaction_log.append({'step': 3, 'action': 'GET_FIRST_RESULT', 'url': target_article_url})
            self.logger(f"Found top article link: {target_article_url}", "INFO")
            status_updater(f"Navigating to article and extracting content...", "INFO")
            driver.get(target_article_url)
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            page_html = driver.page_source
            soup = BeautifulSoup(page_html, "html.parser")
            for element in soup(["script", "style", "header", "footer", "aside", "nav"]):
                element.decompose()
            main_content = soup.get_text(separator='\n', strip=True)
            sanitized_content = main_content.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')
            extraction_prompt = f"Based on the user's original objective, provide a concise summary or extract the key information from the following page content.\n\nOriginal Objective: \"{user_objective}\"\n\nPage Content:\n---\n{sanitized_content[:12000]}\n---\n\nExtracted Information (in Indonesian):"
            extraction_response = ai_manager.query_ai_by_task('text', extraction_prompt)
            if "error" in extraction_response: raise ValueError(f"AI failed to extract content: {extraction_response['error']}")
            final_answer = extraction_response.get('data', 'Could not extract information.')
            status_updater("Objective complete!", "SUCCESS")
            if not isinstance(payload, dict): payload = {}
            if 'data' not in payload: payload['data'] = {}
            payload['data']['agent_final_answer'] = final_answer
            payload['data']['interaction_log'] = interaction_log
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            error_msg = f"AI Web Agent failed: {e}"
            self.logger(error_msg, "ERROR")
            if not isinstance(payload, dict): payload = {}
            if 'data' not in payload: payload['data'] = {}
            payload['data']['error'] = error_msg
            payload['data']['interaction_log'] = interaction_log
            return {"payload": payload, "output_name": "error"}
        finally:
            if driver:
                driver.quit()
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        source_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_objective_source_mode_label'))
        source_frame.pack(fill='x', padx=5, pady=5)
        property_vars['objective_source_mode'] = StringVar(value=config.get('objective_source_mode', 'manual'))
        manual_objective_frame = ttk.Frame(source_frame)
        dynamic_objective_frame = ttk.Frame(source_frame)
        def _toggle_objective_source():
            if property_vars['objective_source_mode'].get() == 'manual':
                manual_objective_frame.pack(fill='x', padx=5, pady=5)
                dynamic_objective_frame.pack_forget()
            else:
                manual_objective_frame.pack_forget()
                dynamic_objective_frame.pack(fill='x', padx=5, pady=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_manual'), variable=property_vars['objective_source_mode'], value='manual', command=_toggle_objective_source).pack(anchor='w', padx=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_dynamic'), variable=property_vars['objective_source_mode'], value='dynamic', command=_toggle_objective_source).pack(anchor='w', padx=5)
        ttk.Label(manual_objective_frame, text=self.loc.get('prop_manual_objective_label', fallback="Objective / Prompt:")).pack(fill='x')
        objective_editor = scrolledtext.ScrolledText(manual_objective_frame, height=4, font=("Helvetica", 9))
        objective_editor.pack(fill="both", expand=True, pady=(0, 5))
        objective_editor.insert('1.0', config.get('manual_objective', ''))
        property_vars['manual_objective'] = objective_editor
        property_vars['objective_source_variable'] = StringVar(value=config.get('objective_source_variable', ''))
        LabelledCombobox(parent=dynamic_objective_frame, label_text=self.loc.get('prop_objective_source_variable_label'), variable=property_vars['objective_source_variable'], values=list(available_vars.keys()))
        _toggle_objective_source()
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'This module performs live web navigation and AI analysis.'}]
