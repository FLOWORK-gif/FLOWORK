#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\widgets\canvas_area\canvas_area_widget.py
# JUMLAH BARIS : 343
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, simpledialog, scrolledtext, Menu
import urllib.parse
from flowork_kernel.ui_shell.version_manager_popup import VersionManagerPopup
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_kernel.ui_shell.canvas_manager import CanvasManager
import json
from widgets.data_canvas_widget.data_canvas_widget import DataCanvasWidget
class CanvasAreaWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget that contains the main canvas and ALL its action buttons, including preset management.
    [UPGRADE]: Now includes the Time-Travel Debugger UI with a manual toggle switch.
    [FIXED]: Correctly handles history data structure to prevent AttributeError.
    [FIXED V4]: Context menu logic moved here to fix bug after clearing layout.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.parent_tab = coordinator_tab
        self.canvas_manager = None
        self.execution_history = {}
        self.debugger_mode_var = ttk.BooleanVar(value=False)
        self.view_mode_var = ttk.StringVar(value="logic")
        self.loop_count_var = ttk.StringVar(value="1")
        self.loop_status_var = ttk.StringVar(value="")
        self.enable_delay_var = ttk.BooleanVar(value=True)
        self.delay_type_var = ttk.StringVar(value="static")
        self.static_delay_var = ttk.StringVar(value="1")
        self.random_min_var = ttk.StringVar(value="1")
        self.random_max_var = ttk.StringVar(value="10")
        self.hide_controls_job = None
        self._create_widgets()
        self.populate_preset_dropdown()
    def _recenter_floating_controls(self, event=None):
        """This function is called whenever the main widget resizes."""
        self.update_idletasks()
        if self.floating_controls_panel and self.floating_controls_panel.winfo_exists() and self.floating_controls_panel.winfo_viewable():
            self.floating_controls_panel.place(in_=self, relx=0.5, rely=1.0, y=-10, anchor="s")
    def _create_widgets(self):
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        self.bind("<Configure>", self._recenter_floating_controls)
        preset_bar_frame = ttk.Frame(self)
        preset_bar_frame.pack(side="top", fill='x', padx=5, pady=(0,5))
        preset_action_frame = ttk.Frame(preset_bar_frame)
        preset_action_frame.pack(fill='x', pady=(5,0))
        self.manage_versions_button = ttk.Button(preset_action_frame, text=self.loc.get('manage_versions_button', fallback="Kelola Versi"), command=self._open_version_manager, style='info.TButton')
        self.manage_versions_button.pack(side='left', padx=(0, 10))
        ttk.Label(preset_action_frame, text=self.loc.get('load_preset_label')).pack(side='left')
        self.preset_combobox = ttk.Combobox(preset_action_frame, state="readonly", width=30)
        self.preset_combobox.pack(side='left', fill='x', expand=True, padx=10)
        self.preset_combobox.bind("<<ComboboxSelected>>", self._on_preset_selected)
        self.delete_preset_button = ttk.Button(preset_action_frame, text=self.loc.get('delete_preset_button', fallback="Hapus Preset"), command=self._delete_selected_preset, style='danger.TButton')
        self.delete_preset_button.pack(side='left', padx=(0, 5))
        self.save_preset_button = ttk.Button(preset_action_frame, text=self.loc.get('save_preset_button'), command=self._save_as_preset, style='primary.TButton')
        self.save_preset_button.pack(side='left')
        self.webhook_info_frame = ttk.Frame(preset_bar_frame)
        self.webhook_info_frame.pack(fill='x', expand=True, pady=(5,0))
        ttk.Label(self.webhook_info_frame, text="URL Pemicu:", style='Webhook.TLabel').pack(side='left', padx=(0, 5))
        self.webhook_url_var = ttk.StringVar()
        webhook_url_entry = ttk.Entry(self.webhook_info_frame, textvariable=self.webhook_url_var, state="readonly", width=60, style='Webhook.TEntry')
        webhook_url_entry.pack(side='left', fill='x', expand=True)
        copy_url_button = ttk.Button(self.webhook_info_frame, text="Salin", command=self._copy_webhook_url, style='secondary.TButton')
        copy_url_button.pack(side='left', padx=5)
        self.canvas_container = ttk.Frame(self)
        self.canvas_container.pack(expand=True, fill='both')
        self.canvas_container.bind("<Button-3>", self._show_canvas_context_menu)
        self.logic_canvas_frame = ttk.Frame(self.canvas_container)
        self.data_canvas_frame = ttk.Frame(self.canvas_container)
        self.canvas = ttk.Canvas(self.logic_canvas_frame, background=colors.get('dark', '#343a40'))
        self.canvas.pack(expand=True, fill='both')
        self.canvas_manager = CanvasManager(self, self.parent_tab, self.canvas, self.kernel)
        self.data_canvas_widget = DataCanvasWidget(self.data_canvas_frame, self.parent_tab, self.kernel, "data_canvas_main")
        self.data_canvas_widget.pack(expand=True, fill='both')
        self.floating_controls_panel = ttk.Frame(self, style='dark.TFrame', padding=5)
        ttk.Separator(self.floating_controls_panel, bootstyle="danger").pack(side="top", fill="x", pady=(0, 5))
        management_group = ttk.LabelFrame(self.floating_controls_panel, text=self.loc.get('workflow_management_title', fallback="Manajemen Alur Kerja"), bootstyle="dark")
        management_group.pack(side='left', padx=(0, 10), fill='y')
        save_button = ttk.Button(management_group, text=self.loc.get('save_workflow_button'), command=self.parent_tab.action_handler.save_workflow, style='success.TButton')
        save_button.pack(side='left', padx=5, pady=5)
        load_button = ttk.Button(management_group, text=self.loc.get('load_workflow_button'), command=self.parent_tab.action_handler.load_workflow, style='info.TButton')
        load_button.pack(side='left', padx=5, pady=5)
        clear_button = ttk.Button(management_group, text=self.loc.get('clear_canvas_button'), command=self.parent_tab.action_handler.clear_canvas, style='danger.TButton')
        clear_button.pack(side='left', padx=5, pady=5)
        execution_control_group = ttk.LabelFrame(self.floating_controls_panel, text=self.loc.get('execution_control_title', fallback="Kontrol Eksekusi"), bootstyle="dark")
        execution_control_group.pack(side='left', padx=5, fill='y')
        loop_control_frame = ttk.Frame(execution_control_group, style='dark.TFrame')
        loop_control_frame.pack(fill='x', padx=5, pady=5)
        loop_count_frame = ttk.Frame(loop_control_frame, style='dark.TFrame')
        loop_count_frame.pack(side='left', fill='y')
        ttk.Label(loop_count_frame, text=self.loc.get('loop_run_label', fallback="Ulangi:"), style='inverse-dark.TLabel').pack(side='left', padx=(0, 5))
        loop_entry = ttk.Entry(loop_count_frame, textvariable=self.loop_count_var, width=5)
        loop_entry.pack(side='left')
        ttk.Label(loop_count_frame, text=self.loc.get('loop_times_label', fallback="kali"), style='inverse-dark.TLabel').pack(side='left', padx=(5, 10))
        ToolTip(loop_entry).update_text("Set how many times the entire workflow should run.")
        delay_options_frame = ttk.Frame(loop_control_frame, style='dark.TFrame')
        delay_options_frame.pack(side='left', fill='y', padx=(10,0))
        ttk.Checkbutton(delay_options_frame, text=self.loc.get('enable_delay_checkbox', fallback="Jeda Antar Loop"), variable=self.enable_delay_var, style='dark.TCheckbutton').pack(side='left')
        self.static_delay_frame = ttk.Frame(delay_options_frame, style='dark.TFrame')
        self.random_delay_frame = ttk.Frame(delay_options_frame, style='dark.TFrame')
        delay_type_radio_static = ttk.Radiobutton(delay_options_frame, text=self.loc.get('delay_type_static'), variable=self.delay_type_var, value='static', style='dark.TRadiobutton')
        delay_type_radio_static.pack(side='left', padx=(10, 5))
        ttk.Entry(self.static_delay_frame, textvariable=self.static_delay_var, width=4).pack(side='left')
        ttk.Label(self.static_delay_frame, text="detik", style='inverse-dark.TLabel').pack(side='left', padx=(2,0))
        delay_type_radio_random = ttk.Radiobutton(delay_options_frame, text=self.loc.get('delay_type_random'), variable=self.delay_type_var, value='random', style='dark.TRadiobutton')
        delay_type_radio_random.pack(side='left', padx=(10, 5))
        ttk.Entry(self.random_delay_frame, textvariable=self.random_min_var, width=4).pack(side='left')
        ttk.Label(self.random_delay_frame, text="-", style='inverse-dark.TLabel').pack(side='left', padx=2)
        ttk.Entry(self.random_delay_frame, textvariable=self.random_max_var, width=4).pack(side='left')
        ttk.Label(self.random_delay_frame, text="detik", style='inverse-dark.TLabel').pack(side='left', padx=(2,0))
        execution_buttons_frame = ttk.Frame(execution_control_group, style='dark.TFrame')
        execution_buttons_frame.pack(fill='x', pady=(5, 2), padx=5)
        self.simulate_button = ttk.Button(execution_buttons_frame, text=self.loc.get('simulate_workflow_button', fallback="Jalankan Simulasi"), command=self.parent_tab.action_handler.simulate_workflow, style='primary.TButton')
        self.simulate_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        self.run_button = ttk.Button(execution_buttons_frame, text=self.loc.get('run_workflow_button'), command=self.parent_tab.action_handler.run_workflow, style='success.TButton')
        self.run_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        self.pause_resume_button = ttk.Button(execution_buttons_frame, text="Jeda", command=self.parent_tab.action_handler.pause_workflow, style='info.TButton', state='disabled')
        self.pause_resume_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        self.loop_status_label = ttk.Label(execution_control_group, textvariable=self.loop_status_var, bootstyle="inverse-dark")
        self.loop_status_label.pack(fill='x', pady=(2,5), padx=5)
        view_toggle_frame = ttk.Frame(self.floating_controls_panel, style='dark.TFrame')
        view_toggle_frame.pack(side='left', padx=15, fill='y')
        logic_rb = ttk.Radiobutton(view_toggle_frame, text="Logic", variable=self.view_mode_var, value="logic", command=self._on_view_mode_change, style="light-outline-toolbutton")
        logic_rb.pack(side='left', pady=10)
        data_rb = ttk.Radiobutton(view_toggle_frame, text="Data", variable=self.view_mode_var, value="data", command=self._on_view_mode_change, style="light-outline-toolbutton")
        data_rb.pack(side='left', pady=10)
        debugger_toggle_frame = ttk.Frame(self.floating_controls_panel, style='dark.TFrame')
        debugger_toggle_frame.pack(side='left', padx=10, fill='y')
        debugger_switch = ttk.Checkbutton(debugger_toggle_frame, text="Debugger", variable=self.debugger_mode_var, bootstyle="info-round-toggle", command=self._toggle_debugger_mode)
        debugger_switch.pack(side='left', pady=10)
        self._create_debugger_widgets()
        self._on_view_mode_change()
        self.canvas_container.bind("<Enter>", self._show_floating_controls)
        self.canvas_container.bind("<Leave>", self._schedule_hide_controls)
        self.floating_controls_panel.bind("<Enter>", self._cancel_hide_controls)
        self.floating_controls_panel.bind("<Leave>", self._schedule_hide_controls)
        def _toggle_delay_options(*args):
            if self.delay_type_var.get() == 'static':
                self.random_delay_frame.pack_forget()
                self.static_delay_frame.pack(side='left')
            else:
                self.static_delay_frame.pack_forget()
                self.random_delay_frame.pack(side='left')
        delay_type_radio_static.config(command=_toggle_delay_options)
        delay_type_radio_random.config(command=_toggle_delay_options)
        _toggle_delay_options()
        self.run_button.bind("<Enter>", lambda e: self.run_button.config(bootstyle="danger"))
        self.run_button.bind("<Leave>", lambda e: self.run_button.config(bootstyle="success"))
        self.simulate_button.bind("<Enter>", lambda e: self.simulate_button.config(bootstyle="danger"))
        self.simulate_button.bind("<Leave>", lambda e: self.simulate_button.config(bootstyle="primary"))
        self.save_preset_button.bind("<Enter>", lambda e: self.save_preset_button.config(bootstyle="danger"))
        self.save_preset_button.bind("<Leave>", lambda e: self.save_preset_button.config(bootstyle="primary"))
    def _show_canvas_context_menu(self, event):
        if not self.canvas_manager: return
        self.canvas_manager.interaction_manager._show_canvas_context_menu(event)
    def _show_floating_controls(self, event=None):
        self._cancel_hide_controls()
        if not self.floating_controls_panel.winfo_viewable():
            self.floating_controls_panel.place(in_=self, relx=0.5, rely=1.0, y=-10, anchor="s")
    def _schedule_hide_controls(self, event=None):
        self.hide_controls_job = self.after(500, self._check_and_hide_controls)
    def _cancel_hide_controls(self, event=None):
        if self.hide_controls_job:
            self.after_cancel(self.hide_controls_job)
            self.hide_controls_job = None
    def _check_and_hide_controls(self):
        if not self.winfo_exists(): return
        cursor_x = self.winfo_pointerx()
        cursor_y = self.winfo_pointery()
        canvas_x1 = self.canvas_container.winfo_rootx()
        canvas_y1 = self.canvas_container.winfo_rooty()
        canvas_x2 = canvas_x1 + self.canvas_container.winfo_width()
        canvas_y2 = canvas_y1 + self.canvas_container.winfo_height()
        panel_x1 = self.floating_controls_panel.winfo_rootx()
        panel_y1 = self.floating_controls_panel.winfo_rooty()
        panel_x2 = panel_x1 + self.floating_controls_panel.winfo_width()
        panel_y2 = panel_y1 + self.floating_controls_panel.winfo_height()
        is_over_canvas = (canvas_x1 <= cursor_x <= canvas_x2) and (canvas_y1 <= cursor_y <= canvas_y2)
        is_over_panel = self.floating_controls_panel.winfo_viewable() and (panel_x1 <= cursor_x <= panel_x2) and (panel_y1 <= cursor_y <= panel_y2)
        if not is_over_canvas and not is_over_panel:
            self.floating_controls_panel.place_forget()
        self.hide_controls_job = None
    def _on_view_mode_change(self):
        if self.view_mode_var.get() == "data":
            if self.canvas_manager:
                self.data_canvas_widget.sync_with_logic_canvas(self.canvas_manager.canvas_nodes)
            self.logic_canvas_frame.pack_forget()
            self.data_canvas_frame.pack(expand=True, fill='both')
        else:
            self.data_canvas_frame.pack_forget()
            self.logic_canvas_frame.pack(expand=True, fill='both')
    def _create_debugger_widgets(self):
        self.debugger_frame = ttk.LabelFrame(self, text=" Mesin Waktu Debugger", padding=5)
        controls_frame = ttk.Frame(self.debugger_frame)
        controls_frame.pack(side="left", fill="y", padx=5)
        self.step_label_var = ttk.StringVar(value="Step: 0/0")
        ttk.Label(controls_frame, textvariable=self.step_label_var).pack(pady=2)
        self.timeline_slider = ttk.Scale(controls_frame, from_=0, to=0, orient="vertical", command=self._on_timeline_scrub)
        self.timeline_slider.pack(fill="y", expand=True, pady=5)
        self.timeline_slider.config(state="disabled")
        close_button = ttk.Button(controls_frame, text="Tutup Debugger", command=self.hide_debugger, bootstyle="secondary-outline")
        close_button.pack(pady=5)
        payload_frame = ttk.LabelFrame(self.debugger_frame, text="Payload di Langkah Terpilih")
        payload_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.payload_viewer = scrolledtext.ScrolledText(payload_frame, wrap="word", font=("Consolas", 9))
        self.payload_viewer.pack(fill="both", expand=True)
        self.payload_viewer.config(state="disabled")
    def _toggle_debugger_mode(self):
        if self.debugger_mode_var.get():
            if not self.kernel.is_tier_sufficient('basic'):
                messagebox.showwarning(
                    self.loc.get('license_popup_title'),
                    self.loc.get('license_popup_message', module_name="Time-Travel Debugger"),
                    parent=self.winfo_toplevel()
                )
                self.debugger_mode_var.set(False)
                tab_manager = self.kernel.get_service("tab_manager_service")
                if tab_manager:
                    tab_manager.open_managed_tab("pricing_page")
                return
        if self.debugger_mode_var.get():
            self.show_debugger(self.execution_history or {})
        else:
            self.hide_debugger()
    def show_debugger(self, history_data):
        steps = history_data.get('steps', [])
        self.debugger_frame.pack(side="bottom", fill="x", expand=False, pady=10, padx=5)
        self.debugger_mode_var.set(True)
        if not steps:
            self.kernel.write_to_log("No execution history to debug.", "INFO") # English Log
            self.step_label_var.set("Step: 0/0")
            self.timeline_slider.config(to=0, state="disabled")
            self.payload_viewer.config(state="normal")
            self.payload_viewer.delete("1.0", "end")
            self.payload_viewer.insert("1.0", "Run a workflow to generate debug data.")
            self.payload_viewer.config(state="disabled")
            return
        num_steps = len(steps)
        self.timeline_slider.config(to=num_steps - 1, state="normal")
        self.timeline_slider.set(num_steps - 1)
        self._on_timeline_scrub(num_steps - 1)
    def hide_debugger(self):
        self.debugger_frame.pack_forget()
        self.debugger_mode_var.set(False)
        if self.canvas_manager:
            self.canvas_manager.visual_manager.clear_timeline_highlight()
    def _on_timeline_scrub(self, value):
        step_index = int(float(value))
        steps = self.execution_history.get('steps', [])
        if not steps or step_index >= len(steps):
            self.step_label_var.set("Step: 0/0")
            self.payload_viewer.config(state="normal")
            self.payload_viewer.delete("1.0", "end")
            self.payload_viewer.config(state="disabled")
            if self.canvas_manager:
                self.canvas_manager.visual_manager.clear_timeline_highlight()
            return
        current_step = steps[step_index]
        connection_id = current_step.get('connection_id')
        payload = current_step.get('payload', {})
        self.step_label_var.set(f"Step: {step_index + 1}/{len(steps)}")
        self.payload_viewer.config(state="normal")
        self.payload_viewer.delete("1.0", "end")
        try:
            pretty_payload = json.dumps(payload, indent=4, ensure_ascii=False)
            self.payload_viewer.insert("1.0", pretty_payload)
        except Exception as e:
            self.payload_viewer.insert("1.0", f"Error displaying payload: {e}\n\n{payload}")
        self.payload_viewer.config(state="disabled")
        if self.canvas_manager:
            self.canvas_manager.visual_manager.highlight_timeline_step(connection_id)
    def populate_preset_dropdown(self):
        try:
            preset_manager = self.kernel.get_service("preset_manager")
            if not preset_manager: return
            presets = preset_manager.get_preset_list()
            self.preset_combobox['values'] = sorted(presets)
            current_selection = self.preset_combobox.get()
            if current_selection not in presets:
                self.preset_combobox.set('')
        except Exception as e:
            self.kernel.write_to_log(f"Failed to load preset list: {e}", "ERROR") # English Log
            self.preset_combobox['values'] = []
        self._update_webhook_info()
    def _update_webhook_info(self):
        loc = self.kernel.get_service("localization_manager")
        api_service = self.kernel.get_service("api_server_service")
        is_webhook_enabled = loc.get_setting('webhook_enabled', False) if loc else False
        selected_preset = self.preset_combobox.get()
        if is_webhook_enabled and selected_preset and api_service:
            host = getattr(api_service, 'host', '127.0.0.1')
            if host == '0.0.0.0': host = '127.0.0.1'
            port = getattr(api_service, 'port', 8989)
            encoded_preset = urllib.parse.quote(selected_preset)
            url = f"http://{host}:{port}/webhook/{encoded_preset}"
            self.webhook_url_var.set(url)
            self.webhook_info_frame.pack(fill='x', pady=(5,0))
        else:
            self.webhook_info_frame.pack_forget()
    def _copy_webhook_url(self):
        url_to_copy = self.webhook_url_var.get()
        if url_to_copy:
            self.clipboard_clear()
            self.clipboard_append(url_to_copy)
            self.kernel.write_to_log(f"Webhook URL copied to clipboard: {url_to_copy}", "SUCCESS") # English Log
    def _on_preset_selected(self, event=None):
        if hasattr(self.parent_tab, 'action_handler'):
            self.parent_tab.action_handler.on_preset_selected(event)
    def _save_as_preset(self):
        if hasattr(self.parent_tab, 'action_handler'):
            self.parent_tab.action_handler.save_as_preset()
    def _delete_selected_preset(self):
        if hasattr(self.parent_tab, 'action_handler'):
            self.parent_tab.action_handler._delete_selected_preset()
    def _open_version_manager(self):
        if not self.kernel.is_tier_sufficient('basic'):
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name="Preset Version Management"),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager:
                tab_manager.open_managed_tab("pricing_page")
            return
        selected_preset = self.preset_combobox.get()
        if not selected_preset:
            messagebox.showwarning(self.loc.get('warning_title'), self.loc.get('select_preset_to_delete_warning', fallback="Pilih preset terlebih dahulu untuk mengelola versinya."))
            return
        VersionManagerPopup(self.parent_tab, self.kernel, selected_preset)
    def update_zoom_label(self):
        if hasattr(self, 'zoom_label') and self.canvas_manager and self.canvas_manager.interaction_manager and self.canvas_manager.interaction_manager.navigation_handler:
            self.zoom_label.config(text=f"{int(self.canvas_manager.interaction_manager.navigation_handler.zoom_level * 100)}%")
    def apply_styles(self, colors):
        pass
