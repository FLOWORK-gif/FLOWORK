#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\widgets\data_canvas_widget\data_canvas_widget.py
# JUMLAH BARIS : 77
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk
import json
from flowork_kernel.api_contract import BaseDashboardWidget, IDataPreviewer
class DataCanvasWidget(BaseDashboardWidget):
    TIER = "basic"
    """
    The UI for the Data Canvas. It displays a version of the workflow focused
    on previewing the data output of each configured node in real-time.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.parent_tab = coordinator_tab
        self.data_node_widgets = {} # Stores the UI elements for each node on this canvas
        canvas_container = ttk.Frame(self)
        canvas_container.pack(fill='both', expand=True)
        self.canvas = ttk.Canvas(canvas_container)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.kernel.write_to_log("Data Canvas Widget Initialized.", "SUCCESS")
    def sync_with_logic_canvas(self, logic_canvas_nodes):
        """
        Receives the node data from the main logic canvas and rebuilds the
        Data Canvas UI based on it.
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.data_node_widgets.clear()
        if not logic_canvas_nodes:
            ttk.Label(self.scrollable_frame, text="Tambahkan node di Tampilan Logika untuk melihat preview data di sini.").pack(pady=50)
            return
        module_manager = self.kernel.get_service("module_manager_service")
        for node_id, node_data in logic_canvas_nodes.items():
            module_id = node_data.get('module_id')
            node_name = node_data.get('name', 'Unknown')
            node_frame = ttk.LabelFrame(self.scrollable_frame, text=f"{node_name} ({module_id})", padding=10)
            node_frame.pack(fill='x', expand=True, padx=10, pady=5)
            module_instance = module_manager.get_instance(module_id)
            if isinstance(module_instance, IDataPreviewer):
                try:
                    preview_data = module_instance.get_data_preview(node_data.get('config_values', {}))
                    if isinstance(preview_data, list) and preview_data and isinstance(preview_data[0], dict):
                        columns = list(preview_data[0].keys())
                        tree = tk_ttk.Treeview(node_frame, columns=columns, show="headings", height=min(len(preview_data), 5))
                        for col in columns:
                            tree.heading(col, text=col.replace("_", " ").title())
                            tree.column(col, width=120)
                        for item in preview_data:
                            tree.insert("", "end", values=[str(item.get(col, '')) for col in columns])
                        tree.pack(fill='both', expand=True)
                    else:
                        pretty_data = json.dumps(preview_data, indent=2, ensure_ascii=False)
                        text_area = ttk.Text(node_frame, height=5, wrap="word", font=("Consolas", 9))
                        text_area.insert("1.0", pretty_data)
                        text_area.config(state="disabled")
                        text_area.pack(fill='both', expand=True)
                except Exception as e:
                    ttk.Label(node_frame, text=f"Error generating preview: {e}", bootstyle="danger").pack()
            else:
                ttk.Label(node_frame, text=" (Modul ini tidak mendukung data preview) ", bootstyle="secondary").pack()
