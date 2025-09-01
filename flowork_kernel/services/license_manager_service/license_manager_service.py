#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\license_manager_service\license_manager_service.py
# JUMLAH BARIS : 262
#######################################################################

import os
import json
import base64
import uuid
import platform
import hashlib
import time
import datetime
import requests
import shutil
from tkinter import messagebox
from ..base_service import BaseService
from flowork_kernel.exceptions import SignatureVerificationError
from flowork_kernel.api_client import ApiClient
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from flowork_kernel.kernel import Kernel
try:
    from cryptography.hazmat.primitives import hashes as crypto_hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
class LicenseManagerService(BaseService):
    LICENSE_PUBLIC_KEY_PEM_STRING = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAysqZG2+F82W0TgLHmF3Y
0GRPEZvXvmndTY84N/wA1ljt+JxMBVsmcVTkv8f1TrmFRD19IDzl2Yzb2lgqEbEy
GFxHhudC28leDsVEIp8B+oYWVm8Mh242YKYK8r5DAvr9CPQivnIjZ4BWgKKddMTd
harVxLF2CoSoTs00xWKd6VlXfoW9wdBvoDVifL+hCMepgLLdQQE4HbamPDJ3bpra
pCgcAD5urmVoJEUJdjd+Iic27RBK7jD1dWDO2MASMh/0IyXyM8i7RDymQ88gZier
U0OdWzeCWGyl4EquvR8lj5GNz4vg2f+oEY7h9AIC1f4ARtoihc+apSntqz7nAqa/
sQIDAQAB
-----END PUBLIC KEY-----"""
    REMOTE_CONFIG_PUBLIC_KEY_PEM_STRING = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAysqZG2+F82W0TgLHmF3Y
0GRPEZvXvmndTY84N/wA1ljt+JxMBVsmcVTkv8f1TrmFRD19IDzl2Yzb2lgqEbEy
GFxHhudC28leDsVEIp8B+oYWVm8Mh242YKYK8r5DAvr9CPQivnIjZ4BWgKKddMTd
harVxLF2CoSoTs00xWKd6VlXfoW9wdBvoDVifL+hCMepgLLdQQE4HbamPDJ3bpra
pCgcAD5urmVoJEUJdjd+Iic27RBK7jD1dWDO2MASMh/0IyXyM8i7RDymQ88gZier
U0OdWzeCWGyl4EquvR8lj5GNz4vg2f+oEY7h9AIC1f4ARtoihc+apSntqz7nAqa/
sQIDAQAB
-----END PUBLIC KEY-----"""
    LICENSE_FILE_NAME = "license.seal"
    REMOTE_TIER_CONFIG_URL = "https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/flowork_tier_config.json"
    REMOTE_TIER_SIGNATURE_URL = "https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/flowork_tier_config.sig"
    def __init__(self, kernel: 'Kernel', service_id: str):
        super().__init__(kernel, service_id)
        self.logger = self.kernel.write_to_log
        self.license_public_key = None
        self.config_public_key = None
        self.license_data = {}
        self.is_local_license_valid = False
        self.server_error = None
        self.remote_permission_rules = None
        self.api_client = ApiClient(kernel=self.kernel)
        self._load_public_keys()
    def _fetch_remote_tier_config(self):
        try:
            self.logger("LicenseManager: Fetching remote tier configuration and signature...", "INFO")
            config_response = requests.get(self.REMOTE_TIER_CONFIG_URL, timeout=10)
            config_response.raise_for_status()
            config_content_bytes = config_response.content
            sig_response = requests.get(self.REMOTE_TIER_SIGNATURE_URL, timeout=10)
            sig_response.raise_for_status()
            signature_b64 = sig_response.text.strip()
            if not self.config_public_key:
                raise SignatureVerificationError("Config public key is not loaded. Cannot verify remote config.")
            signature_bytes = base64.b64decode(signature_b64)
            self.config_public_key.verify(signature_bytes, config_content_bytes, padding.PKCS1v15(), crypto_hashes.SHA256())
            self.remote_permission_rules = json.loads(config_content_bytes)
            self.logger("LicenseManager: Remote tier configuration loaded and signature VERIFIED successfully.", "SUCCESS")
            return True
        except Exception as e:
            self.logger(f"LicenseManager: CRITICAL: Could not fetch or verify remote config: {e}. Defaulting to SECURE mode (Monetization ON).", "CRITICAL")
            self.remote_permission_rules = {"monetization_active": True}
            return False
    def verify_license_on_startup(self):
        self.logger("LicenseManager: Starting license verification process V6 (Expiry Aware)...", "INFO")
        self._fetch_remote_tier_config()
        monetization_is_active = self.remote_permission_rules and self.remote_permission_rules.get("monetization_active", True)
        if not monetization_is_active:
            override_tier = self.remote_permission_rules.get("default_tier_override", "architect")
            self.kernel.is_premium = True
            self.kernel.license_tier = override_tier
            self.logger(f"Monetization is INACTIVE. Granting full access with tier: '{override_tier}'.", "WARN")
            return
        self.logger("Monetization is ACTIVE. Verifying user's tier...", "INFO")
        if self.kernel.current_user:
            user_tier = self.kernel.current_user.get('tier', 'free')
            expires_at_str = self.kernel.current_user.get('license_expires_at')
            is_expired = False
            if expires_at_str:
                try:
                    expiry_date = datetime.datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                    if datetime.datetime.now(datetime.timezone.utc) > expiry_date:
                        is_expired = True
                        self.logger(f"User {self.kernel.current_user.get('email')}'s license has EXPIRED on {expiry_date}.", "WARN")
                except Exception as e:
                    self.logger(f"Could not parse license expiry date '{expires_at_str}': {e}", "ERROR")
            if is_expired:
                user_tier = 'free'
            self.kernel.license_tier = user_tier
            self.kernel.is_premium = self.kernel.TIER_HIERARCHY.get(user_tier, 0) > 0
            self.logger(f"User is logged in. Tier confirmed as '{user_tier.upper()}'.", "SUCCESS")
            return
        local_data = self._verify_local_license_file()
        if local_data:
            self.logger("Local license file found and signature is valid. Now verifying activation status with server...", "INFO")
            license_key = local_data.get('license_key')
            machine_id = self._get_machine_id()
            if not license_key:
                self.logger("Local license is invalid (missing license_key). Deleting file.", "ERROR")
                os.remove(self._get_license_file_path())
                self.is_local_license_valid = False
            else:
                is_valid_on_server, server_message = self.validate_local_license_online(license_key, machine_id)
                if is_valid_on_server:
                    self.is_local_license_valid = True
                    self.license_data = local_data
                    self.kernel.license_tier = local_data.get('tier', 'free')
                    self.kernel.is_premium = self.kernel.TIER_HIERARCHY.get(self.kernel.license_tier, 0) > 0
                    self.logger(f"Server confirmed license activation. Tier set to '{self.kernel.license_tier.upper()}'.", "SUCCESS")
                else:
                    self.logger(f"Server rejected local license. Reason: {server_message}. Deleting local license file.", "WARN")
                    os.remove(self._get_license_file_path())
                    self.is_local_license_valid = False
                    self.kernel.is_premium = False
                    self.kernel.license_tier = "free"
        else:
            self.is_local_license_valid = False
            self.kernel.is_premium = False
            self.kernel.license_tier = "free"
            self.logger("No logged-in user and no valid local license. App will run in free mode.", "WARN")
    def _load_public_keys(self):
        if not CRYPTO_AVAILABLE:
            self.logger("Cryptography library not found. Security features will be disabled.", "CRITICAL")
            return
        try:
            pem_data = self.LICENSE_PUBLIC_KEY_PEM_STRING.strip().encode('utf-8')
            self.license_public_key = serialization.load_pem_public_key(pem_data)
            self.logger("Public key for license verification loaded successfully.", "SUCCESS")
        except Exception as e:
            self.license_public_key = None
            self.logger(f"Failed to load license public key: {e}. License verification will fail.", "ERROR")
        try:
            pem_data = self.REMOTE_CONFIG_PUBLIC_KEY_PEM_STRING.strip().encode('utf-8')
            self.config_public_key = serialization.load_pem_public_key(pem_data)
            self.logger("Public key for remote config verification loaded successfully.", "SUCCESS")
        except Exception as e:
            self.config_public_key = None
            self.logger(f"Failed to load remote config public key: {e}. Remote config verification will fail.", "ERROR")
    def _get_machine_id(self) -> str:
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])
            machine_id = hashlib.sha256(mac.encode()).hexdigest()
            self.logger(f"Generated Machine ID: {machine_id[:12]}...", "DEBUG")
            return machine_id
        except Exception as e:
            self.logger(f"Could not generate machine ID: {e}. Using a fallback ID.", "WARN")
            return hashlib.sha256("fallback_flowork_synapse_id".encode()).hexdigest()
    def _get_license_file_path(self):
        return os.path.join(self.kernel.data_path, self.LICENSE_FILE_NAME)
    def _verify_local_license_file(self):
        if not self.license_public_key: return None
        license_path = self._get_license_file_path()
        if not os.path.exists(license_path): return None
        try:
            with open(license_path, 'r', encoding='utf-8') as f: content = json.load(f)
            data_to_verify = content.get('data'); signature_b64 = content.get('signature')
            if not data_to_verify or not signature_b64: return None
            data_bytes = json.dumps(data_to_verify, separators=(',', ':')).encode('utf-8')
            signature_bytes = base64.b64decode(signature_b64)
            self.license_public_key.verify(signature_bytes, data_bytes, padding.PKCS1v15(), crypto_hashes.SHA256())
            return data_to_verify
        except Exception as e:
            self.logger(f"CRITICAL: License file tampered with or invalid. Deleting it. Error: {e}", "CRITICAL")
            try: os.remove(license_path)
            except OSError: pass
            return None
    def validate_local_license_online(self, license_key: str, machine_id: str) -> (bool, str):
        self.logger(f"Validating license key '{license_key[:8]}...' for machine '{machine_id[:8]}...' with Supabase.", "INFO")
        function_url = f"{self.api_client.supabase_url}/functions/v1/validate-license-activation"
        headers = self.api_client._get_supabase_headers()
        payload = {"license_key": license_key, "machine_id": machine_id}
        try:
            response = requests.post(function_url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                return True, "License is valid for this machine."
            else:
                error_msg = response.json().get("error", "Unknown validation error.")
                return False, error_msg
        except requests.exceptions.RequestException as e:
            return False, f"Could not connect to validation server: {e}"
        except Exception as e:
            return False, f"An unexpected error occurred during validation: {e}"
    def activate_license_on_server(self, full_license_content: dict):
        if not self.kernel.current_user or not self.kernel.current_user.get('session_token'):
            return False, "You must be logged in to activate a new license."
        self.logger("Attempting to activate license via Supabase Edge Function...", "INFO")
        function_url = f"{self.api_client.supabase_url}/functions/v1/activate-license"
        session_token = self.kernel.current_user.get('session_token')
        headers = {
            'Authorization': f'Bearer {session_token}',
            'apikey': self.api_client.supabase_key,
            'Content-Type': 'application/json'
        }
        payload = {
            "license_content": full_license_content,
            "machine_id": self._get_machine_id()
        }
        try:
            response = requests.post(function_url, headers=headers, json=payload, timeout=20)
            if response.status_code != 200:
                error_msg = response.json().get("error", "Unknown activation error from server.")
                raise Exception(error_msg)
            with open(self._get_license_file_path(), 'w', encoding='utf-8') as f:
                json.dump(full_license_content, f, indent=4)
            self.logger("License activated on Supabase and file saved locally.", "SUCCESS")
            success_refresh, user_data = self.api_client.get_user_profile_by_token(session_token)
            if success_refresh:
                self.kernel.current_user = user_data
                self.verify_license_on_startup()
            return True, "License activated successfully. Please restart the application."
        except Exception as e:
            self.logger(f"Supabase function call for activation failed: {e}", "ERROR")
            return False, f"Could not activate license on server: {e}"
    def deactivate_license_on_server(self):
        if not self.kernel.current_user or not self.kernel.current_user.get('session_token'):
            return False, "You must be logged in to deactivate a license."
        function_url = f"{self.api_client.supabase_url}/functions/v1/deactivate-license"
        session_token = self.kernel.current_user.get('session_token')
        headers = {
            'Authorization': f'Bearer {session_token}',
            'apikey': self.api_client.supabase_key
        }
        try:
            response = requests.post(function_url, headers=headers, timeout=20)
            if response.status_code != 200:
                raise Exception(response.json().get("error", "Unknown deactivation error from server."))
            local_license_path = self._get_license_file_path()
            if os.path.exists(local_license_path):
                os.remove(local_license_path)
            self.logger("Deactivation success, updating kernel state immediately.", "INFO")
            self.kernel.license_tier = "free"
            self.kernel.is_premium = False
            if self.kernel.current_user:
                self.kernel.current_user['tier'] = 'free'
            event_bus = self.kernel.get_service("event_bus")
            if event_bus:
                event_bus.publish("REQUEST_CLEANUP_AND_EXIT", {"reason": "deactivation"})
            return True, "License deactivated successfully. The application will now close."
        except Exception as e:
            self.logger(f"Supabase function call for deactivation failed: {e}", "ERROR")
            return False, f"An error occurred during deactivation: {e}"
