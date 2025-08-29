#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\widgets\widget_toolbox\widget_toolbox_widget.py
# JUMLAH BARIS : 99
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from tkinter import StringVar
from flowork_kernel.api_client import ApiClient
import threading
from flowork_kernel.utils.performance_logger import log_performance
class WidgetToolboxWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget to display the toolbox of available widgets.
    [MODIFICATION] Added a manual reload button for immediate UI refresh.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.coordinator_tab = coordinator_tab
        self.api_client = ApiClient(kernel=self.kernel)
        self.search_var = StringVar()
        self.search_var.trace_add("write", self._on_search)
        self._create_widgets()
        self._load_initial_data()
    def on_widget_load(self):
        """Called by DashboardManager when the widget is fully loaded."""
        super().on_widget_load()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe("COMPONENT_LIST_CHANGED", f"widget_toolbox_{self.widget_id}", self.refresh_content)
            self.kernel.write_to_log(f"WidgetToolboxWidget ({self.widget_id}) is now subscribed to component changes.", "DEBUG")
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(2, weight=0)
        search_icon_label = ttk.Label(search_frame, text="", font=("Font Awesome 6 Free Solid", 9))
        search_icon_label.grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")
        ToolTip(search_entry).update_text("Type to search widgets...")
        reload_button = ttk.Button(search_frame, text="⟳", width=3, command=self._load_initial_data, style="secondary.TButton")
        reload_button.grid(row=0, column=2, padx=(5,0))
        ToolTip(reload_button).update_text("Reload component list")
        ttk.Label(self, text=self.loc.get('available_widgets_header', fallback="Available Widgets")).grid(row=1, column=0, sticky='w', padx=5, pady=(5,0))
        self.widget_tree = tk_ttk.Treeview(self, show="tree", selectmode="browse")
        self.widget_tree.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        self.widget_tree.bind("<Double-1>", self._on_widget_select)
    def _on_search(self, *args):
        self.populate_widget_toolbox()
    def _load_initial_data(self):
        for i in self.widget_tree.get_children():
            self.widget_tree.delete(i)
        self.widget_tree.insert("", "end", text="  Loading widgets from API...", tags=("loading",))
        threading.Thread(target=self._load_data_worker, daemon=True).start()
    @log_performance("Fetching widget list for WidgetToolbox")
    def _load_data_worker(self):
        success, all_widgets_data = self.api_client.get_components('widgets')
        self.after(0, self.populate_widget_toolbox, success, all_widgets_data)
    def populate_widget_toolbox(self, success=True, all_widgets_data=None):
        filter_text = self.search_var.get().lower()
        for item in self.widget_tree.get_children():
            self.widget_tree.delete(item)
        if all_widgets_data is None:
             success, all_widgets_data = self.api_client.get_components('widgets')
        if not success:
            self.widget_tree.insert("", "end", text="  Error: Could not fetch widgets...")
            return
        widgets_to_display = []
        if not filter_text:
            for widget_data in all_widgets_data:
                 widgets_to_display.append((widget_data['id'], widget_data.get('name', widget_data['id'])))
            sorted_widgets = sorted(widgets_to_display, key=lambda item: item[1].lower())
        else:
            for widget_data in all_widgets_data:
                search_haystack = f"{widget_data.get('name','')} {widget_data.get('description','')}".lower()
                if filter_text in search_haystack:
                    widgets_to_display.append((widget_data['id'], widget_data.get('name', widget_data['id'])))
            sorted_widgets = widgets_to_display
        for key, title in sorted_widgets:
            self.widget_tree.insert("", "end", iid=key, text=title)
        self.update_idletasks()
    def _on_widget_select(self, event):
        item_id = self.widget_tree.focus()
        if item_id:
            dashboard_manager = self.coordinator_tab.dashboard_manager
            if dashboard_manager:
                dashboard_manager.add_widget_and_save(item_id, event.x, event.y)
    def refresh_content(self, event_data=None):
        """Called by MainWindow to refresh the widget list if there are changes."""
        self.kernel.write_to_log("WidgetToolboxWidget received signal to refresh.", "INFO")
        self._load_initial_data()
