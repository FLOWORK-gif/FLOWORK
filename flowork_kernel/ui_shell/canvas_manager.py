#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_manager.py
# JUMLAH BARIS : 230
#######################################################################

import ttkbootstrap as ttk
from tkinter import Menu, messagebox, TclError, Text, simpledialog, scrolledtext
import uuid
import json
import re # [PENAMBAHAN] Kita butuh ini untuk parsing markdown
from flowork_kernel.ui_shell.properties_popup import PropertiesPopup
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_kernel.api_contract import LoopConfig, EnumVarWrapper
from .canvas_components.node_manager import NodeManager
from .canvas_components.connection_manager import ConnectionManager
from .canvas_components.interaction_manager import InteractionManager
from .canvas_components.visual_manager import VisualManager
from .canvas_components.properties_manager import PropertiesManager
class _TextEditorPopup(ttk.Toplevel):
    """A custom Toplevel window for multi-line text input."""
    def __init__(self, parent, kernel, title, prompt, initial_text=""):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.title(title)
        self.result = None
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text=prompt, wraplength=380).pack(fill='x', pady=(0, 10))
        self.text_widget = scrolledtext.ScrolledText(main_frame, wrap="word", height=10, width=50)
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.insert("1.0", initial_text)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        ttk.Button(button_frame, text=self.loc.get('button_save', fallback="Save"), command=self._on_save, bootstyle="success").pack(side="right")
        ttk.Button(button_frame, text=self.loc.get('button_cancel', fallback="Cancel"), command=self.destroy, bootstyle="secondary").pack(side="right", padx=(0, 10))
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    def _on_save(self):
        self.result = self.text_widget.get("1.0", "end-1c")
        self.destroy()
