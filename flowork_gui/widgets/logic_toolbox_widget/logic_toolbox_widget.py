#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\widgets\logic_toolbox_widget\logic_toolbox_widget.py
# JUMLAH BARIS : 121
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
class LogicToolboxWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget to display the Logic and Control Flow Modules toolbox.
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
        ToolTip(search_entry).update_text("Type your goal (e.g., 'read a csv file') to search...") # English Hardcode
        reload_button = ttk.Button(search_frame, text="⟳", width=3, command=self._force_reload_and_refresh, style="secondary.TButton")
        reload_button.grid(row=0, column=2, padx=(5,0))
        ToolTip(reload_button).update_text("Reload component list") # English Hardcode
        ttk.Label(self, text=self.loc.get('logic_modules_title', fallback="Logic Modules")).pack(pady=5, anchor='w', padx=5)
        self.module_tree = tk_ttk.Treeview(self, columns=(), style="Custom.Treeview", selectmode="browse")
        self.module_tree.heading('#0', text=self.loc.get('module_name_column', fallback="Module Name"))
        self.module_tree.pack(expand=True, fill='both', side='top', padx=5, pady=(0,5))
        self.module_tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.module_tree.bind("<B1-Motion>", self.parent_tab.on_drag_motion)
        self.module_tree.bind("<ButtonRelease-1>", self.parent_tab.on_drag_release)
    def _on_search(self, *args):
        if self._debounce_job:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(300, self.populate_module_toolbox)
    def _force_reload_and_refresh(self):
        for i in self.module_tree.get_children():
            self.module_tree.delete(i)
        self.module_tree.insert("", "end", text="  Reloading and Refreshing...", tags=("loading",)) # English Hardcode
        threading.Thread(target=self._load_data_worker, args=(True,), daemon=True).start()
    @log_performance("Fetching module list for LogicToolbox")
    def _load_data_worker(self, force_reload: bool = False):
        if force_reload:
            pass
            time.sleep(1)
        success, all_modules_data = self.api_client.get_components('modules')
        self.after(0, self.populate_module_toolbox, success, all_modules_data)
    def populate_module_toolbox(self, success=True, all_modules_data=None):
        if all_modules_data:
            for comp in all_modules_data:
                pass
        search_query = self.search_var.get().strip().lower()
        for i in self.module_tree.get_children():
            self.module_tree.delete(i)
        if all_modules_data is None:
            success, all_modules_data = self.api_client.get_components('modules')
        if not success:
            self.module_tree.insert('', 'end', text="  Error: Could not fetch modules...") # English Hardcode
            return
        logic_modules_data = [
            mod for mod in all_modules_data
            if mod.get('manifest', {}).get('type') in ['LOGIC', 'CONTROL_FLOW']
        ]
        modules_to_display = []
        if not search_query:
            for module_data in logic_modules_data:
                 modules_to_display.append((module_data['id'], module_data))
            sorted_modules = sorted(modules_to_display, key=lambda item: item[1].get('name', item[0]).lower())
        else:
            for module_data in logic_modules_data:
                search_haystack = f"{module_data.get('name','')} {module_data.get('description','')}".lower()
                if search_query in search_haystack:
                    modules_to_display.append((module_data['id'], module_data))
            sorted_modules = modules_to_display
        for module_id, module_data in sorted_modules:
            tier = module_data.get('tier', 'free').capitalize()
            display_name = module_data.get('name', 'Unknown')
            label = f" {display_name}"
            if tier.lower() != 'free':
                label += f" [{tier}]"
            is_sufficient = True # Placeholder
            tag = 'sufficient' if is_sufficient else 'insufficient'
            self.module_tree.insert('', 'end', iid=module_id, text=label, tags=(tag, tier.lower()))
        self.module_tree.tag_configure('insufficient', foreground='grey')
        self.update_idletasks()
    def on_drag_start(self, event):
        item_id = self.module_tree.identify_row(event.y)
        if not item_id or 'category' in self.module_tree.item(item_id, "tags"): return
        tags = self.module_tree.item(item_id, "tags")
        if 'insufficient' in tags:
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name=self.module_tree.item(item_id, "text").strip()),
                parent=self.winfo_toplevel()
            )
            return
        self.parent_tab.on_drag_start(event)
    def refresh_content(self, event_data=None):
        threading.Thread(target=self._load_data_worker, args=(False,), daemon=True).start()
