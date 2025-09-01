#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\api_server_service.py
# JUMLAH BARIS : 285
#######################################################################

import http.server
import socketserver
import threading
import json
import uuid
import time
import os
import re
import importlib
import inspect
from urllib.parse import urlparse, unquote
from ..base_service import BaseService
from .routes.base_api_route import BaseApiRoute
import cgi
from flowork_kernel.exceptions import PermissionDeniedError
class ApiRequestHandler(http.server.BaseHTTPRequestHandler):
    def _authenticate_request(self):
        variable_manager = self.server.service_instance.variable_manager
        if not variable_manager:
            self._send_response(503, {"error": "Service Unavailable: VariableManager is not running."})
            return False
        expected_key = variable_manager.get_variable("FLOWORK_API_KEY")
        if not expected_key:
            self._send_response(403, {"error": "Forbidden: API access is disabled. FLOWORK_API_KEY is not set."})
            return False
        provided_key = self.headers.get('X-API-Key')
        if provided_key == expected_key:
            return True
        else:
            self._send_response(401, {"error": "Unauthorized: API Key is missing or invalid."})
            return False
    def _get_json_body(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            return json.loads(post_data)
        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            self._send_response(400, {"error": "Bad Request: Invalid or missing JSON body."})
            return None
    def _send_response(self, status_code, response_data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if response_data is not None:
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
    def _handle_request(self, method):
        parsed_path = urlparse(self.path).path
        if parsed_path.startswith('/webhook/'):
            if method == 'POST':
                preset_name = unquote(parsed_path.replace('/webhook/', ''))
                body = self._get_json_body()
                self.server.service_instance.kernel.write_to_log(f"Webhook received for preset '{preset_name}'. Triggering execution...", "INFO")
                self.server.service_instance.trigger_workflow_by_api(preset_name, body)
                self._send_response(202, {"status": "accepted", "message": f"Workflow for preset '{preset_name}' has been queued."})
            else:
                self._send_response(405, {"error": "Method Not Allowed for webhooks."})
            return
        static_routes = self.server.service_instance.static_router.get(method, {})
        variable_routes = self.server.service_instance.variable_router.get(method, {})
        if parsed_path in static_routes:
            handler_func = static_routes[parsed_path]
            if parsed_path == '/api/v1/status':
                handler_func(self)
                return
            if not self._authenticate_request():
                return
            handler_func(self)
            return
        if not self._authenticate_request():
            return
        for route_pattern, handler_func in variable_routes.items():
            path_params = self._match_route(route_pattern, parsed_path)
            if path_params is not None:
                handler_func(self, **path_params)
                return
        self._send_response(404, {"error": f"API endpoint not found: {self.path}"})
    def _match_route(self, route_pattern, request_path):
        pattern_parts = route_pattern.strip('/').split('/')
        path_parts = request_path.strip('/').split('/')
        if len(pattern_parts) != len(path_parts): return None
        params = {}
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith('{') and pattern_part.endswith('}'):
                params[pattern_part[1:-1]] = unquote(path_part)
            elif pattern_part != path_part:
                return None
        return params
    def do_GET(self): self._handle_request('GET')
    def do_POST(self): self._handle_request('POST')
    def do_PUT(self): self._handle_request('PUT')
    def do_PATCH(self): self._handle_request('PATCH')
    def do_DELETE(self): self._handle_request('DELETE')
    def log_message(self, format, *args):
        self.server.service_instance.kernel.write_to_log(f"ApiServer: Request: {args[0]}", "DEBUG")
class ApiServerService(BaseService, threading.Thread):
    def __init__(self, kernel, service_id: str):
        BaseService.__init__(self, kernel, service_id)
        threading.Thread.__init__(self, daemon=True)
        self.httpd = None
        self.job_statuses = {}
        self.job_statuses_lock = threading.Lock()
        self.static_router = {}
        self.variable_router = {}
        self.route_modules = []
        self.kernel.write_to_log("Service 'ApiServerService' initialized.", "DEBUG")
        self.core_component_ids = None
        self.loc = None
        self.variable_manager = None
        self.preset_manager = None
        self.state_manager = None
        self.trigger_manager = None
        self.scheduler_manager = None
        self.module_manager_service = None
        self.widget_manager_service = None
        self.trigger_manager_service = None
        self.ai_provider_manager_service = None
        self.addon_service = None
        self.db_service = None
        self.dataset_manager_service = None # (ADDED) Initialize new service attribute
        self.training_service = None
        self.converter_service = None
        self.agent_manager = None
        self.agent_executor = None
        self.prompt_manager_service = None
    def start(self):
        self._load_dependencies()
        self._load_api_routes()
        self.core_component_ids = self._load_protected_component_ids()
        threading.Thread.start(self)
    def _safe_get_service(self, service_id):
        try:
            return self.kernel.get_service(service_id)
        except PermissionDeniedError:
            self.kernel.write_to_log(f"ApiServer dependency '{service_id}' unavailable due to license tier.", "WARN")
            return None
    def _load_dependencies(self):
        self.kernel.write_to_log("ApiServerService: Loading service dependencies...", "INFO")
        self.loc = self._safe_get_service("localization_manager")
        self.variable_manager = self._safe_get_service("variable_manager_service")
        self.preset_manager = self._safe_get_service("preset_manager_service")
        self.state_manager = self._safe_get_service("state_manager")
        self.trigger_manager = self._safe_get_service("trigger_manager_service")
        self.scheduler_manager = self._safe_get_service("scheduler_manager_service")
        self.module_manager_service = self._safe_get_service("module_manager_service")
        self.widget_manager_service = self._safe_get_service("widget_manager_service")
        self.trigger_manager_service = self._safe_get_service("trigger_manager_service")
        self.ai_provider_manager_service = self._safe_get_service("ai_provider_manager_service")
        self.addon_service = self._safe_get_service("community_addon_service")
        self.db_service = self._safe_get_service("database_service")
        self.dataset_manager_service = self._safe_get_service("dataset_manager_service") # (ADDED) Load the correct service
        self.training_service = self._safe_get_service("ai_training_service")
        self.converter_service = self._safe_get_service("model_converter_service")
        self.agent_manager = self._safe_get_service("agent_manager_service")
        self.agent_executor = self._safe_get_service("agent_executor_service")
        self.prompt_manager_service = self._safe_get_service("prompt_manager_service")
        self.kernel.write_to_log("ApiServerService: All available service dependencies loaded.", "SUCCESS")
    def _load_api_routes(self):
        self.kernel.write_to_log("ApiServer: Discovering and loading API routes...", "INFO")
        routes_dir = os.path.join(os.path.dirname(__file__), 'routes')
        for filename in os.listdir(routes_dir):
            if filename.endswith('.py') and not filename.startswith('__') and filename != 'base_api_route.py':
                module_name = f"flowork_kernel.services.api_server_service.routes.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseApiRoute) and obj is not BaseApiRoute:
                            self.kernel.write_to_log(f"  -> Found route class: {name}", "DEBUG")
                            route_instance = obj(self)
                            registered_routes = route_instance.register_routes()
                            for route, handler in registered_routes.items():
                                method, pattern = route.split(' ', 1)
                                if '{' in pattern:
                                    if method not in self.variable_router: self.variable_router[method] = {}
                                    self.variable_router[method][pattern] = handler
                                    self.kernel.write_to_log(f"    - Registered Variable: {method} {pattern}", "DETAIL")
                                else:
                                    if method not in self.static_router: self.static_router[method] = {}
                                    self.static_router[method][pattern] = handler
                                    self.kernel.write_to_log(f"    - Registered Static:   {method} {pattern}", "DETAIL")
                except Exception as e:
                    self.kernel.write_to_log(f"Failed to load routes from {filename}: {e}", "ERROR")
        self.kernel.write_to_log("API route discovery complete.", "SUCCESS")
    def _load_protected_component_ids(self):
        protected_ids = set()
        config_path = os.path.join(self.kernel.data_path, "protected_components.txt")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                protected_ids = {line.strip() for line in f if line.strip() and not line.startswith('#')}
            self.kernel.write_to_log(f"Loaded {len(protected_ids)} protected component IDs.", "INFO")
        except FileNotFoundError:
            self.kernel.write_to_log(f"Config 'protected_components.txt' not found. No components will be protected.", "WARN")
        except Exception as e:
            self.kernel.write_to_log(f"Could not load protected component IDs: {e}", "ERROR")
        return protected_ids
    def run(self):
        loc = self.kernel.get_service("localization_manager")
        if not loc or not loc.get_setting('webhook_enabled', False):
            self.kernel.write_to_log("API server is disabled in settings.", "INFO")
            return
        host = "0.0.0.0"
        port = loc.get_setting('webhook_port', 8989)
        try:
            socketserver.TCPServer.allow_reuse_address = True
            self.httpd = socketserver.TCPServer((host, port), ApiRequestHandler)
            self.httpd.service_instance = self
            self.kernel.write_to_log(f"API server started and listening at http://{host}:{port}", "SUCCESS")
            self.httpd.serve_forever()
        except OSError as e:
            self.kernel.write_to_log(f"FAILED to start API server on port {port}: {e}. Port might be in use.", "ERROR")
        except Exception as e:
            self.kernel.write_to_log(f"An unexpected error occurred while starting the API server: {e}", "ERROR")
    def stop(self):
        if self.httpd:
            self.kernel.write_to_log("Stopping API server...", "INFO")
            self.httpd.shutdown()
            self.httpd.server_close()
    def trigger_workflow_by_api(self, preset_name: str, initial_payload: dict = None) -> str | None:
        if not self.preset_manager:
            self.kernel.write_to_log(f"API Trigger failed: PresetManager service is not available.", "ERROR")
            return None
        preset_data = self.preset_manager.get_preset_data(preset_name)
        if not preset_data:
            self.kernel.write_to_log(f"API Trigger failed: preset '{preset_name}' not found or is empty.", "ERROR")
            return None
        job_id = str(uuid.uuid4())
        with self.job_statuses_lock:
            self.job_statuses[job_id] = {"type": "workflow", "status": "QUEUED", "preset_name": preset_name, "start_time": time.time()}
        self.kernel.write_to_log(f"Job '{job_id}' for preset '{preset_name}' has been queued.", "INFO")
        workflow_executor = self.kernel.get_service("workflow_executor_service")
        if workflow_executor:
            nodes = {node['id']: node for node in preset_data.get('nodes', [])}
            connections = {conn['id']: conn for conn in preset_data.get('connections', [])}
            workflow_executor.execute_workflow(
                nodes, connections, initial_payload,
                logger=self.kernel.write_to_log,
                status_updater=lambda *args: None,
                highlighter=lambda *args: None,
                ui_callback=lambda func, *args: func(*args) if callable(func) else None,
                workflow_context_id=job_id,
                job_status_updater=self.update_job_status
            )
            event_bus = self.kernel.get_service("event_bus")
            if event_bus and initial_payload and initial_payload.get("triggered_by") == "scheduler":
                rule_id = initial_payload.get("rule_id")
                if rule_id:
                    event_bus.publish("CRON_JOB_EXECUTED", {"rule_id": rule_id})
                    self.kernel.write_to_log(f"Published CRON_JOB_EXECUTED event for rule '{rule_id}'.", "DEBUG")
        else:
            self.kernel.write_to_log(f"Cannot trigger workflow '{preset_name}', WorkflowExecutor service is unavailable (likely due to license tier).", "ERROR")
        return job_id
    def trigger_scan_by_api(self, scanner_id: str = None) -> str | None:
        if not self.module_manager_service: return None
        diagnostics_plugin = self.module_manager_service.get_instance("system_diagnostics_plugin")
        if not diagnostics_plugin:
            self.kernel.write_to_log("API Scan Trigger failed: system_diagnostics_plugin not found.", "ERROR")
            return None
        job_id = f"scan_{uuid.uuid4()}"
        with self.job_statuses_lock:
            self.job_statuses[job_id] = {"type": "diagnostics_scan", "status": "QUEUED", "start_time": time.time(), "target": "ALL" if not scanner_id else scanner_id}
        scan_thread = threading.Thread(target=self._run_scan_worker, args=(job_id, diagnostics_plugin, scanner_id), daemon=True)
        scan_thread.start()
        return job_id
    def _run_scan_worker(self, job_id, diagnostics_plugin, scanner_id: str = None):
        self.update_job_status(job_id, {"status": "RUNNING"})
        try:
            result_data = diagnostics_plugin.start_scan_headless(job_id, target_scanner_id=scanner_id)
            self.update_job_status(job_id, {"status": "COMPLETED", "end_time": time.time(), "result": result_data})
        except Exception as e:
            self.kernel.write_to_log(f"Headless scan job '{job_id}' failed: {e}", "ERROR")
            self.update_job_status(job_id, {"status": "FAILED", "end_time": time.time(), "error": str(e)})
    def update_job_status(self, job_id: str, status_data: dict):
        with self.job_statuses_lock:
            if job_id not in self.job_statuses:
                self.job_statuses[job_id] = {}
            self.job_statuses[job_id].update(status_data)
    def get_job_status(self, job_id: str) -> dict | None:
        with self.job_statuses_lock:
            return self.job_statuses.get(job_id)
