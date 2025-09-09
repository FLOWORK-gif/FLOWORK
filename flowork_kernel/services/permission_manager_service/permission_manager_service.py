#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\permission_manager_service\permission_manager_service.py
# JUMLAH BARIS : 69
#######################################################################

import os
import json
import base64
from ..base_service import BaseService
from flowork_kernel.exceptions import PermissionDeniedError
import hashlib
class PermissionManagerService(BaseService):
    """
    The central gatekeeper for all capability-based permissions.
    [REFACTORED V3] Now receives its rules from the LicenseManagerService at startup.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.permission_rules = {} # (MODIFIKASI) Starts empty
        self.is_compromised = False # (MODIFIKASI) Will be set if rules are not loaded
        self.capability_display_map = {
            "web_scraping_advanced": "Advanced Web Scraping (Selenium)",
            "time_travel_debugger": "Time-Travel Debugger",
            "screen_recorder": "Screen Recorder",
            "unlimited_api": "Unlimited API & Webhooks",
            "preset_versioning": "Preset Version Management",
            "ai_provider_access": "AI Provider Access (Gemini, etc)",
            "ai_local_models": "Run Local AI Models (GGUF, etc)",
            "ai_copilot": "AI Co-pilot Analysis",
            "marketplace_upload": "Upload to Marketplace",
            "video_processing": "Advanced Video Processing",
            "ai_architect": "AI Architect (Workflow Generator)",
            "core_compiler": "Core Workflow Compiler",
            "module_generator": "Module Generator"
        }
    def load_rules_from_source(self, rules_dict):
        """Loads the permission rules provided by an external source (like LicenseManager)."""
        if rules_dict and 'capabilities' in rules_dict:
            self.permission_rules = rules_dict['capabilities']
            self.is_compromised = False
            self.logger(f"PermissionManager: Loaded {len(self.permission_rules)} capability rules from source.", "SUCCESS") # English Log
        else:
            self.permission_rules = {}
            self.is_compromised = True
            self.logger("PermissionManager: Received empty or invalid rules. Entering secure mode.", "CRITICAL") # English Log
    def check_permission(self, capability: str, is_system_call: bool = False) -> bool:
        """
        Checks if the current user has the required tier for a specific capability.
        """
        if is_system_call:
            return True
        if self.is_compromised:
            error_msg = self.loc.get('permission_denied_secure_mode', fallback="Access Denied due to secure mode. Please check license file signature.")
            raise PermissionDeniedError(error_msg)
        required_tier = self.permission_rules.get(capability)
        if not required_tier:
            return True
        user_tier = self.kernel.license_tier
        if not self.kernel.is_tier_sufficient(required_tier):
            capability_name = self.capability_display_map.get(capability, capability.replace('_', ' ').title())
            error_msg = self.loc.get('permission_denied_detailed',
                                     fallback="Access Denied. The '{capability}' feature requires a '{required_tier}' license, but your current tier is '{user_tier}'.",
                                     capability=capability_name,
                                     required_tier=required_tier.capitalize(),
                                     user_tier=user_tier.capitalize())
            raise PermissionDeniedError(error_msg)
        return True
