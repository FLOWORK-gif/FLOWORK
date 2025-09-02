#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\trigger_manager_page.py
# JUMLAH BARIS : 344
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, Toplevel, scrolledtext
import uuid
from datetime import datetime, timezone
from flowork_kernel.api_client import ApiClient
import threading
from flowork_kernel.utils.performance_logger import log_performance
import re # (ADDED) Import regex for markdown parsing
class TriggerManagerPage(ttk.Frame):
    """
    [REFACTORED V5] Complete UI overhaul for trigger management.
    Features a three-pane layout: a trigger toolbox, a details panel
    with localized descriptions and tutorials, and the active rules area.
    [FIXED] Text color in details panel now respects the current theme.
    """
    def __init__(self, parent, kernel):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient()
        self.countdown_updater_id = None
        self.countdown_jobs = {}
        self._drag_data = {}
        self.trigger_definitions = {}
        self.right_pane = None
        self._build_ui_v3()
        self._load_initial_data()
        self._start_countdown_updater()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            subscriber_id = f"trigger_manager_page_{id(self)}"
            event_bus.subscribe("CRON_JOB_EXECUTED", subscriber_id, self._on_cron_job_executed)
            self.kernel.write_to_log(f"TriggerManagerPage is now listening for cron job executions.", "DEBUG")
    def _build_ui_v3(self):
        """Builds the new three-pane, drag-and-drop UI with details panel."""
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill='both', expand=True, padx=15, pady=15)
        left_pane_container = ttk.Frame(main_pane)
        main_pane.add(left_pane_container, weight=1)
        left_vertical_pane = ttk.PanedWindow(left_pane_container, orient='vertical')
        left_vertical_pane.pack(fill='both', expand=True)
        toolbox_frame = ttk.LabelFrame(left_vertical_pane, text="Available Triggers", padding=10)
        left_vertical_pane.add(toolbox_frame, weight=1)
        self.trigger_toolbox_tree = ttk.Treeview(toolbox_frame, show="tree", selectmode="browse")
        self.trigger_toolbox_tree.pack(expand=True, fill='both')
        self.trigger_toolbox_tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.trigger_toolbox_tree.bind("<B1-Motion>", self._on_drag_motion)
        self.trigger_toolbox_tree.bind("<ButtonRelease-1>", self._on_drag_release)
        self.trigger_toolbox_tree.bind("<<TreeviewSelect>>", self._on_toolbox_select)
        details_frame = ttk.LabelFrame(left_vertical_pane, text="Trigger Details", padding=10)
        left_vertical_pane.add(details_frame, weight=2)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(2, weight=1)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {}
        fg_color = colors.get('fg', 'white')
        bg_color = colors.get('bg', '#222222')
        text_bg_color = colors.get('dark', '#333333')
        self.detail_title = ttk.Label(details_frame, text="Select a trigger to see details", font="-weight bold", wraplength=250)
        self.detail_title.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.detail_desc = ttk.Label(details_frame, text="", wraplength=280, justify="left", foreground=fg_color, background=bg_color)
        self.detail_desc.grid(row=1, column=0, sticky="nsew", pady=(0,10))
        self.detail_usage = scrolledtext.ScrolledText(
            details_frame,
            wrap="word",
            height=8,
            state="disabled",
            font="-size 9",
            background=text_bg_color,
            foreground=fg_color,
            borderwidth=0,
            highlightthickness=0,
            insertbackground=fg_color # (ADDED) Makes the cursor visible if editable
        )
        self.detail_usage.grid(row=2, column=0, sticky="nsew")
        self.detail_usage.tag_configure("bold", font="-size 9 -weight bold")
        self.right_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(self.right_pane, weight=3)
        self.right_pane.rowconfigure(1, weight=1)
        self.right_pane.columnconfigure(0, weight=1)
        button_frame = ttk.Frame(self.right_pane)
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(button_frame, text=self.loc.get('trigger_btn_new', fallback="New Rule..."), command=self._open_rule_editor, style="success.TButton").pack(side="left")
        ttk.Button(button_frame, text=self.loc.get('trigger_btn_edit', fallback="Edit..."), command=self._edit_selected_rule).pack(side="left", padx=10)
        ttk.Button(button_frame, text=self.loc.get('trigger_btn_delete', fallback="Delete"), command=self._delete_selected_rule, style="danger.TButton").pack(side="left")
        rules_frame = ttk.LabelFrame(self.right_pane, text="Active Trigger Rules")
        rules_frame.grid(row=1, column=0, sticky="nsew")
        rules_frame.rowconfigure(0, weight=1)
        rules_frame.columnconfigure(0, weight=1)
        columns = ("name", "trigger_type", "preset", "status", "next_run")
        self.rules_tree = ttk.Treeview(rules_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.rules_tree.heading("name", text=self.loc.get('trigger_col_name', fallback="Rule Name"))
        self.rules_tree.heading("trigger_type", text=self.loc.get('trigger_col_type', fallback="Trigger Type"))
        self.rules_tree.heading("preset", text=self.loc.get('trigger_col_preset', fallback="Preset to Run"))
        self.rules_tree.heading("status", text=self.loc.get('trigger_col_status', fallback="Status"))
        self.rules_tree.heading("next_run", text=self.loc.get('trigger_col_next_run', fallback="Next Schedule"))
        self.rules_tree.column("name", width=250)
        self.rules_tree.column("trigger_type", width=150)
        self.rules_tree.column("preset", width=200)
        self.rules_tree.column("status", width=80, anchor='center')
        self.rules_tree.column("next_run", width=150, anchor='center')
        self.rules_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(rules_frame, orient="vertical", command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _on_toolbox_select(self, event=None):
        selected_items = self.trigger_toolbox_tree.selection()
        if not selected_items:
            return
        trigger_id = selected_items[0]
        trigger_def = self.trigger_definitions.get(trigger_id)
        if trigger_def:
            name = self.loc.get(trigger_def.get('name_key'), fallback=trigger_def.get('id'))
            desc = self.loc.get(trigger_def.get('description_key'), fallback='No description available.')
            usage = self.loc.get(trigger_def.get('tutorial_key'), fallback='No tutorial available.')
            self.detail_title.config(text=name)
            self.detail_desc.config(text=desc)
            self._apply_markdown_to_text_widget(self.detail_usage, usage)
    def _populate_trigger_toolbox(self, success, definitions):
        for item in self.trigger_toolbox_tree.get_children():
            self.trigger_toolbox_tree.delete(item)
        self.trigger_definitions.clear()
        if success:
            for trigger_def in sorted(definitions, key=lambda x: self.loc.get(x.get('name_key'), fallback=x.get('id', ''))):
                trigger_id = trigger_def['id']
                display_name = self.loc.get(trigger_def.get('name_key'), fallback=trigger_id)
                self.trigger_definitions[trigger_id] = trigger_def
                self.trigger_toolbox_tree.insert("", "end", iid=trigger_id, text=display_name)
        else:
            self.trigger_toolbox_tree.insert("", "end", text="Error loading triggers.")
    def _on_drag_start(self, event):
        item_id = self.trigger_toolbox_tree.identify_row(event.y)
        if not item_id: return
        item_text = self.trigger_toolbox_tree.item(item_id, "text")
        self._drag_data = {
            "item_id": item_id,
            "widget": ttk.Label(self.winfo_toplevel(), text=item_text, bootstyle="inverse-info", padding=5, relief="solid"),
            "tree_widget": self.trigger_toolbox_tree
        }
    def _on_drag_motion(self, event):
        if self._drag_data.get("widget"):
            self._drag_data['widget'].place(x=event.x_root - self.winfo_toplevel().winfo_rootx() + 15, y=event.y_root - self.winfo_toplevel().winfo_rooty() + 15)
    def _on_drag_release(self, event):
        if self._drag_data.get("widget"):
            self._drag_data["widget"].destroy()
        drop_x, drop_y = event.x_root, event.y_root
        right_pane = self.right_pane
        if right_pane and right_pane.winfo_rootx() < drop_x < right_pane.winfo_rootx() + right_pane.winfo_width() and \
           right_pane.winfo_rooty() < drop_y < right_pane.winfo_rooty() + right_pane.winfo_height():
            dropped_trigger_id = self._drag_data.get("item_id")
            if dropped_trigger_id:
                self.kernel.write_to_log(f"Trigger type '{dropped_trigger_id}' dropped. Opening editor.", "INFO")
                prefilled_data = {'trigger_id': dropped_trigger_id}
                self._open_rule_editor(rule_data=prefilled_data)
        self._drag_data = {}
    def _load_initial_data(self):
        self.rules_tree.insert("", "end", values=("Loading rules from API...", "", "", "", ""), tags=("loading",))
        self.trigger_toolbox_tree.insert("", "end", text="Loading triggers...", tags=("loading",))
        threading.Thread(target=self._load_data_worker, daemon=True).start()
    @log_performance("Fetching all trigger data for TriggerManagerPage")
    def _load_data_worker(self):
        success_rules, rules = self.api_client.get_trigger_rules()
        success_defs, defs = self.api_client.get_trigger_definitions()
        self.after(0, self._populate_rules_list_from_data, success_rules, rules)
        self.after(0, self._populate_trigger_toolbox, success_defs, defs)
    def _populate_rules_list_from_data(self, success, rules):
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        self.countdown_jobs.clear()
        if not success:
            messagebox.showerror(self.loc.get('error_title'), f"Failed to load trigger rules: {rules}")
            self.rules_tree.insert("", "end", values=("Failed to load rules.", "", "", "", ""), tags=("error",))
            return
        for rule_data in sorted(rules, key=lambda r: r.get('name', '')):
            status = self.loc.get('status_enabled') if rule_data.get("is_enabled") else self.loc.get('status_disabled')
            next_run_text = "-"
            if rule_data.get("is_enabled") and rule_data.get('next_run_time'):
                next_run_text = self.loc.get('status_calculating')
            values = (
                rule_data.get("name", "No Name"),
                rule_data.get("trigger_name", "Unknown"),
                rule_data.get("preset_to_run", "-"),
                status,
                next_run_text
            )
            item_id = self.rules_tree.insert("", "end", values=values, iid=rule_data['id'])
            if rule_data.get("is_enabled") and rule_data.get('next_run_time'):
                self.countdown_jobs[item_id] = rule_data['next_run_time']
    def _start_countdown_updater(self):
        if self.countdown_updater_id is None:
            self._update_countdowns()
    def _update_countdowns(self):
        if not self.winfo_exists(): return
        for item_id, next_run_iso in self.countdown_jobs.items():
            if not self.rules_tree.exists(item_id): continue
            try:
                next_run_time = datetime.fromisoformat(next_run_iso)
                now_utc = datetime.now(timezone.utc)
                delta = next_run_time - now_utc
                if delta.total_seconds() > 0:
                    hours, remainder = divmod(int(delta.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    countdown_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                    self.rules_tree.set(item_id, "next_run", countdown_str)
                else:
                    self.rules_tree.set(item_id, "next_run", self.loc.get('status_waiting_schedule'))
            except (ValueError, TypeError):
                 self.rules_tree.set(item_id, "next_run", self.loc.get('status_not_scheduled'))
        self.countdown_updater_id = self.after(1000, self._update_countdowns)
    def destroy(self):
        if self.countdown_updater_id:
            self.after_cancel(self.countdown_updater_id)
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            subscriber_id = f"trigger_manager_page_{id(self)}"
        super().destroy()
    def _on_cron_job_executed(self, event_data):
        self.kernel.write_to_log("Cron job executed, TriggerManagerPage is refreshing its data.", "DEBUG")
        self.after(1000, self._load_initial_data)
    def _edit_selected_rule(self):
        selected_items = self.rules_tree.selection()
        if not selected_items:
            messagebox.showwarning(self.loc.get('warning_title'), self.loc.get('trigger_warn_select_to_edit'))
            return
        success, all_rules = self.api_client.get_trigger_rules()
        if not success:
            messagebox.showerror(self.loc.get('error_title'), "Could not fetch rule details for editing.")
            return
        rule_data = next((r for r in all_rules if r['id'] == selected_items[0]), None)
        if rule_data:
            self._open_rule_editor(rule_id=selected_items[0], rule_data=rule_data)
    def _delete_selected_rule(self):
        selected_items = self.rules_tree.selection()
        if not selected_items:
            messagebox.showwarning(self.loc.get('warning_title'), self.loc.get('trigger_warn_select_to_delete'))
            return
        rule_id = selected_items[0]
        rule_name = self.rules_tree.item(rule_id, 'values')[0]
        if messagebox.askyesno(self.loc.get('confirm_delete_title'), self.loc.get('trigger_confirm_delete', name=rule_name)):
            success, response = self.api_client.delete_trigger_rule(rule_id)
            if success:
                self._save_and_reload()
            else:
                messagebox.showerror(self.loc.get('error_title'), f"Failed to delete rule: {response}")
    def _save_and_reload(self):
        self._load_initial_data()
        self.api_client.reload_triggers()
    def _open_rule_editor(self, rule_id=None, rule_data=None):
        rule_data = rule_data or {}
        editor_window = Toplevel(self)
        editor_window.transient(self)
        editor_window.grab_set()
        editor_window.title(self.loc.get('trigger_editor_title_edit' if rule_id else 'trigger_editor_title_new'))
        _, trigger_defs = self.api_client.get_trigger_definitions()
        _, presets = self.api_client.get_presets()
        form_vars = {
            'name': ttk.StringVar(value=rule_data.get('name', '')),
            'trigger_id': ttk.StringVar(value=rule_data.get('trigger_id', '')),
            'preset_to_run': ttk.StringVar(value=rule_data.get('preset_to_run', '')),
            'is_enabled': ttk.BooleanVar(value=rule_data.get('is_enabled', True)),
        }
        main_frame = ttk.Frame(editor_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text=self.loc.get('trigger_form_name')).pack(anchor='w', pady=(0,2))
        ttk.Entry(main_frame, textvariable=form_vars['name']).pack(fill='x', pady=(0, 10))
        ttk.Label(main_frame, text=self.loc.get('trigger_form_type')).pack(anchor='w', pady=(0,2))
        trigger_display_names = {self.loc.get(tdef.get('name_key'), fallback=tdef['id']): tdef['id'] for tdef in trigger_defs}
        trigger_combobox = ttk.Combobox(main_frame, state="readonly", values=list(sorted(trigger_display_names.keys())))
        if form_vars['trigger_id'].get():
            id_to_display = {v: k for k, v in trigger_display_names.items()}
            display_name = id_to_display.get(form_vars['trigger_id'].get())
            if display_name:
                trigger_combobox.set(display_name)
            else:
                self.kernel.write_to_log(f"Cannot set trigger in UI, ID '{form_vars['trigger_id'].get()}' not found in loaded definitions.", "WARN")
        trigger_combobox.pack(fill='x', pady=(0, 10))
        ttk.Label(main_frame, text=self.loc.get('trigger_form_preset')).pack(anchor='w', pady=(0,2))
        ttk.Combobox(main_frame, textvariable=form_vars['preset_to_run'], values=presets, state="readonly").pack(fill='x', pady=(0, 10))
        config_frame_container = ttk.Frame(main_frame)
        config_frame_container.pack(fill="both", expand=True, pady=5)
        def on_trigger_selected(event=None):
            for widget in config_frame_container.winfo_children(): widget.destroy()
            trigger_manager_service = self.kernel.get_service("trigger_manager_service")
            if not trigger_manager_service: return
            selected_display_name = trigger_combobox.get()
            selected_trigger_id = trigger_display_names.get(selected_display_name)
            if not selected_trigger_id: return
            form_vars['trigger_id'].set(selected_trigger_id)
            ConfigUIClass = trigger_manager_service.get_config_ui_class(selected_trigger_id)
            if ConfigUIClass:
                config_frame_container.configure(padding=(0, 10))
                config_ui_instance = ConfigUIClass(config_frame_container, self.loc, rule_data.get('config', {}))
                config_ui_instance.pack(fill='both', expand=True)
                form_vars['config_ui'] = config_ui_instance
            else:
                config_frame_container.configure(padding=(0, 0))
        trigger_combobox.bind("<<ComboboxSelected>>", on_trigger_selected)
        if form_vars['trigger_id'].get(): on_trigger_selected()
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(side='bottom', fill='x', pady=(10,0))
        ttk.Checkbutton(bottom_frame, text=self.loc.get('trigger_form_enable'), variable=form_vars['is_enabled']).pack(side='left')
        button_container = ttk.Frame(bottom_frame)
        button_container.pack(side='right')
        def _save_rule():
            if not form_vars['trigger_id'].get():
                messagebox.showerror(self.loc.get('error_title'), self.loc.get('trigger_err_no_type_selected'))
                return
            new_rule_data = {
                "name": form_vars['name'].get(),
                "trigger_id": form_vars['trigger_id'].get(),
                "preset_to_run": form_vars['preset_to_run'].get(),
                "is_enabled": form_vars['is_enabled'].get(),
                "config": {}
            }
            if 'config_ui' in form_vars and hasattr(form_vars['config_ui'], 'get_config'):
                new_rule_data['config'] = form_vars['config_ui'].get_config()
            if rule_id:
                success, _ = self.api_client.update_trigger_rule(rule_id, new_rule_data)
            else:
                success, _ = self.api_client.create_trigger_rule(new_rule_data)
            if success:
                self._save_and_reload()
                editor_window.destroy()
            else:
                messagebox.showerror(self.loc.get('error_title'), "Failed to save the rule via API.")
        ttk.Button(button_container, text=self.loc.get('button_save'), command=_save_rule, style="success.TButton").pack(side="right")
        ttk.Button(button_container, text=self.loc.get('button_cancel'), command=editor_window.destroy, style="secondary.TButton").pack(side="right", padx=10)
