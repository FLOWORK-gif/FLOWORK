#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_components\logic_builder_canvas.py
# JUMLAH BARIS : 113
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk
from flowork_kernel.ui_shell.canvas_manager import CanvasManager
class LogicBuilderCanvas(ttk.Frame):
    """
    Kanvas visual untuk merancang logika 'execute' dari sebuah modul baru.
    Ini adalah implementasi dari "Logic Builder Canvas" pada Manifesto Flowork.
    [FIXED V2] Toolbox now dynamically loads all available LOGIC and ACTION modules.
    """
    def __init__(self, parent, kernel):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.canvas_manager = None
        self._drag_data = {}
        self._create_widgets()
    def _create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill="both", expand=True)
        toolbox_frame = ttk.LabelFrame(main_pane, text="Node Logika Dasar", padding=10)
        main_pane.add(toolbox_frame, weight=0)
        self.logic_node_tree = tk_ttk.Treeview(toolbox_frame, show="tree", selectmode="browse")
        self.logic_node_tree.pack(expand=True, fill='both')
        self._populate_logic_toolbox()
        canvas_container = ttk.Frame(main_pane)
        main_pane.add(canvas_container, weight=4)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        class DummyCoordinatorTab(ttk.Frame):
            def __init__(self, kernel, logic_builder_instance):
                super().__init__(logic_builder_instance)
                self.kernel = kernel
                self._execution_state = "IDLE"
                self.logic_builder_instance = logic_builder_instance
            def on_drag_start(self, event):
                self.logic_builder_instance.on_drag_start(event)
            def on_drag_motion(self, event):
                self.logic_builder_instance.on_drag_motion(event)
            def on_drag_release(self, event):
                self.logic_builder_instance.on_drag_release(event)
        dummy_tab = DummyCoordinatorTab(self.kernel, self)
        self.canvas = ttk.Canvas(canvas_container, background=colors.get('bg', '#222'))
        self.canvas.pack(expand=True, fill='both')
        self.canvas_manager = CanvasManager(canvas_container, dummy_tab, self.canvas, self.kernel)
        self.logic_node_tree.bind("<ButtonPress-1>", self.on_drag_start)
    def _populate_logic_toolbox(self):
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager:
            self.logic_node_tree.insert('', 'end', text="Error: ModuleManager not found.")
            return
        logic_modules = {}
        action_modules = {}
        for mod_id, mod_data in module_manager.loaded_modules.items():
            manifest = mod_data.get("manifest", {})
            mod_type = manifest.get("type")
            if mod_type == "LOGIC" or mod_type == "CONTROL_FLOW":
                logic_modules[mod_id] = manifest.get("name", mod_id)
            elif mod_type == "ACTION":
                action_modules[mod_id] = manifest.get("name", mod_id)
        if logic_modules:
            logic_category = self.logic_node_tree.insert('', 'end', iid='logic_category', text='Logic & Control Flow', open=True)
            for mod_id, name in sorted(logic_modules.items(), key=lambda item: item[1]):
                 self.logic_node_tree.insert(logic_category, 'end', iid=mod_id, text=f" {name}")
        if action_modules:
            action_category = self.logic_node_tree.insert('', 'end', iid='action_category', text='Actions', open=True)
            for mod_id, name in sorted(action_modules.items(), key=lambda item: item[1]):
                 self.logic_node_tree.insert(action_category, 'end', iid=mod_id, text=f" {name}")
    def get_logic_data(self):
        """Mengambil data dari kanvas untuk disimpan."""
        if self.canvas_manager:
            return self.canvas_manager.get_workflow_data()
        return {"nodes": [], "connections": []}
    def load_logic_data(self, logic_data):
        """Memuat data ke kanvas."""
        if self.canvas_manager and logic_data:
            self.canvas_manager.load_workflow_data(logic_data)
    def on_drag_start(self, event):
        tree_widget = event.widget
        item_id = tree_widget.identify_row(event.y)
        if not item_id or 'category' in tree_widget.item(item_id, "tags") or not tree_widget.parent(item_id):
            return
        self._drag_data = {
            "item_id": item_id,
            "widget": ttk.Label(self.winfo_toplevel(), text=tree_widget.item(item_id, "text").strip(), style='Ghost.TLabel'),
            "tree_widget": tree_widget
        }
        self.winfo_toplevel().bind("<B1-Motion>", self.on_drag_motion)
        self.winfo_toplevel().bind("<ButtonRelease-1>", self.on_drag_release)
    def on_drag_motion(self, event):
        if self._drag_data.get("widget"):
            self._drag_data['widget'].place(
                x=event.x_root - self.winfo_toplevel().winfo_rootx(),
                y=event.y_root - self.winfo_toplevel().winfo_rooty()
            )
    def on_drag_release(self, event):
        if self._drag_data.get("widget"):
            self._drag_data["widget"].destroy()
        if self.canvas_manager and self._drag_data.get("item_id"):
            self.canvas_manager.interaction_manager.on_drag_release(
                event,
                self._drag_data["item_id"],
                self._drag_data["tree_widget"]
            )
        self._drag_data = {}
        self.winfo_toplevel().unbind("<B1-Motion>")
        self.winfo_toplevel().unbind("<ButtonRelease-1>")
