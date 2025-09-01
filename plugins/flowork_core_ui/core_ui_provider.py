#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\core_ui_provider.py
# JUMLAH BARIS : 155
#######################################################################

from flowork_kernel.api_contract import BaseModule, BaseUIProvider
from plugins.flowork_core_ui.settings_tab import SettingsTab
from plugins.flowork_core_ui.template_manager_page import TemplateManagerPage
from plugins.flowork_core_ui.generator_page import GeneratorPage
from plugins.flowork_core_ui.trigger_manager_page import TriggerManagerPage
from plugins.flowork_core_ui.marketplace_page import MarketplacePage
from plugins.flowork_core_ui.ai_architect_page import AiArchitectPage
from plugins.flowork_core_ui.core_editor_page import CoreEditorPage
from plugins.flowork_core_ui.pricing_page import PricingPage
from plugins.flowork_core_ui.ai_trainer_page import AITrainerPage
from plugins.flowork_core_ui.model_converter_page import ModelConverterPage
from plugins.flowork_core_ui.prompt_manager_page import PromptManagerPage
class CoreUIProvider(BaseModule, BaseUIProvider):
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        if hasattr(self, 'logger') and callable(self.logger):
            self.logger("Core UI Provider plugin loaded successfully.", "SUCCESS")
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        status_updater("No action", "INFO")
        return payload
    def get_ui_tabs(self):
        """
        Reports all the pages (tabs) that this provider can create to the Kernel.
        """
        if hasattr(self, 'logger') and callable(self.logger):
            self.logger("CoreUIProvider: Kernel is requesting the list of pages I provide.", "DEBUG")
        all_pages = [
            {
                "key": "settings",
                "title": self.loc.get('settings_tab_title', fallback="Settings"),
                "frame_class": SettingsTab
            },
            {
                "key": "trigger_manager",
                "title": self.loc.get('trigger_manager_page_title', fallback="Trigger Management"),
                "frame_class": TriggerManagerPage
            },
            {
                "key": "prompt_manager",
                "title": self.loc.get('menu_title_prompt_manager', fallback="Prompt Manager"),
                "frame_class": PromptManagerPage
            },
            {
                "key": "template_manager",
                "title": self.loc.get('template_manager_page_title', fallback="Template Management"),
                "frame_class": TemplateManagerPage
            },
            {
                "key": "generator",
                "title": self.loc.get('generator_page_title', fallback="Generator Tools"),
                "frame_class": GeneratorPage
            },
            {
                "key": "marketplace",
                "title": self.loc.get('marketplace_page_title', fallback="Marketplace"),
                "frame_class": MarketplacePage
            },
            {
                "key": "ai_architect",
                "title": self.loc.get('ai_architect_page_title', fallback="AI Architect"),
                "frame_class": AiArchitectPage
            },
            {
                "key": "ai_trainer",
                "title": self.loc.get('menu_open_ai_trainer', fallback="AI Trainer"),
                "frame_class": AITrainerPage
            },
            {
                "key": "model_converter",
                "title": self.loc.get('menu_open_model_factory', fallback="Model Factory"),
                "frame_class": ModelConverterPage
            },
            {
                "key": "core_editor",
                "title": self.loc.get('core_editor_page_title', fallback="Core Editor"),
                "frame_class": CoreEditorPage
            },
            {
                "key": "pricing_page",
                "title": self.loc.get('pricing_page_title', fallback="Upgrade Plan"),
                "frame_class": PricingPage
            }
        ]
        license_manager = self.kernel.get_service("license_manager_service") # (FIXED) Using self.kernel.get_service
        monetization_is_active = license_manager and license_manager.remote_permission_rules and license_manager.remote_permission_rules.get("monetization_active")
        final_pages_to_show = []
        for page in all_pages:
            if page['key'] == 'pricing_page' and not monetization_is_active:
                self.logger(f"UI: Monetization is inactive, hiding page: {page['key']}", "DEBUG")
                continue # Skip adding this page to the final list.
            final_pages_to_show.append(page)
        return final_pages_to_show
    def get_menu_items(self):
        """
        Adds menu items for all managed pages.
        """
        tab_manager = self.kernel.get_service("tab_manager_service")
        all_items = [
            {
                "parent": self.loc.get('menu_ai_tools', fallback="AI Tools"),
                "add_separator": True,
                "label": self.loc.get('menu_title_prompt_manager', fallback="Prompt Manager"),
                "command": lambda: tab_manager.open_managed_tab('prompt_manager')
            },
            {
                "parent": self.loc.get('menu_ai_tools', fallback="AI Tools"),
                "label": self.loc.get('menu_open_ai_architect', fallback="Open AI Architect"),
                "command": lambda: tab_manager.open_managed_tab('ai_architect')
            },
            {
                "parent": self.loc.get('menu_ai_tools', fallback="AI Tools"),
                "add_separator": True,
                "label": self.loc.get('menu_open_ai_trainer', fallback="Open AI Trainer"),
                "command": lambda: tab_manager.open_managed_tab('ai_trainer')
            },
            {
                "parent": self.loc.get('menu_ai_tools', fallback="AI Tools"),
                "label": self.loc.get('menu_open_model_factory', fallback="Open Model Factory"),
                "command": lambda: tab_manager.open_managed_tab('model_converter')
            },
            {
                "parent": self.loc.get('menu_ai_tools', fallback="AI Tools"),
                "add_separator": True,
                "label": self.loc.get('menu_open_generator', fallback="Open Module Factory"),
                "command": lambda: tab_manager.open_managed_tab('generator')
            },
            {
                "parent": self.loc.get('menu_developer', fallback="Developer"),
                "label": self.loc.get('menu_open_core_editor', fallback="Open Core Workflow Editor"),
                "command": lambda: tab_manager.open_managed_tab('core_editor')
            },
            {
                "parent": self.loc.get('menu_help', fallback="Help"),
                "add_separator": True,
                "label": self.loc.get('menu_open_pricing_page', fallback="View Plans & Upgrade"),
                "command": lambda: tab_manager.open_managed_tab('pricing_page')
            }
        ]
        license_manager = self.kernel.get_service("license_manager_service") # (FIXED) Using self.kernel.get_service
        monetization_is_active = license_manager and license_manager.remote_permission_rules and license_manager.remote_permission_rules.get("monetization_active")
        final_items_to_show = []
        for item in all_items:
            if item['label'] == self.loc.get('menu_open_pricing_page', fallback="View Plans & Upgrade") and not monetization_is_active:
                self.logger(f"UI: Monetization is inactive, hiding menu item: {item['label']}", "DEBUG")
                continue # Skip this commercial item.
            final_items_to_show.append(item)
        return final_items_to_show
