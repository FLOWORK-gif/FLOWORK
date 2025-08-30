#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\dashboard_manager.py
# JUMLAH BARIS : 331
#######################################################################

import ttkbootstrap as ttk
from tkinter import Menu, messagebox
import uuid
from .dashboard_frame import DashboardFrame
from flowork_kernel.api_client import ApiClient
from flowork_kernel.utils.performance_logger import log_performance
import threading
import time
class DashboardManager:
    """
    Manages adding, removing, moving, resizing, and saving the layout of widgets.
    [UPGRADED] Now supports dockable, auto-hiding side panels (fly-outs).
    [FIXED] Dock handles are now visible to trigger fly-out panels correctly.
    [UPGRADED V2] Docks are now user-configurable via a '+' menu.
    [FIXED V4] Fixed resize bug and clear layout error. CanvasArea is now a permanent fixture.
    """
    def __init__(self, host_frame, coordinator_tab, kernel, tab_id, is_new_tab=False):
        self.host_frame = host_frame
        self.coordinator_tab = coordinator_tab
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.widgets = {}
        self.tab_id = tab_id
        self.is_new_tab = is_new_tab
        self.watermark_label = None
        self._drag_data = {'widget': None, 'x': 0, 'y': 0}
        self._resize_data = {'widget': None, 'start_x': 0, 'start_y': 0, 'start_width': 0, 'start_height': 0}
        self.available_widgets = {}
        self.docks = {}
        self.docked_widgets = {"left": [], "right": []}
        self.pinned_docks = {"left": False, "right": False}
        self.hide_jobs = {"left": None, "right": None}
        self._build_ui_with_docks()
        self.host_frame.after(50, self._load_initial_data_async)
    def _build_ui_with_docks(self):
        """(REFACTORED V3) Uses .place() for all main components to ensure stable geometry management."""
        self.canvas_area = ttk.Frame(self.host_frame)
        self.canvas_area.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvas_area.bind("<Button-3>", self.show_context_menu)
        self.docks['left'] = self._create_dock_structure('left', '>')
        self.docks['right'] = self._create_dock_structure('right', '<')
        self.docks['left']['handle'].place(relx=0, rely=0, relheight=1)
        self.docks['right']['handle'].place(relx=1.0, rely=0, relheight=1, anchor='ne')
    def _create_dock_structure(self, side, handle_text):
        """(MODIFIED) Now creates handle as a direct child of host_frame for stable placement."""
        handle = ttk.Frame(self.host_frame, width=20, bootstyle="secondary")
        handle_label = ttk.Label(handle, text=handle_text, bootstyle="inverse-secondary", font=("Helvetica", 12, "bold"))
        handle_label.pack(expand=True)
        content_frame = ttk.Frame(self.host_frame, width=300, bootstyle="secondary")
        control_bar = ttk.Frame(content_frame, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        add_button = ttk.Button(control_bar, text="+", bootstyle="success-link", width=2, command=lambda s=side: self._show_add_to_dock_menu(s))
        add_button.pack(side='left')
        pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=lambda s=side: self._toggle_pin(s))
        pin_button.pack(side='right')
        handle.bind("<Enter>", lambda e, s=side: self._show_dock(s))
        content_frame.bind("<Leave>", lambda e, s=side: self._hide_dock_later(s))
        return {'frame': content_frame, 'content': content_frame, 'handle': handle, 'pin_button': pin_button}
    def _show_add_to_dock_menu(self, side):
        """Creates and shows a context menu to add any available widget to the specified dock."""
        add_menu = Menu(self.host_frame, tearoff=0)
        all_docked_widget_types = {w.content_widget.widget_id for w_list in self.docked_widgets.values() for w in w_list}
        available_for_docking = {k: v for k, v in self.available_widgets.items() if k not in all_docked_widget_types}
        if not available_for_docking:
            add_menu.add_command(label=self.loc.get('dock_no_widgets_available', fallback="No more widgets to add"), state="disabled")
        else:
            for key, info in sorted(available_for_docking.items(), key=lambda item: item[1]['title'].lower()):
                add_menu.add_command(label=info['title'], command=lambda k=key, s=side: self.add_widget_and_save(k, dock_side=s))
        try:
            add_menu.tk_popup(self.host_frame.winfo_pointerx(), self.host_frame.winfo_pointery())
        finally:
            add_menu.grab_release()
    def _toggle_pin(self, side):
        """Toggles the pinned state of a dock."""
        self.pinned_docks[side] = not self.pinned_docks[side]
        pin_char = "📌"
        self.docks[side]['pin_button'].config(text=pin_char)
        if not self.pinned_docks[side]:
            self._hide_dock_later(side)
    def _show_dock(self, side):
        """Shows a dock panel."""
        if self.hide_jobs[side]:
            self.host_frame.after_cancel(self.hide_jobs[side])
            self.hide_jobs[side] = None
        relx = 0 if side == 'left' else 1.0
        anchor = 'nw' if side == 'left' else 'ne'
        self.docks[side]['frame'].place(in_=self.host_frame, relx=relx, rely=0, relheight=1.0, anchor=anchor)
        self.docks[side]['frame'].lift()
    def _hide_dock_later(self, side):
        """Schedules a dock to be hidden after a short delay."""
        if not self.pinned_docks[side]:
            self.hide_jobs[side] = self.host_frame.after(300, lambda: self.docks[side]['frame'].place_forget())
    def _load_initial_data_async(self):
        self._create_watermark()
        threading.Thread(target=self._load_initial_data_worker, daemon=True).start()
    @log_performance("Fetching all initial data for DashboardManager")
    def _load_initial_data_worker(self):
        max_retries = 10 # (COMMENT) Increased from 5 to 10 for slower systems
        retry_delay = 0.5 # (COMMENT) seconds
        success_layout, layout_data = False, None
        success_widgets, widgets_data = False, None
        for attempt in range(max_retries):
            self.kernel.write_to_log(f"DashboardManager: Attempting to load layout (Attempt {attempt + 1}/{max_retries})", "DEBUG")
            success_widgets, widgets_data = self.api_client.get_components('widgets')
            success_layout, layout_data = self.api_client.get_dashboard_layout(self.tab_id)
            is_connection_error = not success_layout and "Connection to API server failed" in str(layout_data)
            if not is_connection_error:
                self.kernel.write_to_log(f"DashboardManager: API connection successful or non-retriable error. Proceeding.", "DEBUG")
                break
            self.kernel.write_to_log(f"DashboardManager: API not ready, retrying in {retry_delay}s...", "WARN")
            time.sleep(retry_delay)
        self.host_frame.after(0, self._on_initial_data_loaded, success_widgets, widgets_data, success_layout, layout_data)
    def _on_initial_data_loaded(self, success_widgets, widgets_data, success_layout, layout_data):
        if not success_widgets:
            self.kernel.write_to_log(f"Failed to fetch available widgets via API: {widgets_data}", "ERROR")
        else:
            for widget_data in widgets_data:
                widget_id = widget_data.get('id')
                if not widget_data.get('is_paused', False):
                    self.available_widgets[widget_id] = {"title": widget_data.get("name", widget_id)}
            self.kernel.write_to_log(f"Dashboard Manager: {len(self.available_widgets)} widgets available.", "DEBUG")
        if not success_layout:
            self.kernel.write_to_log(f"Failed to load layout for tab {self.tab_id}: {layout_data}", "ERROR")
        elif layout_data:
            self._remove_watermark()
            for widget_id, config in layout_data.items():
                widget_type = config.get("type")
                if widget_type in self.available_widgets:
                    dock_side = config.get("dock")
                    self.add_widget(
                        widget_type,
                        config.get("x", 10),
                        config.get("y", 10),
                        config.get("width", 400),
                        config.get("height", 300),
                        existing_id=widget_id,
                        dock_side=dock_side
                    )
                else:
                    self.kernel.write_to_log(f"Widget type '{widget_type}' from saved layout could not be loaded (likely disabled or uninstalled).", "WARN")
        canvas_area_exists = any(
            hasattr(frame, 'content_widget') and frame.content_widget.widget_id == 'canvas_area'
            for frame in self.widgets.values()
        )
        if not canvas_area_exists:
            self.add_widget("canvas_area", 0, 0, 0, 0)
            self.kernel.write_to_log("DashboardManager: Core 'canvas_area' was not in the layout, re-initializing it.", "INFO")
        if not self.widgets:
            if self.is_new_tab:
                self._load_default_layout()
            else:
                 self._create_watermark()
    def _create_watermark(self):
        if not self.canvas_area.winfo_exists(): return
        if self.watermark_label and self.watermark_label.winfo_exists(): return
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        colors = theme_manager.get_colors()
        watermark_color = colors.get('border', '#555555')
        self.watermark_label = ttk.Label(
            self.canvas_area,
            text="www.teetah.art",
            font=("Helvetica", 40, "bold"),
            foreground=watermark_color,
            anchor="center"
        )
        self.watermark_label.place(relx=0.5, rely=0.5, anchor="center")
        self.watermark_label.lower()
    def _remove_watermark(self):
        if self.watermark_label and self.watermark_label.winfo_exists():
            self.watermark_label.destroy()
            self.watermark_label = None
    def clear_all_widgets(self):
        for widget_id in list(self.widgets.keys()):
            self.remove_widget(widget_id) # remove_widget handles destroying and unregistering from all lists.
        self.save_layout()
        self._create_watermark()
    @log_performance("Loading default dashboard layout")
    def _load_default_layout(self):
        self.kernel.write_to_log(f"DashboardManager for tab {self.tab_id} is loading a default layout.", "INFO")
        self._remove_watermark()
        self.add_widget("logic_toolbox_widget", dock_side='left')
        self.add_widget("plugin_toolbox_widget", dock_side='left')
        self.add_widget("widget_toolbox", dock_side='left')
        self.add_widget("log_viewer_widget", dock_side='right')
        self.add_widget("canvas_area", 0, 0, 0, 0)
        self.save_layout()
    def save_layout(self):
        layout = {}
        for widget_id, frame in self.widgets.items():
            if hasattr(frame, 'content_widget') and hasattr(frame.content_widget, 'widget_id'):
                widget_type_key = frame.content_widget.widget_id
                dock_side = None
                if frame in self.docked_widgets['left']:
                    dock_side = 'left'
                elif frame in self.docked_widgets['right']:
                    dock_side = 'right'
                if dock_side:
                    layout[widget_id] = {"type": widget_type_key, "dock": dock_side}
                elif widget_type_key != 'canvas_area':
                    if widget_type_key in self.available_widgets:
                        layout[widget_id] = {"type": widget_type_key, "x": frame.winfo_x(), "y": frame.winfo_y(), "width": frame.winfo_width(), "height": frame.winfo_height()}
        success, response = self.api_client.save_dashboard_layout(self.tab_id, layout)
        if not success:
            self.kernel.write_to_log(f"Failed to save layout via API: {response}", "ERROR")
    def add_widget(self, widget_type_key, x=0, y=0, width=400, height=300, existing_id=None, dock_side=None):
        widget_manager_service = self.kernel.get_service("widget_manager_service")
        if widget_manager_service and widget_type_key in widget_manager_service.loaded_widgets:
            widget_data = widget_manager_service.loaded_widgets[widget_type_key]
            WidgetClass = widget_data.get("class")
            if WidgetClass and hasattr(WidgetClass, 'TIER'):
                required_tier = WidgetClass.TIER
                if not self.kernel.is_tier_sufficient(required_tier):
                    widget_name = widget_data.get("name", widget_type_key)
                    messagebox.showwarning(
                        self.loc.get('license_popup_title'),
                        self.loc.get('license_popup_message', module_name=widget_name),
                        parent=self.host_frame.winfo_toplevel()
                    )
                    tab_manager = self.kernel.get_service("tab_manager_service")
                    if tab_manager: tab_manager.open_managed_tab("pricing_page")
                    return
        self._remove_watermark()
        widget_info = self.available_widgets.get(widget_type_key)
        if not widget_info:
            self.kernel.write_to_log(f"Failed to add widget: Type '{widget_type_key}' not found or is disabled.", "ERROR")
            return
        widget_class_info = widget_manager_service.loaded_widgets[widget_type_key]
        widget_class = widget_class_info["class"]
        widget_id = existing_id or str(uuid.uuid4())
        frame = None
        if dock_side == 'left':
            frame = DashboardFrame(self.docks['left']['content'], self, widget_id, widget_info["title"], widget_class, content_widget_id=widget_type_key)
            frame.pack(fill='x', pady=5)
            self.docked_widgets['left'].append(frame)
        elif dock_side == 'right':
            frame = DashboardFrame(self.docks['right']['content'], self, widget_id, widget_info["title"], widget_class, content_widget_id=widget_type_key)
            frame.pack(fill='both', expand=True, pady=5)
            self.docked_widgets['right'].append(frame)
        else:
            frame = DashboardFrame(self.canvas_area, self, widget_id, widget_info["title"], widget_class, content_widget_id=widget_type_key)
            if widget_type_key == 'canvas_area':
                frame.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                frame.place(x=x, y=y, width=width, height=height)
        self.widgets[widget_id] = frame
        if hasattr(frame.content_widget, 'on_widget_load'):
            frame.content_widget.on_widget_load()
        core_widget_ids = ["canvas_area", "log_viewer_widget", "logic_toolbox_widget", "plugin_toolbox_widget", "preset_manager", "widget_toolbox"]
        if widget_type_key in core_widget_ids:
            setattr(self.coordinator_tab, f"{widget_type_key}_instance", frame.content_widget)
    def remove_widget(self, widget_id):
        if widget_id in self.widgets:
            frame_to_remove = self.widgets[widget_id]
            widget_type_key = frame_to_remove.content_widget.widget_id
            if hasattr(self.coordinator_tab, f"{widget_type_key}_instance"):
                setattr(self.coordinator_tab, f"{widget_type_key}_instance", None)
            if hasattr(frame_to_remove.content_widget, 'on_widget_destroy'):
                frame_to_remove.content_widget.on_widget_destroy()
            if frame_to_remove in self.docked_widgets['left']:
                self.docked_widgets['left'].remove(frame_to_remove)
            if frame_to_remove in self.docked_widgets['right']:
                self.docked_widgets['right'].remove(frame_to_remove)
            frame_to_remove.destroy()
            del self.widgets[widget_id]
            if not self.widgets:
                self._create_watermark()
    def start_drag(self, widget, event):
        if widget.master == self.canvas_area:
            widget.lift()
            self._drag_data['widget'] = widget
            self._drag_data['x'] = event.x
            self._drag_data['y'] = event.y
    def drag_widget(self, event):
        if self._drag_data['widget']:
            dx = event.x - self._drag_data['x']
            dy = event.y - self._drag_data['y']
            x = self._drag_data['widget'].winfo_x() + dx
            y = self._drag_data['widget'].winfo_y() + dy
            self._drag_data['widget'].place(x=x, y=y)
    def stop_drag(self, event):
        self._drag_data['widget'] = None
        self.save_layout()
    def start_resize(self, widget, event):
        self._resize_data['widget'] = widget
        self._resize_data['start_x'] = event.x_root
        self._resize_data['start_y'] = event.y_root
        self._resize_data['start_width'] = widget.winfo_width()
        self._resize_data['start_height'] = widget.winfo_height()
    def resize_widget(self, event):
        if self._resize_data['widget']:
            dx = event.x_root - self._resize_data['start_x']
            dy = event.y_root - self._resize_data['start_y']
            new_width = self._resize_data['start_width'] + dx
            new_height = self._resize_data['start_height'] + dy
            if new_width > 150 and new_height > 100:
                self._resize_data['widget'].place(width=new_width, height=new_height)
    def stop_resize(self, event):
        self._resize_data['widget'] = None
        self.save_layout()
    def _create_add_widget_menu(self, event_x=10, event_y=10):
        """ (MODIFIED) This context menu is now for adding FLOATING widgets to the canvas area. """
        context_menu = Menu(self.canvas_area, tearoff=0)
        sorted_widgets = sorted(self.available_widgets.items(), key=lambda item: item[1]['title'].lower())
        dock_exclusive_widgets = {"logic_toolbox_widget", "plugin_toolbox_widget", "widget_toolbox", "log_viewer_widget"}
        has_addable_widgets = False
        for key, info in sorted_widgets:
            if key not in dock_exclusive_widgets:
                context_menu.add_command(label=info['title'], command=lambda k=key, x=event_x, y=event_y: self.add_widget_and_save(k, x=x, y=y))
                has_addable_widgets = True
        if not has_addable_widgets:
            context_menu.add_command(label="No non-dockable widgets available", state="disabled")
        return context_menu
    @log_performance("Showing dashboard context menu")
    def show_context_menu(self, event):
        context_menu = self._create_add_widget_menu(event_x=event.x, event_y=event.y)
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    def add_widget_and_save(self, widget_type_key, x=0, y=0, dock_side=None):
        self.add_widget(widget_type_key, x, y, dock_side=dock_side)
        self.save_layout()
