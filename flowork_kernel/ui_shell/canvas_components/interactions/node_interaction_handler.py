#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_components\interactions\node_interaction_handler.py
# JUMLAH BARIS : 123
#######################################################################

from tkinter import Menu
from flowork_kernel.api_client import ApiClient
class NodeInteractionHandler:
    """
    (REFACTORED) Handles all node-specific interactions like pressing, dragging, releasing, and context menus.
    This version is robust for both widget-based (rectangular) and canvas-item-based (circular) nodes.
    """
    def __init__(self, canvas_manager):
        self.canvas_manager = canvas_manager
        self.kernel = self.canvas_manager.kernel
        self.canvas = self.canvas_manager.canvas
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self._move_data = {"id": None, "x": 0, "y": 0}
    def on_node_press(self, event):
        item_ids = self.canvas.find_withtag("current")
        node_id = None
        if item_ids:
            tags = self.canvas.gettags(item_ids[0])
            node_id = next((tag for tag in tags if tag in self.canvas_manager.canvas_nodes), None)
        if not node_id:
            widget = event.widget
            while widget and not hasattr(widget, 'node_id'):
                widget = widget.master
            if not widget: return
            node_id = widget.node_id
        connection_handler = self.canvas_manager.interaction_manager.connection_handler
        is_drawing_line = connection_handler._line_data.get("start_node_id") is not None
        if is_drawing_line:
            self.kernel.write_to_log("Logic Builder: Left-click detected on target node, finishing connection.", "DEBUG")
            target_port_name = getattr(event.widget, 'port_name', None)
            target_port_type = getattr(event.widget, 'port_type', 'input')
            connection_handler.finish_line_drawing(node_id, target_port_name, target_port_type)
            self._move_data = {"id": None, "x": 0, "y": 0}
            return
        self.canvas_manager.node_manager.select_node(node_id)
        if hasattr(event.widget, 'port_name'): return
        self._move_data["id"] = node_id
        self._move_data["x"] = self.canvas.canvasx(event.x)
        self._move_data["y"] = self.canvas.canvasy(event.y)
        return "break"
    def on_node_motion(self, event):
        if self._move_data.get("id"):
            node_id = self._move_data["id"]
            if node_id not in self.canvas_manager.canvas_nodes: return
            new_x = self.canvas.canvasx(event.x)
            new_y = self.canvas.canvasy(event.y)
            delta_x = new_x - self._move_data["x"]
            delta_y = new_y - self._move_data["y"]
            self.canvas_manager.node_manager.move_node_by_delta(node_id, delta_x, delta_y)
            self._move_data["x"] = new_x
            self._move_data["y"] = new_y
    def on_node_release(self, event):
        if self._move_data.get("id"):
            node_id = self._move_data["id"]
            if node_id in self.canvas_manager.canvas_nodes:
                zoom_level = self.canvas_manager.interaction_manager.navigation_handler.zoom_level
                bbox = self.canvas.bbox(node_id)
                if bbox:
                    scaled_x = bbox[0]
                    scaled_y = bbox[1]
                    self.canvas_manager.canvas_nodes[node_id]["x"] = scaled_x / zoom_level
                    self.canvas_manager.canvas_nodes[node_id]["y"] = scaled_y / zoom_level
            self._move_data = {"id": None, "x": 0, "y": 0}
    def on_delete_key_press(self, event=None):
        if self.canvas_manager.selected_node_id:
            self.canvas_manager.node_manager.delete_node(self.canvas_manager.selected_node_id)
            return "break"
    def show_node_context_menu(self, event):
        closest_items = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        if not closest_items: return
        item_id = closest_items[0]
        tags = self.canvas.gettags(item_id)
        node_id = next((tag for tag in tags if tag in self.canvas_manager.canvas_nodes), None)
        if not node_id:
            widget = event.widget
            while widget and not hasattr(widget, 'node_id'):
                widget = widget.master
            if not widget: return
            node_id = widget.node_id
        self.canvas_manager.node_manager.select_node(node_id)
        context_menu = Menu(self.canvas, tearoff=0)
        context_menu.add_command(label=self.loc.get('context_menu_properties', fallback="Properties"), command=lambda: self.canvas_manager.properties_manager.open_properties_popup(node_id))
        context_menu.add_separator()
        line_data = self.canvas_manager.interaction_manager.connection_handler._line_data
        node_data = self.canvas_manager.canvas_nodes[node_id]
        start_conn_state = "normal" if not line_data["start_node_id"] else "disabled"
        finish_conn_state = "disabled" if not line_data["start_node_id"] else "normal"
        module_manager = self.kernel.get_service("module_manager_service")
        manifest = module_manager.get_manifest(node_data.get("module_id")) if module_manager else {}
        start_connection_menu = Menu(context_menu, tearoff=0)
        has_any_output = False
        if node_data.get("output_ports"):
            has_any_output = True
            for port_data in node_data["output_ports"]:
                port_name = port_data.get("name")
                port_info = next((p for p in manifest.get('output_ports', []) if p['name'] == port_name), {'display_name': port_name.replace("_", " ").title()})
                start_connection_menu.add_command(label=port_info.get("display_name"), command=lambda n=node_id, p=port_name: self.canvas_manager.interaction_manager.connection_handler.start_line_drawing(n, port_name=p, port_type='output'))
        if node_data.get("tool_ports"):
            has_any_output = True
            if node_data.get("output_ports"):
                start_connection_menu.add_separator()
            for port_data in node_data["tool_ports"]:
                port_name = port_data.get("name")
                port_info = next((p for p in manifest.get('tool_ports', []) if p['name'] == port_name), {'display_name': port_name.replace("_", " ").title()})
                start_connection_menu.add_command(label=f"Connect to {port_info.get('display_name')}", command=lambda n=node_id, p=port_name: self.canvas_manager.interaction_manager.connection_handler.start_line_drawing(n, port_name=p, port_type='tool'))
        if has_any_output:
            context_menu.add_cascade(label=self.loc.get('context_menu_start_connection', fallback="Start Connection"), menu=start_connection_menu, state=start_conn_state)
        context_menu.add_command(label=self.loc.get('context_menu_finish_connection', fallback="Finish Connection Here"), command=lambda: self.canvas_manager.interaction_manager.connection_handler.finish_line_drawing(node_id), state=finish_conn_state)
        context_menu.add_separator()
        context_menu.add_command(label=self.loc.get('context_menu_duplicate_node', fallback="Duplicate Node"), command=lambda: self.canvas_manager.node_manager.duplicate_node(node_id))
        context_menu.add_command(label=self.loc.get('context_menu_delete_node'), command=lambda: self.canvas_manager.node_manager.delete_node(node_id))
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
