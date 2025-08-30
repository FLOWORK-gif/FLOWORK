#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_components\interaction_manager.py
# JUMLAH BARIS : 84
#######################################################################

from tkinter import Menu
from ..properties_popup import PropertiesPopup
from .interactions.node_interaction_handler import NodeInteractionHandler
from .interactions.connection_interaction_handler import ConnectionInteractionHandler
from .interactions.canvas_navigation_handler import CanvasNavigationHandler
class InteractionManager:
    """
    Manages all user interactions with the canvas by coordinating specialized handlers.
    (FIXED) Now correctly resets the node handler's move data to the new format.
    """
    def __init__(self, canvas_manager, kernel, canvas_widget):
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.canvas = canvas_widget
        self.loc = self.kernel.get_service("localization_manager")
        self.node_handler = NodeInteractionHandler(self.canvas_manager)
        self.connection_handler = ConnectionInteractionHandler(self.canvas_manager)
        self.navigation_handler = CanvasNavigationHandler(self.canvas_manager)
        self._drag_data = {}
        self._resize_data = {} # (COMMENT) Added missing initialization for resize data
    def bind_events(self):
        """Binds all canvas events to the appropriate specialized handlers."""
        self.canvas.bind("<Motion>", self.connection_handler.on_line_motion)
        self.canvas.tag_bind("connection_line", "<ButtonPress-3>", self.connection_handler.show_line_context_menu)
        self.canvas.bind("<ButtonPress-2>", self.navigation_handler.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.navigation_handler.on_pan_move)
        self.canvas.bind("<ButtonRelease-2>", self.navigation_handler.on_pan_end)
        self.canvas.bind("<Delete>", self.node_handler.on_delete_key_press)
        self.canvas.bind("<ButtonPress-1>", self.canvas_manager.node_manager.deselect_all_nodes)
        self.canvas.bind("<ButtonPress-3>", self._handle_canvas_right_click)
    def _handle_canvas_right_click(self, event):
        """Decides whether to cancel line drawing or show the context menu."""
        if self.connection_handler._line_data.get("line_id"):
            self.connection_handler._cancel_line_drawing(event)
        else:
            self._show_canvas_context_menu(event)
    def _show_canvas_context_menu(self, event):
        """Displays the main canvas context menu for adding modules or text notes."""
        context_menu = Menu(self.canvas, tearoff=0)
        context_menu.add_command(
            label=self.loc.get('context_menu_add_note', fallback="Add Text Note"),
            command=lambda: self.canvas_manager.create_label(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        )
        context_menu.add_separator()
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    def on_drag_release(self, event, item_id, tree_widget):
        if item_id:
            x_root, y_root = event.x_root, event.y_root
            canvas_x0, canvas_y0 = self.canvas.winfo_rootx(), self.canvas.winfo_rooty()
            canvas_x1, canvas_y1 = canvas_x0 + self.canvas.winfo_width(), canvas_y0 + self.canvas.winfo_height()
            if canvas_x0 <= x_root <= canvas_x1 and canvas_y0 <= y_root <= canvas_y1:
                zoom_level = self.navigation_handler.zoom_level
                canvas_x = self.canvas.canvasx(x_root - canvas_x0)
                canvas_y = self.canvas.canvasy(y_root - canvas_y0)
                world_x = canvas_x / zoom_level
                world_y = canvas_y / zoom_level
                module_id = item_id
                module_manager = self.kernel.get_service("module_manager_service")
                if not module_manager: return
                manifest = module_manager.get_manifest(module_id)
                if manifest:
                    self.canvas_manager.node_manager.create_node_on_canvas(name=manifest.get('name', 'Unknown'), x=world_x, y=world_y, module_id=module_id)
            self._reset_all_actions()
    def _reset_all_actions(self):
        """Resets any ongoing user interaction state, like line drawing."""
        if hasattr(self.canvas_manager.coordinator_tab, 'unbind_all'):
            self.canvas_manager.coordinator_tab.unbind_all("<B1-Motion>")
            self.canvas_manager.coordinator_tab.unbind_all("<ButtonRelease-1>")
        if hasattr(self.canvas_manager.coordinator_tab, '_drag_data_toplevel'):
             if self.canvas_manager.coordinator_tab._drag_data_toplevel.get("widget") and self.canvas_manager.coordinator_tab._drag_data_toplevel["widget"].winfo_exists():
                self.canvas_manager.coordinator_tab._drag_data_toplevel["widget"].destroy()
             self.canvas_manager.coordinator_tab._drag_data_toplevel = {}
        self.node_handler._move_data = {"id": None, "x": 0, "y": 0}
        self.connection_handler._cancel_line_drawing()
