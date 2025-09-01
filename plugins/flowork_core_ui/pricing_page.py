#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\pricing_page.py
# JUMLAH BARIS : 151
#######################################################################

import ttkbootstrap as ttk
import webbrowser
import os
from dotenv import load_dotenv
class PricingPage(ttk.Frame):
    """
    A UI frame that displays the different license tiers and their features,
    with dynamic buttons based on the user's current license.
    (MODIFIED) Redesigned with a more persuasive, benefit-driven, and cinematic narrative.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, padding=20)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.feature_groups = {
            "foundation": {
                "title_key": "feature_group_foundation",
                "features": ["feature_visual_editor", "feature_basic_modules", "feature_manual_install", "feature_theme_customization", "feature_limited_api"]
            },
            "connectivity": {
                "title_key": "feature_group_connectivity",
                "features": ["feature_unlimited_api", "feature_headless_mode"]
            },
            "powerhouse": {
                "title_key": "feature_group_powerhouse",
                "features": ["feature_time_travel_debugger", "feature_preset_versioning", "screen_recorder", "web_scraping_advanced"]
            },
            "intelligence": {
                "title_key": "feature_group_intelligence",
                "features": ["feature_ai_copilot", "ai:provider_access", "ai:local_models", "feature_marketplace_upload", "video_processing"]
            },
            "creator": {
                "title_key": "feature_group_creator",
                "features": ["feature_ai_architect", "core_compiler", "module_generator"]
            },
            "enterprise": {
                "title_key": "feature_group_enterprise",
                "features": ["feature_advanced_security", "feature_priority_support", "feature_team_collaboration"]
            }
        }
        self.tier_data = {
            "free": {
                "title_key": "tier_pemula_title", "tagline_key": "tier_pemula_tagline", "desc_key": "tier_pemula_desc_detail", "style": "secondary",
                "features": ["foundation"]
            },
            "basic": {
                "title_key": "tier_profesional_title", "tagline_key": "tier_profesional_tagline", "desc_key": "tier_profesional_desc_detail", "style": "info",
                "features": ["connectivity", "powerhouse"]
            },
            "pro": {
                "title_key": "tier_arsitek_ai_title", "tagline_key": "tier_arsitek_ai_tagline", "desc_key": "tier_arsitek_ai_desc_detail", "style": "success",
                "features": ["intelligence"]
            },
            "architect": {
                "title_key": "tier_maestro_title", "tagline_key": "tier_maestro_tagline", "desc_key": "tier_maestro_desc_detail", "style": "primary",
                "features": ["creator"]
            },
            "enterprise": {
                "title_key": "tier_titan_title", "tagline_key": "tier_titan_tagline", "desc_key": "tier_titan_desc_detail", "style": "dark",
                "features": ["enterprise"]
            }
        }
        self.base_upgrade_urls = {
            "basic": "https://www.flowork.art/harga/basic",
            "pro": "https://www.flowork.art/harga/pro",
            "architect": "https://www.flowork.art/harga/architect",
            "enterprise": "https://www.flowork.art/kontak"
        }
        self.affiliate_id = None
        affiliate_file_path = os.path.join(self.kernel.data_path, ".flowork_id")
        if os.path.exists(affiliate_file_path):
            load_dotenv(dotenv_path=affiliate_file_path)
            self.affiliate_id = os.getenv("ID_USER")
            if self.affiliate_id:
                self.kernel.write_to_log(f"Affiliate ID '{self.affiliate_id}' loaded successfully.", "SUCCESS")
        self._build_ui()
    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)
        container.columnconfigure(0, weight=2)
        container.columnconfigure(1, weight=2)
        container.columnconfigure(2, weight=3)
        container.columnconfigure(3, weight=2)
        container.columnconfigure(4, weight=2)
        container.rowconfigure(0, weight=1)
        tier_order = ["free", "basic", "pro", "architect", "enterprise"]
        for i, tier_key in enumerate(tier_order):
            data = self.tier_data[tier_key]
            is_highlighted = (tier_key == "pro")
            self._create_tier_card(container, tier_key, data, is_highlighted).grid(row=0, column=i, sticky="nsew", padx=10, pady=10)
    def _create_tier_card(self, parent, tier_key, data, is_highlighted=False):
        style = f"{data['style']}"
        card = ttk.LabelFrame(parent, text=self.loc.get(data['title_key']), padding=20, bootstyle=style)
        if is_highlighted:
            banner = ttk.Label(card, text=self.loc.get('btn_most_popular', fallback="MOST POPULAR"), bootstyle=f"inverse-{data['style']}", padding=(10, 2), font="-weight bold")
            banner.place(relx=0.5, rely=0, anchor="n", y=-15)
        tagline_text = self.loc.get(data['tagline_key'])
        ttk.Label(card, text=tagline_text, font="-size 12 -weight bold", anchor="center").pack(fill='x', pady=(10, 5))
        desc_text = self.loc.get(data['desc_key'])
        ttk.Label(card, text=desc_text, wraplength=250, justify='center', anchor='center').pack(fill='x', pady=(0, 20))
        all_features_in_tier = set()
        tier_hierarchy_keys = list(self.kernel.TIER_HIERARCHY.keys())
        current_tier_index = tier_hierarchy_keys.index(tier_key)
        for i in range(current_tier_index + 1):
            tier_to_include = tier_hierarchy_keys[i]
            for group_key in self.tier_data[tier_to_include]['features']:
                all_features_in_tier.add(group_key)
        for group_key, group_data in self.feature_groups.items():
            if group_key in all_features_in_tier:
                ttk.Label(card, text=self.loc.get(group_data['title_key']), font="-weight bold", bootstyle="secondary").pack(anchor='w', pady=(10, 2))
                for feature_key in group_data['features']:
                    if feature_key == "feature_limited_api" and self.kernel.TIER_HIERARCHY[tier_key] >= self.kernel.TIER_HIERARCHY['basic']:
                        continue
                    if feature_key == "feature_unlimited_api" and self.kernel.TIER_HIERARCHY[tier_key] < self.kernel.TIER_HIERARCHY['basic']:
                        continue
                    feature_text = self.loc.get(feature_key, fallback=feature_key.replace('_', ' ').title())
                    ttk.Label(card, text=f"✓ {feature_text}", anchor='w').pack(fill='x', padx=10)
        ttk.Frame(card).pack(fill='y', expand=True) # Spacer
        user_tier_level = self.kernel.TIER_HIERARCHY[self.kernel.license_tier]
        card_tier_level = self.kernel.TIER_HIERARCHY[tier_key]
        btn_command = None
        if user_tier_level == card_tier_level:
            btn_text = self.loc.get('btn_current_plan')
            btn_state = "disabled"
            btn_bootstyle = f"outline-{data['style']}"
        elif user_tier_level > card_tier_level:
            btn_text = self.loc.get('btn_included')
            btn_state = "disabled"
            btn_bootstyle = f"outline-{data['style']}"
        else:
            base_url = self.base_upgrade_urls.get(tier_key, "https://www.flowork.art")
            final_url = f"{base_url}?aff={self.affiliate_id}" if self.affiliate_id else base_url
            btn_command = lambda url=final_url: webbrowser.open(url)
            if tier_key == "enterprise":
                btn_text = self.loc.get('btn_contact_us')
            else:
                btn_text = self.loc.get(f'btn_upgrade_{tier_key}', fallback=f"Upgrade to {tier_key.capitalize()}")
            btn_state = "normal"
            btn_bootstyle = data['style']
        action_button = ttk.Button(card, text=btn_text, state=btn_state, command=btn_command, bootstyle=btn_bootstyle)
        action_button.pack(fill='x', ipady=8, pady=(15, 0))
        return card
