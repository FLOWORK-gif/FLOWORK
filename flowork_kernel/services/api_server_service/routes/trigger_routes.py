#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\trigger_routes.py
# JUMLAH BARIS : 101
#######################################################################

from .base_api_route import BaseApiRoute
import uuid
class TriggerRoutes(BaseApiRoute):
    """
    Manages API routes for Trigger definitions and rules.
    """
    def register_routes(self):
        return {
            "GET /api/v1/triggers/definitions": self.handle_get_trigger_definitions,
            "GET /api/v1/triggers/rules": self.handle_get_trigger_rules,
            "GET /api/v1/triggers/rules/{rule_id}": self.handle_get_trigger_rules,
            "POST /api/v1/triggers/rules": self.handle_post_trigger_rule,
            "PUT /api/v1/triggers/rules/{rule_id}": self.handle_put_trigger_rule,
            "DELETE /api/v1/triggers/rules/{rule_id}": self.handle_delete_trigger_rule,
            "POST /api/v1/triggers/actions/reload": self.handle_reload_triggers,
        }
    def handle_get_trigger_definitions(self, handler):
        trigger_manager = self.service_instance.trigger_manager
        if not trigger_manager:
            return handler._send_response(503, {"error": "TriggerManager service is unavailable."})
        definitions = [tdata['manifest'] for tid, tdata in trigger_manager.loaded_triggers.items()]
        handler._send_response(200, sorted(definitions, key=lambda x: x.get('name', '')))
    def handle_get_trigger_rules(self, handler, rule_id=None):
        state_manager = self.service_instance.state_manager
        if not state_manager:
            return handler._send_response(503, {"error": "StateManager service is unavailable."})
        all_rules = state_manager.get("trigger_rules", {})
        if rule_id:
            rule_data = all_rules.get(rule_id)
            if rule_data:
                handler._send_response(200, rule_data)
            else:
                handler._send_response(404, {"error": f"Rule with ID '{rule_id}' not found."})
        else:
            trigger_manager = self.service_instance.trigger_manager
            scheduler_manager = self.service_instance.scheduler_manager
            enriched_rules = []
            for rid, rdata in all_rules.items():
                enriched_data = rdata.copy()
                enriched_data['id'] = rid
                trigger_id = rdata.get('trigger_id')
                enriched_data['trigger_name'] = trigger_manager.loaded_triggers.get(trigger_id, {}).get('manifest', {}).get('name', trigger_id) if trigger_manager else trigger_id
                next_run = None
                if scheduler_manager and trigger_id == 'cron_trigger' and rdata.get('is_enabled'):
                    try:
                        next_run_time = scheduler_manager.get_next_run_time(rid)
                        if next_run_time:
                            next_run = next_run_time.isoformat()
                    except Exception as e:
                        self.logger(f"A non-critical error occurred while fetching next_run_time for job '{rid}'. The UI will show '-'. Error: {e}", "WARN") # English Log
                        next_run = None
                enriched_data['next_run_time'] = next_run
                enriched_rules.append(enriched_data)
            handler._send_response(200, enriched_rules)
    def handle_post_trigger_rule(self, handler):
        state_manager = self.service_instance.state_manager
        if not state_manager:
            return handler._send_response(503, {"error": "StateManager service is unavailable."})
        body = handler._get_json_body()
        if body is None: return
        new_rule_id = str(uuid.uuid4())
        all_rules = state_manager.get("trigger_rules", {})
        all_rules[new_rule_id] = body
        state_manager.set("trigger_rules", all_rules)
        handler._send_response(201, {"status": "success", "id": new_rule_id})
    def handle_put_trigger_rule(self, handler, rule_id=None):
        state_manager = self.service_instance.state_manager
        if not state_manager:
            return handler._send_response(503, {"error": "StateManager service is unavailable."})
        body = handler._get_json_body()
        if body is None: return
        all_rules = state_manager.get("trigger_rules", {})
        if rule_id not in all_rules:
            return handler._send_response(404, {"error": f"Rule with ID '{rule_id}' not found."})
        all_rules[rule_id] = body
        state_manager.set("trigger_rules", all_rules)
        handler._send_response(200, {"status": "success", "id": rule_id})
    def handle_delete_trigger_rule(self, handler, rule_id=None):
        state_manager = self.service_instance.state_manager
        if not state_manager:
            return handler._send_response(503, {"error": "StateManager service is unavailable."})
        all_rules = state_manager.get("trigger_rules", {})
        if rule_id in all_rules:
            del all_rules[rule_id]
            state_manager.set("trigger_rules", all_rules)
            handler._send_response(204, None)
        else:
            handler._send_response(404, {"error": f"Rule with ID '{rule_id}' not found."})
    def handle_reload_triggers(self, handler):
        trigger_manager = self.service_instance.trigger_manager
        if not trigger_manager:
            return handler._send_response(503, {"error": "TriggerManager service is unavailable."})
        trigger_manager.start_all_listeners()
        handler._send_response(200, {"status": "success", "message": "Trigger reload process initiated."})
