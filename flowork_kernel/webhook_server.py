#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\webhook_server.py
# JUMLAH BARIS : 142
#######################################################################

import http.server
import socketserver
import threading
import json
import logging
import uuid
import queue # (COMMENT) This import seems to be used correctly.
from urllib.parse import urlparse, unquote
class WebhookRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Handles incoming HTTP requests. Now acts as a router
    for /webhook and /api endpoints, and handles GET and POST requests.
    """
    def do_POST(self):
        """Handles all POST requests."""
        parsed_path = urlparse(self.path)
        path_parts = [part for part in unquote(parsed_path.path).strip('/').split('/') if part]
        if not path_parts:
            self._send_response(404, {"error": "Endpoint not found."})
            return
        request_type = path_parts[0]
        if request_type == 'webhook':
            if len(path_parts) == 2:
                preset_name = path_parts[1]
                self._handle_workflow_trigger(preset_name)
            else:
                self._send_response(400, {"error": "Invalid webhook format. Use /webhook/{preset_name}"})
        elif request_type == 'api':
            self._handle_api_request(path_parts)
        else:
            self._send_response(404, {"error": f"Unknown endpoint '{request_type}'."})
    def do_GET(self):
        """Handles all GET requests, specifically for status checks and fetching diagnostic results."""
        parsed_path = urlparse(self.path)
        path_parts = [part for part in unquote(parsed_path.path).strip('/').split('/') if part]
        if not path_parts:
            self._send_response(404, {"error": "Endpoint not found."})
            return
        if len(path_parts) == 4 and path_parts[0] == 'api' and path_parts[1] == 'management' and path_parts[2] == 'status':
            job_id = path_parts[3]
            logging.info(f"API: Received status request for job_id: {job_id}")
            status_info = self.server.kernel.get_job_status(job_id)
            if status_info:
                self._send_response(200, status_info)
            else:
                self._send_response(404, {"error": f"Job with ID '{job_id}' not found."})
        elif len(path_parts) == 3 and path_parts[0] == 'api' and path_parts[1] == 'diagnostics' and path_parts[2] == 'raw_log':
            self.server.kernel.write_to_log("API: Received request to fetch Raw CMD Log.", "INFO")
            all_logs = []
            while not self.server.kernel.cmd_log_queue.empty():
                try:
                    all_logs.append(self.server.kernel.cmd_log_queue.get_nowait())
                except queue.Empty:
                    break
            self._send_response(200, {"console_output": "\n".join(all_logs)})
        else:
            self._send_response(404, {"error": "Invalid GET endpoint or not found."})
    def _handle_api_request(self, path_parts):
        """Processes various commands coming through /api/... (for POST only)"""
        if len(path_parts) == 3 and path_parts[0] == 'api' and path_parts[1] == 'diagnostics' and path_parts[2] == 'start_scan':
            self.server.kernel.write_to_log("API: Received request to start Sanity Scan...", "INFO")
            diag_plugin = self.server.kernel.module_manager.get_instance("system_diagnostics_plugin")
            if diag_plugin and hasattr(diag_plugin, 'start_scan_headless'):
                scan_id = str(uuid.uuid4())
                result_data = diag_plugin.start_scan_headless(scan_id)
                self._send_response(200, result_data) # Directly return the result with a 200 OK status
            else:
                self._send_response(500, {"error": "Diagnostics plugin not found or not ready."})
            return
        if len(path_parts) == 4 and path_parts[1] == 'management' and path_parts[2] == 'start':
            preset_name = path_parts[3]
            logging.info(f"API received to start preset '{preset_name}'. Triggering execution...")
            job_id = self.server.kernel.trigger_workflow_by_api(preset_name)
            if job_id:
                self._send_response(200, {"status": "success", "message": f"Workflow for preset '{preset_name}' started successfully.", "job_id": job_id})
            else:
                self._send_response(404, {"status": "failed", "message": f"Preset '{preset_name}' not found or failed to start."})
        else:
            self._send_response(400, {"error": "Invalid API command format."})
    def _handle_workflow_trigger(self, preset_name):
        """Processes the workflow trigger from a valid request (old logic)."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            webhook_data = json.loads(post_data)
            logging.info(f"Webhook received for preset '{preset_name}'. Triggering execution...")
            self.server.kernel.trigger_workflow_by_webhook(preset_name, webhook_data)
            self._send_response(200, {"status": "success", "message": f"Workflow for preset '{preset_name}' was triggered successfully."})
        except json.JSONDecodeError:
            self._send_response(400, {"error": "Bad Request: Body must be in valid JSON format."})
        except Exception as e:
            logging.error(f"Error handling webhook for preset '{preset_name}': {e}")
            self._send_response(500, {"error": f"Internal Server Error: {e}"})
    def _send_response(self, status_code, response_data):
        """Sends an HTTP response back to the client."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
    def log_message(self, format, *args):
        """Redirects server logs to the main logging system."""
        logging.info(f"WebhookServer: {args[0]}")
class WebhookServer:
    """
    Manages the lifecycle of the HTTP server running in a separate thread.
    """
    def __init__(self, kernel_instance, host="0.0.0.0", port=8989):
        self.kernel = kernel_instance
        self.host = host
        self.port = port
        self.thread = None
        self.httpd = None
    def start(self):
        """Starts the HTTP server in a new thread."""
        try:
            self.httpd = socketserver.TCPServer((self.host, self.port), WebhookRequestHandler)
            self.httpd.kernel = self.kernel
            self.thread = threading.Thread(target=self.httpd.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            self.kernel.write_to_log(f"Webhook/API Server started and listening on http://{self.host}:{self.port}", "SUCCESS")
        except OSError as e:
            self.kernel.write_to_log(f"FAILED to start Webhook/API server on port {self.port}: {e}. The port might already be in use.", "ERROR")
            self.httpd = None
        except Exception as e:
            self.kernel.write_to_log(f"An unexpected error occurred while starting the Webhook/API server: {e}", "ERROR")
            self.httpd = None
    def stop(self):
        """Stops the HTTP server safely."""
        if self.httpd and self.thread and self.thread.is_alive():
            self.kernel.write_to_log("Stopping Webhook/API server...", "INFO")
            self.httpd.shutdown()
            self.httpd.server_close()
            self.thread.join(timeout=2)
            self.kernel.write_to_log("Webhook/API server stopped successfully.", "SUCCESS")
