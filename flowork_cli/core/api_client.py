#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_cli\core\api_client.py
# JUMLAH BARIS : 37
#######################################################################

import requests
import json
import os
class ApiClient:
    """
    A client to interact with the local Flowork API server.
    This version is completely decoupled from the kernel.
    """
    def __init__(self, base_url="http://localhost:8989/api/v1"):
        self.base_url = base_url
    def _handle_response(self, response):
        """A helper to handle JSON responses and potential errors."""
        if 200 <= response.status_code < 300:
            if response.status_code == 204 or not response.content:
                return True, {}
            return True, response.json()
        else:
            try:
                error_data = response.json()
                message = error_data.get("error", "Unknown API error")
            except json.JSONDecodeError:
                message = response.text
            return False, message
    def get_server_status(self):
        """Pings the server to check if it's alive."""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=3)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
