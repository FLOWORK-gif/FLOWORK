#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\widgets\plugin_toolbox_widget\plugin_toolbox_widget.py
# JUMLAH BARIS : 130
#######################################################################

from flowork_gui.core import build_security
import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, StringVar, messagebox
from flowork_gui.api_contract import BaseDashboardWidget
from flowork_gui.views.custom_widgets.tooltip import ToolTip
from flowork_gui.utils.performance_logger import log_performance # PENAMBAHAN: Importing utility from its new local GUI path.
import threading
import time
from flowork_gui.api_client.client import ApiClient
class PluginToolboxWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget to display the Action and Plugin toolbox.
    (FIXED V2) Correctly fetches and filters both ACTION modules and PLUGIN components.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.parent_tab = coordinator_tab
        self.api_client = ApiClient(kernel=self.kernel)
        self.search_var = StringVar()
        self.search_var.trace_add("write", self._on_search)
        self._debounce_job = None
        self._create_widgets()
        self.refresh_content()
    def on_widget_load(self):
        super().on_widget_load()
    def _create_widgets(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(2, weight=0)
        search_icon_label = ttk.Label(search_frame, text="", font=("Font Awesome 6 Free Solid", 9))
        search_icon_label.grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")
        ToolTip(search_entry).update_text("Type to search plugins...") # English Hardcode
        reload_button = ttk.Button(search_frame, text="⟳", width=3, command=self._force_reload_and_refresh, style="secondary.TButton")
        reload_button.grid(row=0, column=2, padx=(5,0))
        ToolTip(reload_button).update_text("Reload component list") # English Hardcode
        ttk.Label(self, text=self.loc.get('action_plugins_title', fallback="Action & Plugin Toolbox"), style='TLabel').pack(pady=5, anchor='w', padx=5)
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
    def _force_reload_and_refresh(self):
        for i in self.plugin_tree.get_children():
            self.plugin_tree.delete(i)
        self.plugin_tree.insert("", "end", text="  Reloading and Refreshing...", tags=("loading",)) # English Hardcode
        threading.Thread(target=self._load_data_worker, args=(True,), daemon=True).start()
    @log_performance("Fetching data for PluginToolbox")
    def _load_data_worker(self, force_reload: bool = False):
        if force_reload:
            pass
            time.sleep(1)
        success_modules, modules_data = self.api_client.get_components('modules')
        success_plugins, plugins_data = self.api_client.get_components('plugins')
        combined_data = []
        if success_modules:
            combined_data.extend(modules_data)
        if success_plugins:
            combined_data.extend(plugins_data)
        self.after(0, self.populate_plugin_panel, True, combined_data)
    def populate_plugin_panel(self, success=True, all_components_data=None):
        if all_components_data:
            for comp in all_components_data:
                pass
        search_query = self.search_var.get().strip().lower()
        for i in self.plugin_tree.get_children():
            self.plugin_tree.delete(i)
        if all_components_data is None:
            threading.Thread(target=self._load_data_worker, daemon=True).start()
            return
        if not success:
            self.plugin_tree.insert('', 'end', text="  Error: Could not fetch components...") # English Hardcode
            return
        filtered_components = [
            comp for comp in all_components_data
            if comp.get('manifest', {}).get('type') in ['ACTION', 'PLUGIN']
        ]
        components_to_display = []
        if not search_query:
            for data in filtered_components:
                 components_to_display.append((data['id'], data))
            sorted_components = sorted(components_to_display, key=lambda item: item[1].get('name', item[0]).lower())
        else:
            for data in filtered_components:
                search_haystack = f"{data.get('name','')} {data.get('description','')}".lower()
                if search_query in search_haystack:
                    components_to_display.append((data['id'], data))
            sorted_components = components_to_display
        for comp_id, comp_data in sorted_components:
            tier = comp_data.get('tier', 'free').capitalize()
            display_name = comp_data.get('name', 'Unknown')
            label = f" {display_name}"
            if tier.lower() != 'free':
                label += f" [{tier}]"
            is_sufficient = True # Placeholder
            tag = 'sufficient' if is_sufficient else 'insufficient'
            self.plugin_tree.insert('', 'end', iid=comp_id, text=label, tags=(tag, tier.lower()))
        self.plugin_tree.tag_configure('insufficient', foreground='grey')
        self.update_idletasks()
    def on_drag_start(self, event):
        item_id = self.plugin_tree.identify_row(event.y)
        if not item_id or 'category' in self.plugin_tree.item(item_id, "tags"): return
        tags = self.plugin_tree.item(item_id, "tags")
        if 'insufficient' in tags:
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name=self.plugin_tree.item(item_id, "text").strip()),
                parent=self.winfo_toplevel()
            )
            return
        self.parent_tab.on_drag_start(event)
    def refresh_content(self, event_data=None):
        """Called to refresh the widget list if there are changes."""
        threading.Thread(target=self._load_data_worker, args=(False,), daemon=True).start()
