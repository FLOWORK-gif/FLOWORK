#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\api_server_service.py
# JUMLAH BARIS : 273
#######################################################################

import threading
import json
import uuid
import time
import os
import re
import importlib
import inspect
from urllib.parse import urlparse, unquote
from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
import uvicorn
from ..base_service import BaseService
from flowork_kernel.exceptions import PermissionDeniedError
from .routes import (
    agent_routes, component_routes, dataset_routes, execution_routes,
    license_routes, model_routes, preset_routes, prompt_routes,
    settings_routes, system_routes, training_routes, trigger_routes,
    ui_state_routes, variable_routes,
    ui_routes
)
from .connection_manager import ConnectionManager
class ApiServerService(BaseService, threading.Thread):
    def __init__(self, kernel, service_id: str):
        BaseService.__init__(self, kernel, service_id)
        threading.Thread.__init__(self, daemon=True)
        self.app = FastAPI(title="Flowork API", version="1.0")
        self.app.service_instance = self
        self.server = None
        self.connection_manager = ConnectionManager()
        self._setup_error_handlers()
        self._setup_webhook_route()
        self._setup_websocket_route()
        self._setup_static_files()
        self.job_statuses = {}
        self.job_statuses_lock = threading.Lock()
        self.kernel.write_to_log("Service 'ApiServerService' initialized.", "DEBUG")
        self.core_component_ids = None
        self.loc = None
        self.variable_manager = None
        self.preset_manager = None
        self.state_manager = None
        self.trigger_manager = None
        self.scheduler_manager = None
        self.module_manager_service = None
        self.plugin_manager_service = None
        self.widget_manager_service = None
        self.trigger_manager_service = None
        self.ai_provider_manager_service = None
        self.addon_service = None
        self.db_service = None
        self.dataset_manager_service = None
        self.training_service = None
        self.converter_service = None
        self.agent_manager = None
        self.agent_executor = None
        self.prompt_manager_service = None
        self.diagnostics_service = None
    def _setup_error_handlers(self):
        @self.app.exception_handler(PermissionDeniedError)
        async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedError):
            return JSONResponse(
                status_code=403,
                content={"error": f"Permission Denied: {exc}"},
            )
        @self.app.exception_handler(Exception)
        async def generic_exception_handler(request: Request, exc: Exception):
            self.kernel.write_to_log(f"Unhandled API Error: {exc}", "CRITICAL")
            return JSONResponse(
                status_code=500,
                content={"error": "An internal server error occurred.", "detail": str(exc)},
            )
    def _setup_webhook_route(self):
        @self.app.post("/webhook/{preset_name}", tags=["Webhooks"])
        async def trigger_webhook(preset_name: str, payload: dict):
            self.kernel.write_to_log(f"Webhook received for preset '{preset_name}'. Triggering execution...", "INFO")
            job_id = self.trigger_workflow_by_api(preset_name, payload)
            if job_id:
                return JSONResponse(
                    status_code=202,
                    content={"status": "accepted", "message": f"Workflow for preset '{preset_name}' has been queued.", "job_id": job_id}
                )
            else:
                raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found.")
    def _setup_websocket_route(self):
        """
        ADDED: Defines the WebSocket endpoint for real-time connections.
        """
        @self.app.websocket("/ws/status")
        async def websocket_endpoint(websocket: WebSocket):
            await self.connection_manager.connect(websocket)
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.connection_manager.disconnect(websocket)
    def _setup_static_files(self):
        """
        ADDED: Configures FastAPI to serve the web-based server manager.
        """
        server_ui_path = os.path.join(self.kernel.project_root_path, "server_ui")
        if not os.path.isdir(server_ui_path):
            self.kernel.write_to_log(f"Server Manager UI directory not found at {server_ui_path}", "WARN") # English Log
            return
        self.app.mount("/ui", StaticFiles(directory=server_ui_path), name="ui")
        @self.app.get("/", response_class=HTMLResponse, tags=["Server Manager"])
        async def serve_manager_ui():
            index_path = os.path.join(server_ui_path, "index.html")
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    return HTMLResponse(content=f.read())
            raise HTTPException(status_code=404, detail="Server Manager index.html not found.")
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
        self.plugin_manager_service = self._safe_get_service("plugin_manager_service")
        self.widget_manager_service = self._safe_get_service("widget_manager_service")
        self.trigger_manager_service = self._safe_get_service("trigger_manager_service")
        self.ai_provider_manager_service = self._safe_get_service("ai_provider_manager_service")
        self.addon_service = self._safe_get_service("community_addon_service")
        self.db_service = self._safe_get_service("database_service")
        self.dataset_manager_service = self._safe_get_service("dataset_manager_service")
        self.training_service = self._safe_get_service("ai_training_service")
        self.converter_service = self._safe_get_service("model_converter_service")
        self.agent_manager = self._safe_get_service("agent_manager_service")
        self.agent_executor = self._safe_get_service("agent_executor_service")
        self.prompt_manager_service = self._safe_get_service("prompt_manager_service")
        self.diagnostics_service = self._safe_get_service("diagnostics_service")
        self.kernel.write_to_log("ApiServerService: All available service dependencies loaded.", "SUCCESS")
    def _load_api_routes(self):
        api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
        def get_api_key(api_key: str = Depends(api_key_header)):
            expected_key = self.variable_manager.get_variable("FLOWORK_API_KEY")
            if not expected_key:
                 raise HTTPException(status_code=403, detail="API access is disabled. FLOWORK_API_KEY is not set.")
            if api_key == expected_key:
                return api_key
            else:
                raise HTTPException(status_code=401, detail="API Key is missing or invalid.")
        api_v1_router = APIRouter(prefix="/api/v1")
        protected_router = APIRouter(dependencies=[Depends(get_api_key)])
        self.kernel.write_to_log("ApiServer: Discovering and loading API routes...", "INFO")
        routers_to_protect = [
            agent_routes.router, component_routes.router, dataset_routes.router, execution_routes.router,
            license_routes.router, model_routes.router, preset_routes.router, prompt_routes.router,
            settings_routes.router, system_routes.router, training_routes.router, trigger_routes.router,
            ui_state_routes.router, variable_routes.router,
            ui_routes.router
        ]
        for router_instance in routers_to_protect:
            protected_router.include_router(router_instance)
            self.kernel.write_to_log(f"  -> Included protected router: {router_instance.tags[0] if router_instance.tags else 'Unnamed'}", "DEBUG")
        api_v1_router.include_router(system_routes.public_router)
        self.kernel.write_to_log("  -> Included public router: System Status", "DEBUG")
        api_v1_router.include_router(protected_router)
        self.app.include_router(api_v1_router)
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
        if not self.loc or not self.loc.get_setting('webhook_enabled', False):
            self.kernel.write_to_log("API server is disabled in settings.", "INFO")
            return
        host = "0.0.0.0"
        port = self.loc.get_setting('webhook_port', 8989)
        try:
            self.kernel.write_to_log(f"API server starting on http://{host}:{port}", "SUCCESS")
            config = uvicorn.Config(self.app, host=host, port=port, log_level="warning")
            self.server = uvicorn.Server(config)
            self.server.run()
        except Exception as e:
            self.kernel.write_to_log(f"An unexpected error occurred while starting the API server: {e}", "ERROR")
    def stop(self):
        if self.server and self.server.started:
            self.kernel.write_to_log("Stopping API server...", "INFO")
            self.server.should_exit = True
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
        if not self.diagnostics_service:
            self.kernel.write_to_log("API Scan Trigger failed: DiagnosticsService not found.", "ERROR")
            return None
        job_id = f"scan_{uuid.uuid4()}"
        with self.job_statuses_lock:
            self.job_statuses[job_id] = {"type": "diagnostics_scan", "status": "QUEUED", "start_time": time.time(), "target": "ALL" if not scanner_id else scanner_id}
        scan_thread = threading.Thread(target=self._run_scan_worker, args=(job_id, scanner_id), daemon=True)
        scan_thread.start()
        return job_id
    def _run_scan_worker(self, job_id, scanner_id: str = None):
        self.update_job_status(job_id, {"status": "RUNNING"})
        try:
            result_data = self.diagnostics_service.start_scan_headless(job_id, target_scanner_id=scanner_id)
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
