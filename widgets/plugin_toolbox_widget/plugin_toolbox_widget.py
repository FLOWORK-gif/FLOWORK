from flowork_kernel.core import build_security
from flowork_kernel.core import build_security
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\widgets\plugin_toolbox_widget\plugin_toolbox_widget.py
# (Full code for the modified file)
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, StringVar, messagebox
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_kernel.api_client import ApiClient
from flowork_kernel.utils.performance_logger import log_performance
import threading
import time # (ADDED) Import time for delay after reload

class PluginToolboxWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget to display the Action Plugins toolbox.
    (MODIFIED) Refresh logic is now separated for manual trigger vs. event-driven update to prevent loops.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        build_security.perform_runtime_check(__file__)
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.parent_tab = coordinator_tab
        self.api_client = ApiClient(kernel=self.kernel)
        self.search_var = StringVar()
        self.search_var.trace_add("write", self._on_search)
        self._debounce_job = None
        self._create_widgets()
        # (MODIFIED) Initial load is now an event-driven refresh, not a forced reload.
        self.refresh_content()

    def on_widget_load(self):
        super().on_widget_load()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe("COMPONENT_LIST_CHANGED", f"plugin_toolbox_{self.widget_id}", self.refresh_content)
            self.kernel.write_to_log(f"PluginToolboxWidget ({self.widget_id}) is now subscribed to component changes.", "DEBUG")

    def _create_widgets(self):
        # ... (kode di sini tidak berubah)
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(2, weight=0)
        search_icon_label = ttk.Label(search_frame, text="", font=("Font Awesome 6 Free Solid", 9))
        search_icon_label.grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")
        ToolTip(search_entry).update_text("Type to search plugins...")
        reload_button = ttk.Button(search_frame, text="⟳", width=3, command=self._force_reload_and_refresh, style="secondary.TButton")
        reload_button.grid(row=0, column=2, padx=(5,0))
        ToolTip(reload_button).update_text("Reload component list")
        ttk.Label(self, text=self.loc.get('action_plugins_title', fallback="Action Plugins"), style='TLabel').pack(pady=5, anchor='w', padx=5)
        self.plugin_tree = tk_ttk.Treeview(self, columns=(), style="Custom.Treeview", selectmode="browse")
        self.plugin_tree.heading('#0', text=self.loc.get('plugin_name_column', fallback="Plugin Name"))
        self.plugin_tree.pack(expand=True, fill='both', side='top', padx=5, pady=(0,5))
        self.plugin_tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.plugin_tree.bind("<B1-Motion>", self.parent_tab.on_drag_motion)
        self.plugin_tree.bind("<ButtonRelease-1>", self.parent_tab.on_drag_release)

    def _on_search(self, *args):
        if self._debounce_job:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(300, self.populate_plugin_panel)

    # (MODIFIED) This function is now ONLY for the manual refresh button.
    def _force_reload_and_refresh(self):
        for i in self.plugin_tree.get_children():
            self.plugin_tree.delete(i)
        self.plugin_tree.insert("", "end", text="  Reloading and Refreshing...", tags=("loading",))
        threading.Thread(target=self._load_data_worker, args=(True,), daemon=True).start()

    # (MODIFIED) The worker now accepts a 'force_reload' flag.
    @log_performance("Fetching plugin list for PluginToolbox")
    def _load_data_worker(self, force_reload: bool = False):
        if force_reload:
            self.api_client.trigger_hot_reload()
            time.sleep(1)

        success, all_plugins_data = self.api_client.get_components('plugins')
        self.after(0, self.populate_plugin_panel, success, all_plugins_data)

    def populate_plugin_panel(self, success=True, all_plugins_data=None):
        # ... (kode di sini tidak berubah)
        search_query = self.search_var.get().strip().lower()
        for i in self.plugin_tree.get_children():
            self.plugin_tree.delete(i)
        if all_plugins_data is None:
            success, all_plugins_data = self.api_client.get_components('plugins')
        if not success:
            self.plugin_tree.insert('', 'end', text="  Error: Could not fetch plugins...")
            return
        plugins_to_display = []
        if not search_query:
            for plugin_data in all_plugins_data:
                plugins_to_display.append((plugin_data['id'], plugin_data))
            sorted_plugins = sorted(plugins_to_display, key=lambda item: item[1].get('name', item[0]).lower())
        else:
            for plugin_data in all_plugins_data:
                search_haystack = f"{plugin_data.get('name','')} {plugin_data.get('description','')}".lower()
                if search_query in search_haystack:
                    plugins_to_display.append((plugin_data['id'], plugin_data))
            sorted_plugins = plugins_to_display
        for module_id, manifest_data in sorted_plugins:
            tier = manifest_data.get('tier', 'free').capitalize()
            display_name = manifest_data.get('name', 'Unknown')
            label = f" {display_name}"
            if tier.lower() != 'free':
                label += f" [{tier}]"
            is_sufficient = self.kernel.is_tier_sufficient(tier.lower())
            tag = 'sufficient' if is_sufficient else 'insufficient'
            self.plugin_tree.insert('', 'end', iid=module_id, text=label, tags=(tag, tier.lower()))
        self.plugin_tree.tag_configure('insufficient', foreground='grey')
        self.update_idletasks()

    def on_drag_start(self, event):
        # ... (kode di sini tidak berubah)
        item_id = self.plugin_tree.identify_row(event.y)
        if not item_id or 'category' in self.plugin_tree.item(item_id, "tags"): return
        tags = self.plugin_tree.item(item_id, "tags")
        if 'insufficient' in tags:
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name=self.plugin_tree.item(item_id, "text").strip()),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager: tab_manager.open_managed_tab("pricing_page")
            return
        self.parent_tab.on_drag_start(event)

    # (MODIFIED) This function, called by the event bus, now only refreshes data.
    def refresh_content(self, event_data=None):
        self.kernel.write_to_log("PluginToolboxWidget received signal to refresh from EventBus.", "INFO")
        threading.Thread(target=self._load_data_worker, args=(False,), daemon=True).start()

_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature


_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
