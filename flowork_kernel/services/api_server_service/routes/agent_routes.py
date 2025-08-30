#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\agent_routes.py
# JUMLAH BARIS : 85
#######################################################################

from .base_api_route import BaseApiRoute
class AgentRoutes(BaseApiRoute):
    """
    Manages API routes for Agent CRUD, execution, and status checks.
    """
    def register_routes(self):
        return {
            "GET /api/v1/agents": self.handle_get_agents,
            "GET /api/v1/agents/{agent_id}": self.handle_get_agents,
            "POST /api/v1/agents": self.handle_post_agents,
            "DELETE /api/v1/agents/{agent_id}": self.handle_delete_agent,
            "POST /api/v1/agents/{agent_id}/run": self.handle_run_agent,
            "GET /api/v1/agents/run/{run_id}": self.handle_get_agent_run_status,
            "POST /api/v1/agents/run/{run_id}/stop": self.handle_stop_agent_run,
        }
    def handle_get_agents(self, handler, agent_id=None):
        agent_manager = self.service_instance.agent_manager
        if not agent_manager:
            return handler._send_response(503, {"error": "AgentManagerService is not available due to license restrictions."})
        if agent_id:
            agent = agent_manager.get_agent(agent_id)
            if agent:
                handler._send_response(200, agent)
            else:
                handler._send_response(404, {"error": f"Agent with ID '{agent_id}' not found."})
        else:
            agents = agent_manager.get_all_agents()
            handler._send_response(200, agents)
    def handle_post_agents(self, handler):
        agent_manager = self.service_instance.agent_manager
        if not agent_manager:
            return handler._send_response(503, {"error": "AgentManagerService is not available due to license restrictions."})
        body = handler._get_json_body()
        if not body:
            return
        result = agent_manager.save_agent(body)
        if "error" in result:
            handler._send_response(400, result)
        else:
            handler._send_response(201, result)
    def handle_delete_agent(self, handler, agent_id=None):
        agent_manager = self.service_instance.agent_manager
        if not agent_manager:
            return handler._send_response(503, {"error": "AgentManagerService is not available due to license restrictions."})
        if agent_manager.delete_agent(agent_id):
            handler._send_response(204, None)
        else:
            handler._send_response(404, {"error": "Agent not found."})
    def handle_run_agent(self, handler, agent_id=None):
        agent_executor = self.service_instance.agent_executor
        if not agent_executor:
            return handler._send_response(503, {"error": "AgentExecutorService is not available due to license restrictions."})
        body = handler._get_json_body()
        if not body or 'objective' not in body:
            return handler._send_response(400, {"error": "Request must contain an 'objective'."})
        result = agent_executor.run_agent(agent_id, body['objective'])
        if "error" in result:
            handler._send_response(409, result)
        else:
            handler._send_response(202, result)
    def handle_get_agent_run_status(self, handler, run_id=None):
        agent_executor = self.service_instance.agent_executor
        if not agent_executor:
            return handler._send_response(503, {"error": "AgentExecutorService is not available due to license restrictions."})
        status = agent_executor.get_run_status(run_id)
        if "error" in status:
            handler._send_response(404, status)
        else:
            handler._send_response(200, status)
    def handle_stop_agent_run(self, handler, run_id=None):
        agent_executor = self.service_instance.agent_executor
        if not agent_executor:
            return handler._send_response(503, {"error": "AgentExecutorService is not available due to license restrictions."})
        result = agent_executor.stop_agent_run(run_id)
        if "error" in result:
            handler._send_response(404, result)
        else:
            handler._send_response(200, result)
