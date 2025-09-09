#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\plugins\agent_host\processor.py
# JUMLAH BARIS : 123
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, EnumVarWrapper
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
import json
import time
class AgentHost(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "architect"
    MANAGES_OWN_HIGHLIGHTING = True
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.agent_executor = services.get("agent_executor_service")
        self.workflow_executor = self.kernel.get_service("workflow_executor_service")
    def _update_display_widget_on_ui(self, node_id, text_to_display):
        try:
            canvas_manager = self.kernel.root.tab_manager.notebook.nametowidget(self.kernel.root.tab_manager.notebook.select()).canvas_area_instance.canvas_manager
            if not canvas_manager: return
            node_data = canvas_manager.canvas_nodes.get(node_id)
            if not node_data: return
            text_widget = node_data.get('status_display_widget')
            if text_widget and text_widget.winfo_exists():
                text_widget.config(state="normal")
                text_widget.delete("1.0", "end")
                text_widget.insert("1.0", str(text_to_display))
                text_widget.config(state="disabled")
        except Exception as e:
            self.logger(f"Failed to update agent host UI: {e}", "WARN")
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE', **kwargs):
        if not self.agent_executor:
            raise RuntimeError("AgentExecutorService is not available, cannot run agent.")
        node_instance_id = config.get('__internal_node_id')
        original_highlighter = kwargs.get('highlighter')
        connections = kwargs.get('connections', {})
        def update_agent_host_display(text_to_display):
            if callable(ui_callback):
                ui_callback(self._update_display_widget_on_ui, node_instance_id, text_to_display)
        def agent_tool_highlighter(tool_node_id):
            if not callable(original_highlighter) or not callable(ui_callback):
                return
            ui_callback(original_highlighter, 'tool_node', tool_node_id)
            connection_to_highlight = None
            for conn_id, conn_data in connections.items():
                if conn_data.get('from') == tool_node_id and conn_data.get('to') == node_instance_id:
                    if conn_data.get('type') == 'tool':
                        connection_to_highlight = conn_id
                        break
            if connection_to_highlight:
                ui_callback(original_highlighter, 'connection', connection_to_highlight)
        connected_tools = kwargs.get('connected_tools', [])
        connected_brain_node = kwargs.get('connected_brain')
        connected_prompt_node = kwargs.get('connected_prompt')
        if not connected_brain_node:
            error_msg = "Agent Host 'AI Brain' port is not connected."
            if 'data' not in payload or not isinstance(payload['data'], dict): payload['data'] = {}
            payload['data']['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        if not connected_prompt_node:
            error_msg = "Agent Host 'Prompt' port is not connected."
            if 'data' not in payload or not isinstance(payload['data'], dict): payload['data'] = {}
            payload['data']['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        if callable(original_highlighter) and callable(ui_callback):
            brain_conn_id = next((cid for cid, cdata in connections.items() if cdata.get('from') == connected_brain_node['id'] and cdata.get('to') == node_instance_id), None)
            prompt_conn_id = next((cid for cid, cdata in connections.items() if cdata.get('from') == connected_prompt_node['id'] and cdata.get('to') == node_instance_id), None)
            if brain_conn_id: ui_callback(original_highlighter, 'connection', brain_conn_id)
            if prompt_conn_id: ui_callback(original_highlighter, 'connection', prompt_conn_id)
            time.sleep(0.2)
        status_updater("Getting prompt template from connected node...", "INFO")
        sub_workflow_result = self.workflow_executor.execute_workflow_synchronous(
            nodes={connected_prompt_node['id']: connected_prompt_node},
            connections={},
            initial_payload=payload,
            logger=self.logger, status_updater=lambda a,b,c: None, highlighter=lambda a,b: None,
            ui_callback=ui_callback, workflow_context_id=f"get_template_for_agent", mode=mode,
            job_status_updater=None
        )
        prompt_template_payload = sub_workflow_result.get('payload', {}) if isinstance(sub_workflow_result, dict) else {}
        prompt_template = get_nested_value(prompt_template_payload, 'data.final_prompt')
        if not prompt_template:
            self.logger("Could not find 'data.final_prompt', trying fallback 'data.prompt_template'", "DEBUG")
            prompt_template = get_nested_value(prompt_template_payload, 'data.prompt_template')
        if not prompt_template or not isinstance(prompt_template, str):
            raise ValueError("The connected Prompt node did not return a valid string template in 'data.final_prompt' or 'data.prompt_template'.")
        brain_config = connected_brain_node.get('config_values', {})
        ai_brain_endpoint = brain_config.get('selected_ai_provider')
        if not ai_brain_endpoint:
            error_msg = "Connected Brain node does not have an AI Provider selected."
            if 'data' not in payload or not isinstance(payload['data'], dict): payload['data'] = {}
            payload['data']['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        final_answer, interaction_log = self.agent_executor.run_dynamic_agent_synchronous(
            initial_payload=payload,
            full_prompt_template=prompt_template,
            connected_tools=connected_tools,
            ai_brain_endpoint=ai_brain_endpoint,
            status_updater=status_updater,
            agent_display_updater=update_agent_host_display,
            agent_tool_highlighter=agent_tool_highlighter
        )
        if 'data' not in payload or not isinstance(payload['data'], dict):
            payload['data'] = {}
        payload['data']['agent_final_answer'] = final_answer
        payload['data']['agent_interaction_log'] = interaction_log
        return {"payload": payload, "output_name": "success"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        main_frame = ttk.Frame(parent_frame)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        info_text = self.loc.get('prop_agent_host_info', fallback="This node has no direct properties. Configure it by connecting other nodes to its 'Prompt', 'Brain', and 'Tools' ports on the canvas.")
        ttk.Label(main_frame, text=info_text, wraplength=400, justify='left', bootstyle='info').pack(fill='x', padx=5, pady=10)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Agent execution is a live, complex process dependent on connected nodes.'}]
