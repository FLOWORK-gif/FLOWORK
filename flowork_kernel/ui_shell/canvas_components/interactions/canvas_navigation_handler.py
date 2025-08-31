#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_components\interactions\canvas_navigation_handler.py
# JUMLAH BARIS : 57
#######################################################################

class CanvasNavigationHandler:
    def __init__(self, canvas_manager):
        self.canvas_manager = canvas_manager
        self.canvas = self.canvas_manager.canvas
        self.zoom_level = 1.0
        self.zoom_step = 0.1
    def on_pan_start(self, event):
        """Marks the starting point for panning the canvas."""
        self.canvas.scan_mark(event.x, event.y)
        self.canvas.config(cursor="fleur")
    def on_pan_move(self, event):
        """Moves the canvas based on mouse movement."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
    def on_pan_end(self, event):
        """Resets the cursor when panning ends."""
        self.canvas.config(cursor="")
        self.canvas.delete("grid_dot")
        self.canvas_manager.visual_manager.draw_grid()
    def apply_zoom(self):
        """Applies the current zoom level to all canvas elements."""
        for node_id, node_data in self.canvas_manager.canvas_nodes.items():
            original_x, original_y = node_data['x'], node_data['y']
            scaled_x = original_x * self.zoom_level
            scaled_y = original_y * self.zoom_level
            if node_data['widget'].winfo_exists():
                node_data['widget'].place(x=scaled_x, y=scaled_y)
        for node_id in self.canvas_manager.canvas_nodes.keys():
            self.canvas_manager.connection_manager.update_connections_for_node(node_id)
    def zoom_in(self, event=None):
        """Increases the zoom level."""
        self.zoom_level += self.zoom_step
        self.apply_zoom()
        self.canvas_manager.parent_widget.update_zoom_label()
    def zoom_out(self, event=None):
        """Decreases the zoom level."""
        self.zoom_level = max(0.2, self.zoom_level - self.zoom_step)
        self.apply_zoom()
        self.canvas_manager.parent_widget.update_zoom_label()
    def reset_zoom(self, event=None):
        """Resets the zoom level to 100%."""
        self.zoom_level = 1.0
        self.apply_zoom()
        self.canvas_manager.parent_widget.update_zoom_label()
    def handle_zoom_event(self, event):
        """Handles zoom events from the mouse wheel."""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        return "break"
