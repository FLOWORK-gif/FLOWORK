#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\advanced_web_scraper_module_1a2b\processor.py
# JUMLAH BARIS : 284
#######################################################################

from flowork_kernel.core import build_security
import time
import re
import json
import os
import hashlib
from bs4 import BeautifulSoup
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
import ttkbootstrap as ttk
from tkinter import scrolledtext, StringVar, BooleanVar, IntVar
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
class AdvancedWebScraperModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "basic"
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
        if not SELENIUM_AVAILABLE:
            self.logger("FATAL: Selenium/WebDriver-Manager library is not installed for Advanced Web Scraper.", "CRITICAL")
        self.cache_path = os.path.join(self.kernel.data_path, "web_cache")
        os.makedirs(self.cache_path, exist_ok=True)
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not SELENIUM_AVAILABLE:
            error_msg = "Required libraries (selenium, webdriver-manager) are not installed."
            status_updater(error_msg, "ERROR")
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        url_source_mode = config.get('url_source_mode', 'manual')
        target_url = ''
        if url_source_mode == 'dynamic':
            url_variable = config.get('url_source_variable')
            if not url_variable:
                error_msg = "URL source variable is not set in dynamic mode."
                status_updater(error_msg, "ERROR")
                payload['error'] = error_msg
                return {"payload": payload, "output_name": "error"}
            target_url = get_nested_value(payload, url_variable)
        else: # Fallback to manual
            target_url = config.get('target_url', '')
        rules_str = config.get('extraction_rules', '')
        exclude_str = config.get('exclude_selectors', '')
        wait_time = int(config.get('wait_time', 5))
        is_headless = bool(config.get('headless_mode', True))
        use_cache = bool(config.get('use_cache', True))
        if not target_url or not str(target_url).startswith('http'):
            error_msg = f"Target URL is invalid or empty. Received: '{target_url}'"
            status_updater(error_msg, "ERROR")
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        cache_filename = hashlib.md5(str(target_url).encode('utf-8')).hexdigest() + ".html"
        cache_filepath = os.path.join(self.cache_path, cache_filename)
        html_content = None
        if use_cache and os.path.exists(cache_filepath):
            self.logger(f"Cache HIT for {target_url}. Reading from file.", "SUCCESS")
            status_updater("Reading from cache...", "INFO")
            with open(cache_filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
        if html_content is None: # Cache MISS or cache is disabled
            self.logger(f"Cache MISS for {target_url}. Fetching from web.", "WARN")
            driver = None
            try:
                status_updater("Initializing browser driver...", "INFO")
                options = webdriver.ChromeOptions()
                if is_headless:
                    options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1200")
                options.add_argument("--ignore-certificate-errors")
                options.add_argument("--disable-extensions")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                except Exception as e:
                    self.logger(f"Failed to initialize ChromeDriverManager: {e}", "ERROR")
                    self.logger("Please ensure you have a stable internet connection or chromedriver is in your PATH.", "ERROR")
                    error_msg = f"Could not initialize browser driver: {e}"
                    status_updater(error_msg, "ERROR")
                    payload['error'] = error_msg
                    return {"payload": payload, "output_name": "error"}
                status_updater(f"Navigating to {target_url}...", "INFO")
                driver.get(target_url)
                status_updater(f"Waiting for {wait_time}s for page to load...", "INFO")
                time.sleep(wait_time)
                html_content = driver.page_source
                if use_cache:
                    with open(cache_filepath, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    self.logger(f"Saved page content to cache: {cache_filepath}", "INFO")
            finally:
                if driver:
                    status_updater("Closing browser...", "INFO")
                    driver.quit()
        try:
            status_updater("Cleaning and extracting data...", "INFO")
            soup = BeautifulSoup(html_content, 'html.parser')
            if exclude_str:
                exclude_selectors = [line.strip() for line in exclude_str.split('\n') if line.strip()]
                for selector in exclude_selectors:
                    for unwanted_element in soup.select(selector):
                        unwanted_element.decompose()
            extracted_data = {}
            rules = [line.strip() for line in rules_str.split('\n') if line.strip()]
            for rule in rules:
                try:
                    parts = rule.split(':', 1)
                    if len(parts) != 2: continue
                    data_name = parts[0].strip()
                    rule_body = parts[1].strip()
                    option_match = re.search(r'\[(\w+)\]', rule_body)
                    option = option_match.group(1) if option_match else 'text'
                    selector = re.sub(r'\s*\[\w+\]\s*$', '', rule_body).strip() if option_match else rule_body
                    elements = soup.select(selector)
                    if not elements:
                        extracted_data[data_name] = "" if option != 'list' else []
                        continue
                    if option == 'list':
                        extracted_data[data_name] = [el.get_text(strip=True) for el in elements]
                    elif option in ['href', 'src', 'content']:
                        extracted_data[data_name] = elements[0].get(option, '')
                    else: # Default to 'text'
                        extracted_data[data_name] = elements[0].get_text(strip=True)
                except Exception as e:
                    self.logger(f"Failed to process rule '{rule}': {e}", "WARN")
            if 'data' not in payload or not isinstance(payload['data'], dict):
                payload['data'] = {}
            payload['data']['scraped_data'] = extracted_data
            status_updater("Extraction successful!", "SUCCESS")
            return {"payload": payload, "output_name": "success"}
        except Exception as e:
            error_msg = f"An error occurred during data extraction: {e}"
            self.logger(error_msg, "ERROR")
            status_updater("Error during extraction", "ERROR")
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        source_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_url_source_mode_label'))
        source_frame.pack(fill='x', padx=5, pady=10)
        property_vars['url_source_mode'] = StringVar(value=config.get('url_source_mode', 'manual'))
        manual_url_frame = ttk.Frame(source_frame)
        dynamic_url_frame = ttk.Frame(source_frame)
        def _toggle_url_source():
            if property_vars['url_source_mode'].get() == 'manual':
                manual_url_frame.pack(fill='x', padx=5, pady=5)
                dynamic_url_frame.pack_forget()
            else:
                manual_url_frame.pack_forget()
                dynamic_url_frame.pack(fill='x', padx=5, pady=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_manual'), variable=property_vars['url_source_mode'], value='manual', command=_toggle_url_source).pack(anchor='w', padx=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_dynamic'), variable=property_vars['url_source_mode'], value='dynamic', command=_toggle_url_source).pack(anchor='w', padx=5)
        ttk.Label(manual_url_frame, text=self.loc.get('prop_target_url_label')).pack(fill='x')
        property_vars['target_url'] = StringVar(value=config.get('target_url', 'https://'))
        ttk.Entry(manual_url_frame, textvariable=property_vars['target_url']).pack(fill='x')
        property_vars['url_source_variable'] = StringVar(value=config.get('url_source_variable', ''))
        LabelledCombobox(
            parent=dynamic_url_frame,
            label_text=self.loc.get('prop_url_source_variable_label'),
            variable=property_vars['url_source_variable'],
            values=list(available_vars.keys())
        )
        _toggle_url_source()
        ttk.Label(parent_frame, text=self.loc.get('prop_extraction_rules_label')).pack(fill='x', padx=5, pady=(5, 0))
        rules_editor = scrolledtext.ScrolledText(parent_frame, height=8, font=("Consolas", 10))
        rules_editor.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        rules_editor.insert('1.0', config.get('extraction_rules', 'judul_artikel: article.detail h1.detail__title [text]\nisi_artikel: article.detail .detail__body-text [text]'))
        property_vars['extraction_rules'] = rules_editor
        ttk.Label(parent_frame, text=self.loc.get('prop_exclude_selectors_label')).pack(fill='x', padx=5, pady=(5, 0))
        exclude_editor = scrolledtext.ScrolledText(parent_frame, height=4, font=("Consolas", 10))
        exclude_editor.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        exclude_editor.insert('1.0', config.get('exclude_selectors', '.lihatjg\n.para_caption'))
        property_vars['exclude_selectors'] = exclude_editor
        config_frame = ttk.Frame(parent_frame)
        config_frame.pack(fill='x', padx=5, pady=10)
        ttk.Label(config_frame, text=self.loc.get('prop_wait_time_label')).pack(side='left', padx=(0,5))
        property_vars['wait_time'] = IntVar(value=config.get('wait_time', 5))
        wait_entry = ttk.Entry(config_frame, textvariable=property_vars['wait_time'], width=5)
        wait_entry.pack(side='left')
        ToolTip(wait_entry).update_text("Time to wait for the page's JavaScript to finish loading before scraping.")
        property_vars['headless_mode'] = BooleanVar(value=config.get('headless_mode', True))
        headless_check = ttk.Checkbutton(config_frame, text=self.loc.get('prop_headless_mode_label'), variable=property_vars['headless_mode'])
        headless_check.pack(side='left', padx=(20, 10))
        ToolTip(headless_check).update_text("If checked, the browser will run invisibly in the background.")
        property_vars['use_cache'] = BooleanVar(value=config.get('use_cache', True))
        cache_check = ttk.Checkbutton(config_frame, text=self.loc.get('prop_use_cache_label'), variable=property_vars['use_cache'])
        cache_check.pack(side='left', padx=(10, 0))
        ToolTip(cache_check).update_text("If checked, saves a local copy of the page to speed up subsequent runs.")
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        loop_vars = shared_properties.create_loop_settings_ui(parent_frame, config, self.loc, available_vars)
        property_vars.update(loop_vars)
        return property_vars
    def get_dynamic_output_schema(self, config):
        schema = []
        rules_str = config.get('extraction_rules', '')
        rules = [line.strip() for line in rules_str.split('\n') if line.strip()]
        for rule in rules:
            parts = rule.split(':', 1)
            if len(parts) == 2:
                data_name = parts[0].strip()
                rule_body = parts[1].strip()
                data_type = "list" if "[list]" in rule_body else "string"
                schema.append({
                    "name": f"data.scraped_data.{data_name}",
                    "type": data_type,
                    "description": f"Data '{data_name}' scraped from the web."
                })
        return schema
    def get_data_preview(self, config: dict):
        """
        Provides a sample of what this module might output for the Data Canvas.
        NOTE: This preview uses a simple HTTP request (requests library), not Selenium,
        to provide a fast preview without opening a browser. It may not work
        on pages that heavily rely on JavaScript to load content. This is an intentional trade-off for performance.
        """
        target_url = config.get('target_url')
        rules_str = config.get('extraction_rules', '')
        if not target_url or not target_url.startswith('http'):
            return [{"error": "Invalid or empty URL for preview."}]
        try:
            response = self.kernel.network.get(target_url, caller_module_id=self.module_id, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            rules = [line.strip() for line in rules_str.split('\n') if line.strip()]
            if not rules:
                return [{"status": "No extraction rules defined."}]
            is_list_scrape = any('[list]' in rule for rule in rules)
            if is_list_scrape:
                first_rule_selector = rules[0].split(':', 1)[1].strip().split('[')[0].strip()
                parent_selector_parts = first_rule_selector.split(' ')
                parent_selector = " ".join(parent_selector_parts[:-1]) if len(parent_selector_parts) > 1 else first_rule_selector
                containers = soup.select(parent_selector)[:5]
                preview_data = []
                for container in containers:
                    item_data = {}
                    for rule in rules:
                        data_name, rule_body = rule.split(':', 1)
                        data_name = data_name.strip()
                        option_match = re.search(r'\[(\w+)\]', rule_body)
                        option = option_match.group(1) if option_match else 'text'
                        selector = re.sub(r'\s*\[\w+\]\s*$', '', rule_body).strip()
                        element = container.select_one(selector.replace(parent_selector, '').strip())
                        if element:
                            item_data[data_name] = element.get_text(strip=True) if option == 'text' else element.get(option, '')
                        else:
                            item_data[data_name] = None
                    preview_data.append(item_data)
                return preview_data
            else:
                preview_data = {}
                for rule in rules:
                    data_name, rule_body = rule.split(':', 1)
                    data_name = data_name.strip()
                    option_match = re.search(r'\[(\w+)\]', rule_body)
                    option = option_match.group(1) if option_match else 'text'
                    selector = re.sub(r'\s*\[\w+\]\s*$', '', rule_body).strip()
                    element = soup.select_one(selector)
                    if element:
                        preview_data[data_name] = element.get_text(strip=True) if option == 'text' else element.get(option, '')
                    else:
                        preview_data[data_name] = "Not Found"
                return [preview_data]
        except Exception as e:
            return [{"error": f"Preview failed: {str(e)}"}]
