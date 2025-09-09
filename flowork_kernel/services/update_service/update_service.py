#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\update_service\update_service.py
# JUMLAH BARIS : 153
#######################################################################

import os
import json
import hashlib
import requests
from ..base_service import BaseService
import threading
import base64
try:
    from cryptography.hazmat.primitives import hashes as crypto_hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
class UpdateService(BaseService):
    """
    (REMASTERED V2) Handles the SECURE automatic update process.
    It now fetches a signature file and cryptographically verifies the
    fingerprint manifest before trusting it, preventing tampering.
    Also respects a 'devmode.on' file to skip updates.
    """
    UPDATE_SIGNATURE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAysqZG2+F82W0TgLHmF3Y
0GRPEZvXvmndTY84N/wA1ljt+JxMBVsmcVTkv8f1TrmFRD19IDzl2Yzb2lgqEbEy
GFxHhudC28leDsVEIp8B+oYWVm8Mh242YKYK8r5DAvr9CPQivnIjZ4BWgKKddMTd
harVxLF2CoSoTs00xWKd6VlXfoW9wdBvoDVifL+hCMepgLLdQQE4HbamPDJ3bpra
pCgcAD5urmVoJEUJdjd+Iic27RBK7jD1dWDO2MASMh/0IyXyM8i7RDymQ88gZier
U0OdWzeCWGyl4EquvR8lj5GNz4vg2f+oEY7h9AIC1f4ARtoihc+apSntqz7nAqa/
sQIDAQAB
-----END PUBLIC KEY-----"""
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.repo_owner = "FLOWORK-gif"
        self.repo_name = "FLOWORK"
        self.branch = "main"
        self.fingerprint_filename = "file_fingerprints.json"
        self.signature_filename = "file_fingerprints.sig"
        self.dev_mode_file = "devmode.on"
        self.public_key = self._load_public_key()
    def _load_public_key(self):
        if not CRYPTO_AVAILABLE:
            self.logger("UpdateService: Cryptography library not found. Signature verification will be skipped.", "CRITICAL")
            return None
        try:
            pem_data = self.UPDATE_SIGNATURE_PUBLIC_KEY.strip().encode('utf-8')
            return serialization.load_pem_public_key(pem_data)
        except Exception as e:
            self.logger(f"UpdateService: Failed to load public key for update verification: {e}", "CRITICAL")
            return None
    def _calculate_local_sha256(self, file_path):
        """Calculates the SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except IOError:
            return None
    def _get_verified_remote_fingerprints(self):
        """Downloads the fingerprint manifest and its signature, then verifies them."""
        if not self.public_key:
            self.logger("Update verification skipped: Public key not available.", "ERROR")
            return None # Cannot proceed without the public key
        fingerprint_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}/{self.fingerprint_filename}"
        signature_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}/{self.signature_filename}"
        try:
            self.logger(f"UpdateService: Fetching fingerprints from {fingerprint_url}", "INFO")
            fp_response = requests.get(fingerprint_url, timeout=15)
            fp_response.raise_for_status()
            fingerprint_content_bytes = fp_response.content
            self.logger(f"UpdateService: Fetching signature from {signature_url}", "INFO")
            sig_response = requests.get(signature_url, timeout=15)
            sig_response.raise_for_status()
            signature_b64 = sig_response.text.strip()
            signature_bytes = base64.b64decode(signature_b64)
            self.public_key.verify(
                signature_bytes,
                fingerprint_content_bytes,
                padding.PKCS1v15(),
                crypto_hashes.SHA256()
            )
            self.logger("UpdateService: Remote fingerprint signature VERIFIED successfully.", "SUCCESS")
            return json.loads(fingerprint_content_bytes)
        except InvalidSignature:
            self.logger("UpdateService: BENTENG BAJA FAILED! The remote fingerprint file has an INVALID signature. Update process aborted for security.", "CRITICAL")
            return None
        except requests.exceptions.RequestException as e:
            self.logger(f"UpdateService: Could not connect to GitHub to check for updates: {e}", "ERROR")
            return None
        except (json.JSONDecodeError, base64.binascii.Error) as e:
            self.logger(f"UpdateService: Fingerprint or signature file is corrupted. Error: {e}", "ERROR")
            return None
        except Exception as e:
            self.logger(f"UpdateService: An unexpected error occurred during verification: {e}", "CRITICAL")
            return None
    def _download_file(self, relative_path):
        """Downloads a single file from the GitHub repo and saves it locally."""
        url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}/{relative_path}"
        local_path = os.path.join(self.kernel.project_root_path, relative_path.replace('/', os.sep))
        self.logger(f"  -> Downloading update for: {relative_path}", "INFO")
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return True
        except requests.exceptions.RequestException as e:
            self.logger(f"    [FAIL] Could not download '{relative_path}': {e}", "ERROR")
            return False
    def run_update_check(self):
        """
        The main method called by StartupService to perform the update.
        """
        if self.kernel.is_dev_mode:
            self.logger("DEVELOPER MODE ACTIVE: Auto-update check is disabled.", "WARN")
            return
        self.logger("--- Starting SECURE Automatic Update Check ---", "INFO")
        remote_fingerprints = self._get_verified_remote_fingerprints()
        if not remote_fingerprints:
            self.logger("Could not get or verify remote version info. Skipping update. The application might be offline or the remote files are compromised.", "WARN")
            return
        files_to_update = []
        for relative_path, remote_hash in remote_fingerprints.items():
            local_path = os.path.join(self.kernel.project_root_path, relative_path.replace('/', os.sep))
            if not os.path.exists(local_path):
                files_to_update.append({'path': relative_path, 'reason': 'New file'})
            else:
                local_hash = self._calculate_local_sha256(local_path)
                if local_hash != remote_hash:
                    files_to_update.append({'path': relative_path, 'reason': 'File changed'})
        if not files_to_update:
            self.logger("Application is up to date. No new files to download.", "SUCCESS")
            return
        self.logger(f"Found {len(files_to_update)} file(s) to update/add. Starting download process...", "WARN")
        success_count = 0
        for file_info in files_to_update:
            if self._download_file(file_info['path']):
                success_count += 1
        self.logger(f"Update process finished. {success_count}/{len(files_to_update)} files updated successfully.", "SUCCESS")
        if success_count > 0:
            event_bus = self.kernel.get_service("event_bus")
            if event_bus:
                self.logger("Files were updated. Requesting application restart...", "WARN")
                self.kernel.root.after(2000, lambda: event_bus.publish("RESTART_APP_AFTER_UPDATE", {"message": f"{success_count} file(s) have been updated."}))
