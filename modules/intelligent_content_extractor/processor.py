#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\intelligent_content_extractor\processor.py
# (Full code for the modified file)
#######################################################################
from flowork_kernel.api_contract import BaseModule
from flowork_kernel.core.input_schema import create_input_schema, InputVar
from flowork_kernel.core.output_schema import create_output_schema, OutputVar
from flowork_kernel.core import build_security
import importlib.util

# (COMMENT) We check for the library's existence once at the module level.
try:
    import undetected_chromedriver as uc
    from bs4 import BeautifulSoup
    LIBRARIES_AVAILABLE = True
except ImportError:
    LIBRARIES_AVAILABLE = False


# [FIXED] Renamed class to match the manifest.json entry_point
class IntelligentContentExtractorModule(BaseModule):
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        # build_security.perform_runtime_check(__file__) # COMMENT: This line seems duplicated, commenting out the second one.
        super().__init__(module_id, services)
        self.logger = services.get("logger")

        # (COMMENT) The dependency check is removed from __init__ to prevent startup crashes.
        # It will now be checked inside the execute method.

        build_security.perform_runtime_check(__file__)

        self.input_schema = create_input_schema(
            url=InputVar(display_name="Target URL", var_type="string", required=True, description="The full URL of the web page to extract content from."),
            extraction_prompt=InputVar(display_name="Extraction Prompt", var_type="string", required=True, description="A detailed natural language prompt describing what to extract (e.g., 'Extract the main article text, excluding comments and ads').")
        )
        self.output_schema = create_output_schema(
            extracted_content=OutputVar(display_name="Extracted Content", var_type="string", description="The cleaned and extracted content from the web page.")
        )

    def execute(self, payload, abort_signal):
        # (MODIFIED) The dependency check now happens here, at runtime.
        if not LIBRARIES_AVAILABLE:
            error_msg = "'undetected-chromedriver' and 'beautifulsoup4' libraries are required for this module."
            self.logger(f"FATAL: {error_msg}", "CRITICAL") # English Log
            # (COMMENT) Instead of raising an exception, we return a standardized error payload.
            # This makes the workflow more resilient.
            return self.error_payload(error_msg)

        url = self.input_schema.get_var('url', payload)
        extraction_prompt = self.input_schema.get_var('extraction_prompt', payload)
        self.logger(f"Starting intelligent extraction from URL: {url}", "INFO") # English Log

        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = uc.Chrome(options=options)

            driver.get(url)
            page_source = driver.page_source
            driver.quit()

            soup = BeautifulSoup(page_source, 'html.parser')
            # (COMMENT) A more robust way to get text, joining paragraphs.
            all_text = ' '.join(p.get_text() for p in soup.find_all('p'))

            # (COMMENT) This is where the AI part comes in. We ask the AI to clean the text.
            ai_provider_manager = self.kernel.get_service("ai_provider_manager_service")
            if not ai_provider_manager:
                return self.error_payload("AI Provider Manager service is not available.") # English Log

            # (COMMENT) Using the text-specialized model for cleaning.
            ai_response = ai_provider_manager.query_ai_by_task(
                task_type='text',
                prompt=f"Here is the raw text from a webpage:\n\n---\n{all_text}\n---\n\nBased on the following instruction, please clean and extract only the relevant information:\n\nINSTRUCTION: {extraction_prompt}\n\nReturn ONLY the cleaned text."
            )

            if "error" in ai_response:
                return self.error_payload(f"AI failed to process the content: {ai_response['error']}") # English Log

            cleaned_content = ai_response.get("data", "")
            self.logger("Successfully extracted and cleaned content using AI.", "SUCCESS") # English Log
            return self.success_payload({"extracted_content": cleaned_content})

        except Exception as e:
            self.logger(f"An error occurred during web extraction: {e}", "ERROR") # English Log
            return self.error_payload(str(e))

_UNUSED_SIGNATURE = 'AOLA_FLOWORK_OFFICIAL_BUILD_2025_TEETAH_ART' # Embedded Signature


# _UNUSED_SIGNATURE = 'AOLA_FLOWORK_OFFICIAL_BUILD_2025_TEETAH_ART' # Embedded Signature # COMMENT: Duplicated line