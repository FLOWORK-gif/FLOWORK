from flowork_kernel.core import build_security
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\ai_providers\text\chatgpt_provider\provider.py
# JUMLAH BARIS : 36
#######################################################################

from flowork_kernel.api_contract import BaseAIProvider
from .core.ChatGPTConnection import ChatGPTConnection
class ChatGPTProvider(BaseAIProvider):
    """
    Provides a connection to OpenAI's ChatGPT models.
    """
    def __init__(self, kernel, manifest: dict):
        build_security.perform_runtime_check(__file__)
        super().__init__(kernel, manifest)
        self.connection = ChatGPTConnection(self.kernel)
    def get_provider_name(self) -> str:
        return "OpenAI ChatGPT"
    def is_ready(self) -> tuple[bool, str]:
        """Checks if the OpenAI API key is configured."""
        if self.connection.configure():
            return (True, "")
        else:
            return (False, "ChatGPT Provider is not configured. Check for a valid OPENAI_API_KEY in Settings.")
    def generate_response(self, prompt: str) -> dict:
        """
        Processes a prompt using ChatGPT and returns a standardized dictionary.
        """
        is_ready, message = self.is_ready()
        if not is_ready:
            return {"type": "text", "data": f"ERROR: {message}"}
        response_dict = self.connection.get_chat_completion(prompt)
        if "error" in response_dict:
            return {"type": "text", "data": f"CHATGPT_API_ERROR: {response_dict['error']}"}
        else:
            return {"type": "text", "data": response_dict['data']}