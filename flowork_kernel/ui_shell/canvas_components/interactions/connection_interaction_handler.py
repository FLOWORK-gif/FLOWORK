#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_components\interactions\connection_interaction_handler.py
# JUMLAH BARIS : 160
#######################################################################

from tkinter import Menu, Toplevel, scrolledtext, messagebox
import json
import ttkbootstrap as ttk
class _ConnectionDataPopup(Toplevel):
    """(ADDED) A dedicated popup to display the payload from a connection."""
    def __init__(self, parent, kernel, title, data_to_display):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.title(title)
        self.geometry("600x450")
        self.transient(parent)
        self.grab_set()
        try:
            pretty_data = json.dumps(data_to_display, indent=4, ensure_ascii=False, default=str)
        except Exception:
            pretty_data = str(data_to_display)
        txt_area = scrolledtext.ScrolledText(self, wrap="word", width=70, height=20, font=("Consolas", 10))
        txt_area.pack(expand=True, fill="both", padx=10, pady=10)
        txt_area.insert("1.0", pretty_data)
        txt_area.config(state="disabled")
        self.wait_window(self)
class ConnectionInteractionHandler:
    def __init__(self, canvas_manager):
        self.canvas_manager = canvas_manager
        self.kernel = self.canvas_manager.kernel
        self.canvas = self.canvas_manager.canvas
        self.loc = self.kernel.get_service("localization_manager")
        self._line_data = {"start_node_id": None, "line_id": None, "source_port_name": None, "connection_type": "data"}
        self._highlighted_nodes = []
    def start_line_drawing(self, node_id, port_name=None, port_type='output'):
        if node_id not in self.canvas_manager.canvas_nodes: return
        self.canvas_manager.interaction_manager._reset_all_actions()
        self._line_data["start_node_id"] = node_id
        self._line_data["source_port_name"] = port_name
        self._line_data["connection_type"] = port_type
        port_list_key = f"{port_type}_ports"
        port_list = self.canvas_manager.canvas_nodes[node_id].get(port_list_key, [])
        port_widget = next((p['widget'] for p in port_list if p['name'] == port_name), None)
        if not port_widget:
            start_node_widget = self.canvas_manager.canvas_nodes[node_id]["widget"]
            start_x = start_node_widget.winfo_rootx() - self.canvas.winfo_rootx() + start_node_widget.winfo_width()/2
            start_y = start_node_widget.winfo_rooty() - self.canvas.winfo_rooty() + start_node_widget.winfo_height()/2
        else:
            start_x = port_widget.winfo_rootx() - self.canvas.winfo_rootx() + port_widget.winfo_width()/2
            start_y = port_widget.winfo_rooty() - self.canvas.winfo_rooty() + port_widget.winfo_height()/2
        self._line_data["line_id"] = self.canvas.create_line(start_x, start_y, start_x, start_y, fill=self.canvas_manager.colors['success'], width=2, dash=(4, 4))
        self._highlight_valid_target_nodes(node_id)
    def finish_line_drawing(self, end_node_id, target_port_name=None, target_port_type='input'):
        start_node_id = self._line_data["start_node_id"]
        source_port_name = self._line_data.get("source_port_name")
        connection_type = self._line_data.get("connection_type", "data")
        module_manager = self.kernel.get_service("module_manager_service")
        start_node_manifest = module_manager.get_manifest(self.canvas_manager.canvas_nodes[start_node_id]['module_id'])
        is_source_brain = start_node_manifest.get('subtype') == 'BRAIN_PROVIDER'
        if is_source_brain and target_port_name != 'brain_port':
            self.kernel.write_to_log("Invalid Connection: Brain can only connect to a Brain Port.", "WARN")
            messagebox.showwarning("Invalid Connection", "A 'Brain' node can only be connected to the 'Brain' port of an Agent Host.", parent=self.canvas)
            self._cancel_line_drawing()
            return
        if target_port_type == 'tool':
            connection_type = 'tool'
        if start_node_id and start_node_id != end_node_id and start_node_id in self.canvas_manager.canvas_nodes and end_node_id in self.canvas_manager.canvas_nodes:
            self.canvas_manager.connection_manager.create_connection(
                start_node_id,
                end_node_id,
                source_port_name=source_port_name,
                target_port_name=target_port_name,
                connection_type=connection_type
            )
        self._cancel_line_drawing()
    def on_line_motion(self, event):
        if not self._line_data.get("line_id"): return
        start_node_id = self._line_data["start_node_id"]
        if start_node_id not in self.canvas_manager.canvas_nodes:
            self._cancel_line_drawing()
            return
        port_name = self._line_data.get("source_port_name")
        port_type = self._line_data.get("connection_type", "output")
        port_list_key = f"{port_type}_ports"
        port_list = self.canvas_manager.canvas_nodes[start_node_id].get(port_list_key, [])
        port_widget = next((p['widget'] for p in port_list if p['name'] == port_name), None)
        if not port_widget or not port_widget.winfo_exists():
             start_node_widget = self.canvas_manager.canvas_nodes[start_node_id]["widget"]
             start_x = start_node_widget.winfo_rootx() - self.canvas.winfo_rootx() + start_node_widget.winfo_width()/2
             start_y = start_node_widget.winfo_rooty() - self.canvas.winfo_rooty() + start_node_widget.winfo_height()/2
        else:
            start_x = port_widget.winfo_rootx() - self.canvas.winfo_rootx() + port_widget.winfo_width()/2
            start_y = port_widget.winfo_rooty() - self.canvas.winfo_rooty() + port_widget.winfo_height()/2
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        module_manager = self.kernel.get_service("module_manager_service")
        start_node_manifest = module_manager.get_manifest(self.canvas_manager.canvas_nodes[start_node_id]['module_id'])
        is_source_brain = start_node_manifest.get('subtype') == 'BRAIN_PROVIDER'
        hovered_item = self.canvas.find_closest(end_x, end_y)[0]
        hovered_tags = self.canvas.gettags(hovered_item)
        if is_source_brain and hovered_tags:
            hovered_node_id = next((tag for tag in hovered_tags if tag in self.canvas_manager.canvas_nodes), None)
            if hovered_node_id and self.canvas_manager.canvas_nodes[hovered_node_id].get('module_id') == 'agent_host_module':
                snap_x, snap_y = self.canvas_manager.connection_manager._get_port_widget_center(hovered_node_id, 'brain_port', 'tool')
                if snap_x is not None:
                    end_x, end_y = snap_x, snap_y
        self.canvas.coords(self._line_data["line_id"], start_x, start_y, end_x, end_y)
    def _cancel_line_drawing(self, event=None):
        if self._line_data.get("line_id"):
            if self.canvas.find_withtag(self._line_data["line_id"]):
                self.canvas.delete(self._line_data["line_id"])
        self._line_data = {"start_node_id": None, "line_id": None, "source_port_name": None, "connection_type": "data"}
        self._clear_node_highlights()
        return "break"
    def _highlight_valid_target_nodes(self, start_node_id):
        self._clear_node_highlights()
        for node_id, node_data in self.canvas_manager.canvas_nodes.items():
            if node_id != start_node_id:
                widget = node_data['widget']
                if widget.winfo_exists():
                    widget.config(style="Droppable.Module.TFrame")
                    self._highlighted_nodes.append(widget)
    def _clear_node_highlights(self):
        for widget in self._highlighted_nodes:
            if widget.winfo_exists():
                is_selected = self.canvas_manager.selected_node_id == widget.node_id
                widget.config(style="Selected.Module.TFrame" if is_selected else "Module.TFrame")
        self._highlighted_nodes = []
    def show_line_context_menu(self, event):
        current_items = self.canvas.find_withtag("current")
        if not current_items: return
        conn_id = next((cid for cid, cdata in self.canvas_manager.canvas_connections.items() if cdata['line_id'] == current_items[0]), None)
        if conn_id:
            context_menu = Menu(self.canvas, tearoff=0)
            context_menu.add_command(label="Lihat Data Terakhir...", command=lambda: self._show_connection_data_popup(conn_id))
            context_menu.add_separator()
            context_menu.add_command(label=self.loc.get('context_menu_delete_connection'), command=lambda: self.canvas_manager.connection_manager.delete_connection(conn_id))
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    def _show_connection_data_popup(self, conn_id):
        history_data = self.canvas_manager.coordinator_tab.canvas_area_instance.execution_history
        if not history_data or not history_data.get('steps'):
            messagebox.showinfo("Info", "No execution history is available for this run.", parent=self.canvas)
            return
        data_for_this_conn = "No data recorded for this specific connection in the last run."
        for step in reversed(history_data['steps']):
            if step.get('connection_id') == conn_id:
                data_for_this_conn = step.get('payload', {})
                break
        _ConnectionDataPopup(
            parent=self.canvas,
            kernel=self.kernel,
            title=f"Data Preview for Connection",
            data_to_display=data_for_this_conn
        )