class CanvasManager:
    """
    Manages all specialized managers for the canvas.
    Holds the primary state (nodes, connections, labels) and delegates tasks.
    (FIXED) Now correctly saves all connection properties (target_port_name, type).
    """
    def __init__(self, visual_container, coordinator_tab, canvas_widget, kernel):
        self.parent_widget = visual_container
        self.coordinator_tab = coordinator_tab
        self.canvas = canvas_widget
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.canvas_nodes = {}
        self.canvas_connections = {}
        self.canvas_labels = {}
        self.tooltips = {}
        self.selected_node_id = None
        theme_manager = self.kernel.get_service("theme_manager")
        self.colors = theme_manager.get_colors() if theme_manager else {}
        self.node_manager = NodeManager(self, self.kernel, self.canvas)
        self.connection_manager = ConnectionManager(self, self.kernel, self.canvas)
        self.interaction_manager = InteractionManager(self, self.kernel, self.canvas)
        self.visual_manager = VisualManager(self, self.kernel, self.canvas)
        self.properties_manager = PropertiesManager(self, self.kernel)
        self.interaction_manager.bind_events()
        self.visual_manager.draw_watermark()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def get_workflow_data(self):
        nodes_data = [{"id": n_id, "name": d["name"], "x": d["x"], "y": d["y"], "description": d.get("description", ""), "module_id": d.get("module_id"), "config_values": d.get("config_values", {})} for n_id, d in self.canvas_nodes.items()]
        connections_data = [
            {
                "id": c_id,
                "from": d["from"],
                "to": d["to"],
                "source_port_name": d.get("source_port_name"),
                "target_port_name": d.get("target_port_name"), # ADDED: Save the target port name
                "type": d.get("type", "data") # ADDED: Save the connection type (e.g., 'tool')
            } for c_id, d in self.canvas_connections.items()
        ]
        labels_data = [{"id": l_id, "text": d["text"], "x": d["x"], "y": d["y"], "width": d["widget"].winfo_width(), "height": d["widget"].winfo_height()} for l_id, d in self.canvas_labels.items()]
        return {"nodes": nodes_data, "connections": connections_data, "labels": labels_data}
    def load_workflow_data(self, workflow_data):
        self.clear_canvas(feedback=False)
        for node_data in workflow_data.get("nodes", []):
            self.node_manager.create_node_on_canvas(
                name=node_data.get("name"),
                x=node_data.get("x"),
                y=node_data.get("y"),
                existing_id=node_data.get("id"),
                description=node_data.get("description", ""),
                module_id=node_data.get("module_id"),
                config_values=node_data.get("config_values")
            )
        for label_data in workflow_data.get("labels", []):
            self.create_label(
                x=label_data.get("x"),
                y=label_data.get("y"),
                text=label_data.get("text"),
                existing_id=label_data.get("id"),
                width=label_data.get("width", 200),
                height=label_data.get("height", 80)
            )
        self.coordinator_tab.after(50, lambda: self.connection_manager.recreate_connections(workflow_data.get("connections", [])))
        if not self.canvas_nodes and not self.canvas_labels:
            self.visual_manager.draw_watermark()
    def clear_canvas(self, feedback=True):
        if self.coordinator_tab._execution_state != "IDLE":
            messagebox.showwarning("Aksi Ditolak", "Tidak dapat membersihkan kanvas saat alur kerja sedang berjalan.")
            return
        if feedback: self.kernel.write_to_log(self.loc.get('log_clearing_canvas'), "INFO")
        for node_id in list(self.canvas_nodes.keys()):
            self.node_manager.delete_node(node_id, feedback=False)
        for label_id in list(self.canvas_labels.keys()):
            self.delete_label(label_id, feedback=False)
        self.canvas.delete("all")
        self.visual_manager.draw_grid()
        if self.interaction_manager:
            self.interaction_manager._reset_all_actions()
        self.canvas_nodes.clear()
        self.canvas_connections.clear()
        self.canvas_labels.clear()
        self.selected_node_id = None
        self.visual_manager.draw_watermark()
    def create_label(self, x, y, text=None, existing_id=None, width=200, height=80):
        label_id = existing_id or str(uuid.uuid4())
        initial_text = text or self.loc.get('canvas_new_label_text', fallback="Double click to edit...")
        label_frame = ttk.Frame(self.canvas, width=width, height=height, style="success.TFrame", borderwidth=1, relief="solid")
        label_frame.pack_propagate(False)
        text_widget = ttk.Text(label_frame, wrap="word", relief="flat", borderwidth=0,
                               foreground="black", background="#D4EDDA",
                               font=("Helvetica", 10, "normal"),
                               padx=5, pady=5)
        text_widget.pack(fill="both", expand=True)
        text_widget.tag_configure("bold", font=("Helvetica", 10, "bold"))
        self._apply_markdown_to_text_widget(text_widget, initial_text)
        sizegrip = ttk.Sizegrip(label_frame, style='success.TSizegrip')
        sizegrip.place(relx=1.0, rely=1.0, anchor="se")
        self.canvas.create_window(x, y, window=label_frame, anchor="nw", tags=("label_widget", label_id))
        self.canvas_labels[label_id] = {
            "widget": label_frame,
            "text_widget": text_widget, # Menyimpan referensi ke Text widget
            "text": initial_text,
            "x": x,
            "y": y
        }
        for widget in [label_frame, text_widget]:
            widget.bind("<ButtonPress-1>", lambda e, lid=label_id: self._on_label_press(e, lid))
            widget.bind("<B1-Motion>", lambda e, lid=label_id: self._on_label_drag(e, lid))
            widget.bind("<ButtonRelease-1>", lambda e, lid=label_id: self._on_label_release(e, lid))
            widget.bind("<Double-1>", lambda e, lid=label_id: self._edit_label_text(e, lid))
            widget.bind("<Button-3>", lambda e, lid=label_id: self._show_label_context_menu(e, lid))
        sizegrip.bind("<ButtonPress-1>", lambda e, lid=label_id: self._start_label_resize(e, lid))
        sizegrip.bind("<B1-Motion>", lambda e, lid=label_id: self._on_label_resize_drag(e, lid))
        sizegrip.bind("<ButtonRelease-1>", lambda e, lid=label_id: self._on_label_resize_release(e, lid))
        self.visual_manager.hide_watermark()
        return label_id
    def delete_label(self, label_id, feedback=True):
        if label_id in self.canvas_labels:
            widget = self.canvas_labels[label_id]['widget']
            if widget.winfo_exists():
                widget.destroy()
            del self.canvas_labels[label_id]
            self.canvas.delete(label_id)
            if feedback:
                self.kernel.write_to_log(f"Text note '{label_id[:8]}' deleted.", "INFO")
    def _on_label_press(self, event, label_id):
        self.interaction_manager._drag_data = {"x": event.x, "y": event.y, "id": label_id}
        widget = self.canvas_labels[label_id]['widget']
        widget.lift()
    def _on_label_drag(self, event, label_id):
        if self.interaction_manager._drag_data.get("id") != label_id: return
        new_x = self.canvas.canvasx(event.x_root - self.canvas.winfo_rootx()) - self.interaction_manager._drag_data['x']
        new_y = self.canvas.canvasy(event.y_root - self.canvas.winfo_rooty()) - self.interaction_manager._drag_data['y']
        self.canvas.coords(label_id, new_x, new_y)
    def _on_label_release(self, event, label_id):
        if self.interaction_manager._drag_data.get("id") != label_id: return
        coords = self.canvas.coords(label_id)
        self.canvas_labels[label_id]['x'] = coords[0]
        self.canvas_labels[label_id]['y'] = coords[1]
        self.interaction_manager._drag_data = {}
    def _edit_label_text(self, event, label_id):
        current_text = self.canvas_labels[label_id]['text']
        popup = _TextEditorPopup(
            parent=self.canvas, kernel=self.kernel,
            title=self.loc.get('edit_note_title', fallback="Edit Note"),
            prompt=self.loc.get('edit_note_prompt', fallback="Enter new text for the note:"),
            initial_text=current_text
        )
        new_text = popup.result
        if new_text is not None:
            self.canvas_labels[label_id]['text'] = new_text
            text_widget = self.canvas_labels[label_id]['text_widget']
            self._apply_markdown_to_text_widget(text_widget, new_text)
    def _show_label_context_menu(self, event, label_id):
        context_menu = Menu(self.canvas, tearoff=0)
        context_menu.add_command(label=self.loc.get('context_menu_edit_note', fallback="Edit Note..."), command=lambda: self._edit_label_text(event, label_id))
        context_menu.add_command(label=self.loc.get('context_menu_delete_note', fallback="Delete Note"), command=lambda: self.delete_label(label_id))
        context_menu.tk_popup(event.x_root, event.y_root)
    def _start_label_resize(self, event, label_id):
        widget = self.canvas_labels[label_id]['widget']
        self.interaction_manager._resize_data = {
            'widget': widget,
            'start_x': event.x_root,
            'start_y': event.y_root,
            'start_width': widget.winfo_width(),
            'start_height': widget.winfo_height()
        }
    def _on_label_resize_drag(self, event, label_id):
        resize_data = self.interaction_manager._resize_data
        if not resize_data.get('widget'): return
        dx = event.x_root - resize_data['start_x']
        dy = event.y_root - resize_data['start_y']
        new_width = max(100, resize_data['start_width'] + dx)
        new_height = max(50, resize_data['start_height'] + dy)
        resize_data['widget'].configure(width=new_width, height=new_height)
    def _on_label_resize_release(self, event, label_id):
        self.interaction_manager._resize_data = {}
