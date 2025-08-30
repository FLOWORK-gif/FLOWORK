#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_components\connection_manager.py
# JUMLAH BARIS : 115
#######################################################################

import uuid
class ConnectionManager:
    """
    Manages all aspects of connection lines on the canvas, including creation, deletion, and position updates.
    (MODIFIED) Now supports different connection types and dynamically finds port widget locations.
    (FIXED) Added update_idletasks() to ensure correct coordinates for placed port widgets.
    """
    def __init__(self, canvas_manager, kernel, canvas_widget):
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.canvas = canvas_widget
        self.loc = self.kernel.get_service("localization_manager")
    def _get_port_widget_center(self, node_id, port_name, port_type):
        """(ADDED) Helper function to find the absolute center coordinates of any port widget."""
        node_data = self.canvas_manager.canvas_nodes.get(node_id)
        if not node_data: return None, None
        port_list_key = f"{port_type}_ports"
        port_list = node_data.get(port_list_key, [])
        port_widget = next((p['widget'] for p in port_list if p['name'] == port_name), None)
        if port_widget and port_widget.winfo_exists():
            self.canvas.update_idletasks()
            x = port_widget.winfo_rootx() - self.canvas.winfo_rootx() + (port_widget.winfo_width() / 2)
            y = port_widget.winfo_rooty() - self.canvas.winfo_rooty() + (port_widget.winfo_height() / 2)
            return x, y
        return None, None
    def create_connection(self, start_node_id, end_node_id, existing_id=None, source_port_name=None, connection_type='data', target_port_name=None):
        canvas_nodes = self.canvas_manager.canvas_nodes
        canvas_connections = self.canvas_manager.canvas_connections
        colors = self.canvas_manager.colors
        start_port_type = 'tool' if connection_type == 'tool' else 'output'
        start_x, start_y = self._get_port_widget_center(start_node_id, source_port_name, start_port_type)
        if start_x is None:
            start_widget = canvas_nodes[start_node_id]["widget"]
            start_x = start_widget.winfo_x() + start_widget.winfo_width()
            start_y = start_widget.winfo_y() + start_widget.winfo_height() / 2
        end_port_type = 'tool' if connection_type == 'tool' else 'input'
        end_x, end_y = self._get_port_widget_center(end_node_id, target_port_name, end_port_type)
        if end_x is None:
            end_widget = canvas_nodes[end_node_id]["widget"]
            end_x = end_widget.winfo_x()
            end_y = end_widget.winfo_y() + end_widget.winfo_height() / 2
        offset = abs(end_x - start_x) / 2
        control_x1 = start_x + offset
        control_y1 = start_y
        control_x2 = end_x - offset
        control_y2 = end_y
        line_style = {
            'fill': colors.get('info', '#17a2b8'),
            'width': 2,
            'dash': (6, 4),
            'smooth': True
        } if connection_type == 'tool' else {
            'fill': colors.get('success', '#28a745'),
            'width': 2,
            'smooth': True
        }
        line_id = self.canvas.create_line(start_x, start_y, control_x1, control_y1, control_x2, control_y2, end_x, end_y, tags=("connection_line",), **line_style)
        conn_id = existing_id or str(uuid.uuid4())
        canvas_connections[conn_id] = {
            "line_id": line_id,
            "from": start_node_id,
            "to": end_node_id,
            "source_port_name": source_port_name,
            "target_port_name": target_port_name,
            "type": connection_type
        }
        return conn_id
    def delete_connection(self, conn_id_to_delete, feedback=True):
        canvas_connections = self.canvas_manager.canvas_connections
        if conn_id_to_delete in canvas_connections:
            line_id = canvas_connections[conn_id_to_delete]['line_id']
            if self.canvas.find_withtag(line_id):
                self.canvas.delete(line_id)
            del canvas_connections[conn_id_to_delete]
            if feedback:
                self.kernel.write_to_log(self.loc.get('connection_deleted_success', conn_id=conn_id_to_delete), "INFO")
    def update_connections_for_node(self, node_id):
        canvas_nodes = self.canvas_manager.canvas_nodes
        canvas_connections = self.canvas_manager.canvas_connections
        connections_to_update = []
        for conn_id, conn_data in list(canvas_connections.items()):
            if conn_data["from"] == node_id or conn_data["to"] == node_id:
                connections_to_update.append((conn_id, conn_data))
        for conn_id, conn_data in connections_to_update:
            if conn_data["from"] in canvas_nodes and conn_data["to"] in canvas_nodes:
                self.delete_connection(conn_id, feedback=False)
                self.create_connection(
                    start_node_id=conn_data["from"],
                    end_node_id=conn_data["to"],
                    existing_id=conn_id,
                    source_port_name=conn_data.get("source_port_name"),
                    target_port_name=conn_data.get("target_port_name"),
                    connection_type=conn_data.get("type", 'data')
                )
            else:
                self.delete_connection(conn_id, feedback=False)
    def recreate_connections(self, connections_data):
        canvas_nodes = self.canvas_manager.canvas_nodes
        for conn_data in connections_data:
            if conn_data.get("from") in canvas_nodes and conn_data.get("to") in canvas_nodes:
                self.create_connection(
                    start_node_id=conn_data["from"],
                    end_node_id=conn_data["to"],
                    existing_id=conn_data.get("id"),
                    source_port_name=conn_data.get("source_port_name"),
                    target_port_name=conn_data.get("target_port_name"),
                    connection_type=conn_data.get("type", "data")
                )
