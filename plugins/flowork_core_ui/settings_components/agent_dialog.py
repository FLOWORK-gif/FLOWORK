#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\settings_components\agent_dialog.py
# JUMLAH BARIS : 112
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, messagebox, scrolledtext
from flowork_kernel.api_client import ApiClient
from flowork_kernel.ui_shell.custom_widgets.DualListbox import DualListbox
import os
class AgentDialog(ttk.Toplevel):
    """
    A dialog for creating and editing an AI Agent's properties.
    (MODIFIED) Now fetches ALL available AI endpoints (local models and providers) for the brain.
    """
    DEFAULT_PROMPT_TEMPLATE = "" # It's better to provide an empty default or a minimal placeholder.
    def __init__(self, parent, kernel, agent_data=None):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.agent_data = agent_data or {}
        self.result = None
        title = self.loc.get('agent_dialog_title_edit' if self.agent_data else 'agent_dialog_title_new')
        self.title(title)
        self.geometry("800x850")
        self.name_var = StringVar(value=self.agent_data.get('name', ''))
        self.brain_display_name_var = StringVar()
        self._build_ui()
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(5, weight=1)
        main_frame.columnconfigure(0, weight=1)
        ttk.Label(main_frame, text=self.loc.get('agent_dialog_name_label')).grid(row=0, column=0, sticky="w", pady=(0,2))
        ttk.Entry(main_frame, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", pady=(0,10))
        ttk.Label(main_frame, text=self.loc.get('agent_dialog_desc_label')).grid(row=2, column=0, sticky="w", pady=(0,2))
        self.desc_text = scrolledtext.ScrolledText(main_frame, height=3, wrap="word")
        self.desc_text.grid(row=3, column=0, sticky="ew", pady=(0,10))
        self.desc_text.insert("1.0", self.agent_data.get('description', ''))
        config_pane = ttk.PanedWindow(main_frame, orient='horizontal')
        config_pane.grid(row=4, column=0, sticky="ew", pady=(0,15))
        brain_frame = ttk.LabelFrame(config_pane, text=self.loc.get('agent_dialog_brain_label'), padding=10)
        config_pane.add(brain_frame, weight=1)
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        all_endpoints = ai_manager.get_available_providers() if ai_manager else {}
        self.id_to_display_map = {endpoint_id: display_name for endpoint_id, display_name in all_endpoints.items()}
        self.display_to_id_map = {display_name: endpoint_id for endpoint_id, display_name in all_endpoints.items()}
        available_brains_display = sorted(list(self.display_to_id_map.keys()))
        self.brain_combo = ttk.Combobox(brain_frame, textvariable=self.brain_display_name_var, values=available_brains_display, state="readonly")
        self.brain_combo.pack(fill="x")
        saved_brain_id = self.agent_data.get('brain_model_id', '')
        if saved_brain_id in self.id_to_display_map:
            self.brain_display_name_var.set(self.id_to_display_map[saved_brain_id])
        tools_frame = ttk.LabelFrame(config_pane, text=self.loc.get('agent_dialog_tools_label'), padding=10)
        config_pane.add(tools_frame, weight=2)
        modules_success, modules_data = self.api_client.get_components('modules')
        plugins_success, plugins_data = self.api_client.get_components('plugins')
        if not modules_success:
            self.kernel.write_to_log(f"AgentDialog: Failed to get modules from API: {modules_data}", "ERROR")
            modules_data = []
        if not plugins_success:
            self.kernel.write_to_log(f"AgentDialog: Failed to get plugins from API: {plugins_data}", "ERROR")
            plugins_data = []
        all_tools_dict = {item['id']: item['name'] for item in modules_data + plugins_data}
        available_tools = sorted(all_tools_dict.values())
        selected_tool_ids = self.agent_data.get('tool_ids', [])
        selected_tool_names = [all_tools_dict[tid] for tid in selected_tool_ids if tid in all_tools_dict]
        self.tool_selector = DualListbox(tools_frame, self.kernel, available_items=available_tools, selected_items=selected_tool_names)
        self.tool_selector.pack(fill="both", expand=True)
        prompt_frame = ttk.LabelFrame(main_frame, text="Agent Prompt Template", padding=10)
        prompt_frame.grid(row=5, column=0, sticky="nsew", pady=(0,15))
        prompt_frame.rowconfigure(0, weight=1)
        prompt_frame.columnconfigure(0, weight=1)
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap="word", height=15)
        self.prompt_text.grid(row=0, column=0, sticky="nsew")
        prompt_placeholder = self.agent_data.get('prompt_template') or "# The prompt template is now managed by the 'Prompt Engineer' module.\n# This field is for reference or overrides."
        self.prompt_text.insert("1.0", prompt_placeholder)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, sticky="e")
        save_button = ttk.Button(button_frame, text=self.loc.get("button_save"), command=self._on_save, bootstyle="success")
        save_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text=self.loc.get("button_cancel"), command=self.destroy, bootstyle="secondary")
        cancel_button.pack(side="right", padx=(0, 10))
    def _on_save(self):
        name = self.name_var.get().strip()
        brain_display_name = self.brain_display_name_var.get()
        brain_id = self.display_to_id_map.get(brain_display_name)
        selected_tool_names = self.tool_selector.get_selected_items()
        if not name or not brain_id:
            messagebox.showerror("Validation Error", "Agent Name and Brain Model are required.", parent=self)
            return
        modules_success, modules_data = self.api_client.get_components('modules')
        plugins_success, plugins_data = self.api_client.get_components('plugins')
        safe_modules = modules_data if modules_success else []
        safe_plugins = plugins_data if plugins_success else []
        name_to_id_map = {item['name']: item['id'] for item in safe_modules + safe_plugins}
        selected_tool_ids = [name_to_id_map[name] for name in selected_tool_names if name in name_to_id_map]
        self.result = {
            "id": str(self.agent_data.get('id', '')),
            "name": name,
            "description": self.desc_text.get("1.0", "end-1c").strip(),
            "brain_model_id": brain_id,
            "tool_ids": selected_tool_ids,
            "prompt_template": self.prompt_text.get("1.0", "end-1c").strip()
        }
        self.destroy()
