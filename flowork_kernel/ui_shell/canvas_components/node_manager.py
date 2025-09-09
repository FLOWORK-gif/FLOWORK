#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_components\node_manager.py
# JUMLAH BARIS : 594
#######################################################################

import ttkbootstrap as ttk
from tkinter import TclError, messagebox, scrolledtext
import uuid
import json
from ..custom_widgets.tooltip import ToolTip
import threading
import time
import os
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
class NodeManager:
    """
    Manages the lifecycle of nodes on the canvas.
    (MODIFIED V15) Now handles cases where a manifest is not found for a module ID in a preset, preventing crashes.
    """
    def __init__(self, canvas_manager, kernel, canvas_widget):
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.canvas = canvas_widget
        self.loc = self.kernel.get_service("localization_manager")
        self.logger = self.kernel.write_to_log
        self.hovered_node_id = None
        self.icon_cache = {}
        self.animation_jobs = {}
    def _get_component_data(self, component_id):
        """
        Searches for component data (manifest, instance, etc.) across all relevant managers.
        Returns a tuple of (manager_service, component_data) or (None, None).
        """
        module_manager = self.kernel.get_service("module_manager_service")
        if module_manager and component_id in module_manager.loaded_modules:
            return module_manager, module_manager.loaded_modules[component_id]
        plugin_manager = self.kernel.get_service("plugin_manager_service")
        if plugin_manager and component_id in plugin_manager.loaded_plugins:
            return plugin_manager, plugin_manager.loaded_plugins[component_id]
        return None, None
    def move_node_by_delta(self, node_id, dx, dy):
        if self.canvas.find_withtag(node_id):
            self.canvas.move(node_id, dx, dy)
            self.canvas.update_idletasks()
            self.canvas_manager.connection_manager.update_connections_for_node(node_id)
    def _apply_style_to_node_widgets(self, node_id, frame_style_name):
        if node_id not in self.canvas_manager.canvas_nodes: return
        node_data = self.canvas_manager.canvas_nodes[node_id]
        if node_data.get("shape") == 'agent_host':
             border_frame = node_data.get('border_frame')
             if not border_frame or not border_frame.winfo_exists(): return
             border_frame.config(style='AgentBorder.Selected.TFrame' if "Selected" in frame_style_name or "Hover" in frame_style_name else 'AgentBorder.Normal.TFrame')
             return
        if node_data.get('shape') in ['circle', 'icon_box', 'agent_brain']:
            shape_id = node_data.get('oval_id')
            if shape_id and self.canvas.find_withtag(shape_id):
                is_active = "Selected" in frame_style_name or "Hover" in frame_style_name
                outline_color = self.canvas_manager.colors.get('success', 'green') if is_active else self.canvas_manager.colors.get('border', 'grey')
                outline_width = 3 if is_active else 1
                if node_data.get('shape') == 'agent_brain':
                    outline_color = self.canvas_manager.colors.get('info', '#17a2b8') if is_active else "#4A00E0"
                self.canvas.itemconfig(shape_id, outline=outline_color, width=outline_width)
            return
        widget = node_data.get('widget')
        if not widget or not widget.winfo_exists(): return
        label_style_name = frame_style_name.replace('.Module.TFrame', '.TLabel')
        def _recursive_style(current_widget):
            if not current_widget.winfo_exists(): return
            if isinstance(current_widget, (ttk.Frame, ttk.LabelFrame)):
                current_widget.config(style=frame_style_name)
            elif isinstance(current_widget, ttk.Label):
                if "Port" not in current_widget.cget('style') and not hasattr(current_widget, '_is_icon_label'):
                    current_widget.config(style=label_style_name)
            for child in current_widget.winfo_children():
                _recursive_style(child)
        _recursive_style(widget)
    def _load_and_display_icon(self, parent_widget, module_id, module_manager):
        if not PIL_AVAILABLE: return None
        manager, component_data = self._get_component_data(module_id)
        if not component_data: return None
        manifest = component_data.get("manifest", {})
        icon_filename = manifest.get("icon_file")
        if not icon_filename: return None
        icon_path = os.path.join(component_data.get("path"), icon_filename)
        if not os.path.exists(icon_path): return None
        icon_label = ttk.Label(parent_widget, style="Glass.TLabel")
        icon_label._is_icon_label = True # (COMMENT) Custom flag to prevent style changes.
        if icon_filename.lower().endswith('.gif'):
            self._animate_gif(icon_label, icon_path, module_id)
        else: # (COMMENT) Assume PNG or other static image
            if icon_path in self.icon_cache:
                photo_image = self.icon_cache[icon_path]
            else:
                try:
                    image = Image.open(icon_path).resize((20, 20), Image.Resampling.LANCZOS)
                    photo_image = ImageTk.PhotoImage(image)
                    self.icon_cache[icon_path] = photo_image
                except Exception as e:
                    self.logger(f"Could not load icon for {module_id}: {e}", "WARN")
                    return None
            icon_label.config(image=photo_image)
            icon_label.image = photo_image # (COMMENT) Keep a reference!
        icon_label.pack(side="left", padx=(0, 5))
        return icon_label
    def _animate_gif(self, label_widget, path, node_id, size=(20,20)):
        if node_id in self.animation_jobs:
            self._stop_gif_animation(node_id)
        try:
            gif = Image.open(path)
            frames = []
            for i in range(gif.n_frames):
                gif.seek(i)
                frame_image = gif.copy().resize(size, Image.Resampling.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame_image))
            if not frames: return
            delay = gif.info.get('duration', 100)
            job_data = {
                'label': label_widget,
                'frames': frames,
                'delay': delay,
                'idx': 0,
                'job_id': None
            }
            self.animation_jobs[node_id] = job_data
            def _update_frame():
                if node_id not in self.animation_jobs or not job_data['label'].winfo_exists():
                    return
                frame = job_data['frames'][job_data['idx']]
                job_data['label'].config(image=frame)
                job_data['idx'] = (job_data['idx'] + 1) % len(job_data['frames'])
                job_data['job_id'] = self.canvas.after(job_data['delay'], _update_frame)
            _update_frame()
        except Exception as e:
            self.logger(f"Could not animate GIF for {node_id}: {e}", "ERROR")
    def _stop_gif_animation(self, node_id):
        if node_id in self.animation_jobs:
            job_data = self.animation_jobs.pop(node_id)
            if job_data.get('job_id'):
                try:
                    self.canvas.after_cancel(job_data['job_id'])
                except TclError:
                    pass
            self.logger(f"Stopped GIF animation for node {node_id}.", "DEBUG")
    def create_node_on_canvas(self, name, x, y, existing_id=None, description="", module_id=None, config_values=None):
        if module_id:
            manager, component_data = self._get_component_data(module_id)
            if component_data:
                required_tier = component_data.get('tier', 'free')
                if not self.kernel.is_tier_sufficient(required_tier):
                    messagebox.showwarning(self.loc.get('license_popup_title'), self.loc.get('license_popup_message', module_name=name), parent=self.canvas.winfo_toplevel())
                    tab_manager = self.kernel.get_service("tab_manager_service")
                    if tab_manager: tab_manager.open_managed_tab("pricing_page")
                    return
        node_id = existing_id
        if module_id == 'prompt_receiver_module' and not existing_id:
            if "receiver-node-1" in self.canvas_manager.canvas_nodes:
                messagebox.showwarning("Node Already Exists", "You can only have one 'Prompt Receiver' node on the canvas. Its ID is always 'receiver-node-1'.")
                return
            node_id = "receiver-node-1"
        elif not node_id:
            node_id = str(uuid.uuid4())
        canvas_nodes = self.canvas_manager.canvas_nodes
        tooltips = self.canvas_manager.tooltips
        manager, component_data = self._get_component_data(module_id)
        manifest = component_data.get('manifest', {}) if component_data else {}
        if manifest is None or not manifest:
            self.logger(f"Warning: Manifest for component ID '{module_id}' not found. It may have been uninstalled or is not a recognized type. Using a default empty manifest.", "WARN")
            manifest = {}
        display_props = manifest.get('display_properties', {})
        node_shape = display_props.get('shape', 'rectangle')
        zoom_level = self.canvas_manager.interaction_manager.navigation_handler.zoom_level
        scaled_x = x * zoom_level
        scaled_y = y * zoom_level
        main_label, widget_to_register = None, None
        output_ports_widgets, input_ports_widgets, tool_ports_widgets = [], [], []
        ports_frame, info_frame, border_frame, status_text, oval_id = None, None, None, None, None
        if node_shape == 'agent_brain':
            node_width = 80
            node_height = 80
            oval_id = self.canvas.create_rectangle(scaled_x, scaled_y, scaled_x + node_width, scaled_y + node_height, fill="#2E0854", outline="#4A00E0", width=1, tags=(node_id, "node_shape"))
            widget_to_register = ttk.Frame(self.canvas, width=node_width-8, height=node_height-8, style='TFrame', relief="solid", borderwidth=1)
            self.canvas.create_window(scaled_x + node_width/2, scaled_y + node_height/2, window=widget_to_register, tags=(node_id, "node_widget_container"))
            if PIL_AVAILABLE and display_props.get("icon_file"):
                icon_filename = display_props.get("icon_file")
                _manager, comp_data = self._get_component_data(module_id)
                icon_path = os.path.join(comp_data.get("path"), icon_filename) if comp_data else None
                icon_label = ttk.Label(widget_to_register, style="TLabel")
                icon_label.place(relx=0.5, rely=0.5, anchor="center")
                if icon_path and os.path.exists(icon_path):
                    if icon_filename.lower().endswith('.gif'):
                        self._animate_gif(icon_label, icon_path, node_id, size=(48, 48))
                    else:
                        image = Image.open(icon_path).resize((48, 48), Image.Resampling.LANCZOS)
                        photo_image = ImageTk.PhotoImage(image)
                        self.icon_cache[icon_path] = photo_image
                        icon_label.config(image=photo_image)
                        icon_label.image = photo_image
            connection_handler = self.canvas_manager.interaction_manager.connection_handler
            for port_info in manifest.get('output_ports', []):
                port_name = port_info.get("name")
                port_type = port_info.get("type", "output")
                port_x, port_y = scaled_x + node_width/2, scaled_y
                connector = ttk.Frame(self.canvas, width=24, height=12, style="info.TFrame", relief="raised", borderwidth=1)
                self.canvas.create_window(port_x, port_y, window=connector, tags=(node_id, "node_port"), anchor="s")
                connector.node_id = node_id
                connector.port_name = port_name
                output_ports_widgets.append({"name": port_name, "widget": connector})
                connector.bind("<ButtonPress-1>", lambda e, n=node_id, p=port_name, pt=port_type: connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
                connector.bind("<Enter>", lambda e, w=connector: w.config(style="success.TFrame"))
                connector.bind("<Leave>", lambda e, w=connector: w.config(style="info.TFrame"))
                ToolTip(connector).update_text(port_info.get("tooltip", port_name))
            self.canvas_manager.visual_manager.start_brain_pulse(node_id)
        elif node_shape == 'circle':
            node_width = 120
            node_height = 120
            oval_id = self.canvas.create_oval(scaled_x, scaled_y, scaled_x + node_width, scaled_y + node_height, fill=self.canvas_manager.colors.get('dark', '#343a40'), outline=self.canvas_manager.colors.get('border', 'grey'), width=1, tags=(node_id, "node_shape"))
            widget_to_register = ttk.Frame(self.canvas, width=node_width-10, height=node_height-10)
            widget_to_register.config(style='TFrame')
            self.canvas.create_window(scaled_x + node_width/2, scaled_y + node_height/2, window=widget_to_register, tags=(node_id, "node_widget_container"))
            if PIL_AVAILABLE and display_props.get("icon_file"):
                icon_filename = display_props.get("icon_file")
                _manager, comp_data = self._get_component_data(module_id)
                icon_path = os.path.join(comp_data.get("path"), icon_filename) if comp_data else None
                icon_label = ttk.Label(widget_to_register, style="TLabel")
                icon_label.place(relx=0.5, rely=0.4, anchor="center")
                if icon_path and os.path.exists(icon_path):
                    if icon_filename.lower().endswith('.gif'):
                        self._animate_gif(icon_label, icon_path, node_id, size=(48, 48))
                    else:
                        image = Image.open(icon_path).resize((48, 48), Image.Resampling.LANCZOS)
                        photo_image = ImageTk.PhotoImage(image)
                        self.icon_cache[icon_path] = photo_image
                        icon_label.config(image=photo_image)
                        icon_label.image = photo_image
            main_label = ttk.Label(widget_to_register, text=name, wraplength=node_width - 20, justify='center')
            main_label.place(relx=0.5, rely=0.8, anchor="center")
            connection_handler = self.canvas_manager.interaction_manager.connection_handler
            for port_info in manifest.get('output_ports', []):
                port_name = port_info.get("name")
                port_position = port_info.get("port_position", "top")
                port_type = port_info.get("type", "output")
                rely_val, anchor_val = (0.0, "n") if port_position == "top" else (1.0, "s")
                port_x, port_y = scaled_x + node_width/2, scaled_y if port_position == "top" else scaled_y + node_height
                connector = ttk.Frame(self.canvas, width=20, height=10, style="success.TFrame", relief="solid", borderwidth=1)
                self.canvas.create_window(port_x, port_y, window=connector, tags=(node_id, "node_port"), anchor=anchor_val)
                connector.node_id = node_id
                connector.port_name = port_name
                output_ports_widgets.append({"name": port_name, "widget": connector})
                connector.bind("<ButtonPress-1>", lambda e, n=node_id, p=port_name, pt=port_type: connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
                connector.bind("<Enter>", lambda e, w=connector: w.config(style="info.TFrame"))
                connector.bind("<Leave>", lambda e, w=connector: w.config(style="success.TFrame"))
                ToolTip(connector).update_text(port_info.get("tooltip", port_name))
        elif node_shape == 'icon_box':
            node_width = 80
            node_height = 80
            oval_id = self.canvas.create_rectangle(scaled_x, scaled_y, scaled_x + node_width, scaled_y + node_height, fill=self.canvas_manager.colors.get('bg', '#222'), outline=self.canvas_manager.colors.get('border', 'grey'), width=1, tags=(node_id, "node_shape"))
            widget_to_register = ttk.Frame(self.canvas, width=node_width-10, height=node_height-10)
            widget_to_register.config(style='TFrame')
            self.canvas.create_window(scaled_x + node_width/2, scaled_y + node_height/2, window=widget_to_register, tags=(node_id, "node_widget_container"))
            if PIL_AVAILABLE and display_props.get("icon_file"):
                icon_filename = display_props.get("icon_file")
                _manager, comp_data = self._get_component_data(module_id)
                icon_path = os.path.join(comp_data.get("path"), icon_filename) if comp_data else None
                icon_label = ttk.Label(widget_to_register, style="TLabel")
                icon_label.place(relx=0.5, rely=0.5, anchor="center")
                if icon_path and os.path.exists(icon_path):
                    if icon_filename.lower().endswith('.gif'):
                        self._animate_gif(icon_label, icon_path, node_id, size=(48, 48))
                    else:
                        image = Image.open(icon_path).resize((48, 48), Image.Resampling.LANCZOS)
                        photo_image = ImageTk.PhotoImage(image)
                        self.icon_cache[icon_path] = photo_image
                        icon_label.config(image=photo_image)
                        icon_label.image = photo_image
            connection_handler = self.canvas_manager.interaction_manager.connection_handler
            for port_info in manifest.get('output_ports', []):
                port_name = port_info.get("name")
                port_type = port_info.get("type", "output")
                port_x, port_y = scaled_x + node_width/2, scaled_y
                connector = ttk.Frame(self.canvas, width=20, height=10, style="success.TFrame", relief="solid", borderwidth=1)
                self.canvas.create_window(port_x, port_y, window=connector, tags=(node_id, "node_port"), anchor="s")
                connector.node_id = node_id
                connector.port_name = port_name
                output_ports_widgets.append({"name": port_name, "widget": connector})
                connector.bind("<ButtonPress-1>", lambda e, n=node_id, p=port_name, pt=port_type: connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
                connector.bind("<Enter>", lambda e, w=connector: w.config(style="info.TFrame"))
                connector.bind("<Leave>", lambda e, w=connector: w.config(style="success.TFrame"))
                ToolTip(connector).update_text(port_info.get("tooltip", port_name))
        elif node_shape == 'agent_host':
            style = ttk.Style()
            style.configure('AgentBorder.Normal.TFrame', background="#6A2E2E")
            style.configure('AgentBorder.Selected.TFrame', background="yellow")
            style.configure('AgentHeader.TFrame', background="#4A00E0")
            style.configure('AgentHeader.TLabel', background="#4A00E0", foreground="yellow")
            style.configure('AgentBody.TFrame', background="#6A2E2E")
            style.configure('AgentBody.TLabel', background="#6A2E2E")
            style.configure('AgentFooter.TFrame', background="#6A2E2E")
            widget_to_register = ttk.Frame(self.canvas, width=320, height=132)
            widget_to_register.pack_propagate(False)
            border_frame = ttk.Frame(widget_to_register, width=302, height=132, style='AgentBorder.Normal.TFrame')
            border_frame.place(relx=0.5, rely=0.5, anchor='center')
            node_frame = ttk.Frame(border_frame, width=300, height=130)
            node_frame.pack(padx=1, pady=1)
            node_frame.pack_propagate(False)
            header = ttk.Frame(node_frame, height=30, style='AgentHeader.TFrame')
            header.pack(side="top", fill="x")
            main_label = ttk.Label(header, text="Agent Host", font=("Arial", 12, "bold"), style='AgentHeader.TLabel')
            main_label.pack(pady=5)
            status_text = scrolledtext.ScrolledText(node_frame, height=2, wrap="word", relief="sunken", borderwidth=1, background="#4d2424", foreground="#E0E0E0", font=("Consolas", 8), state="disabled", name=f"agent_status_text_{node_id}")
            status_text.pack(fill='x', expand=True, padx=30, pady=5)
            icon_size = (24, 24)
            tool_ports_config = {'prompt_port': 'icon_prompt.png', 'brain_port': 'icon_brain.png', 'tools_port': 'icon_tools.png'}
            icon_holder_frame = ttk.Frame(node_frame, style='AgentFooter.TFrame')
            icon_holder_frame.pack(side="bottom", fill="x", pady=5)
            for port_name, icon_file in tool_ports_config.items():
                port_container = ttk.Frame(icon_holder_frame, style='AgentFooter.TFrame')
                port_container.pack(side='left', expand=True, fill='x')
                component_base_path = component_data.get("path")
                full_path = os.path.join(component_base_path, icon_file)
                if os.path.exists(full_path):
                    img = Image.open(full_path).resize(icon_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    icon_label = ttk.Label(port_container, image=photo, style='AgentBody.TLabel', cursor="tcross")
                    icon_label.image = photo
                    icon_label.pack()
                    ToolTip(icon_label).update_text(f"Connect {port_name.replace('_port','').capitalize()} here")
                    icon_label.node_id = node_id
                    icon_label.port_name = port_name
                    icon_label.port_type = 'tool'
                    tool_ports_widgets.append({"name": port_name, "widget": icon_label})
            input_ports_widgets, output_ports_widgets = [], []
            input_port_connector = ttk.Frame(widget_to_register, width=10, height=20, style="success.TFrame")
            input_port_connector.place(x=0, rely=0.5, anchor='w')
            input_port_connector.node_id = node_id; input_port_connector.port_name = "payload_input"; input_port_connector.port_type = 'input'
            input_ports_widgets.append({"name": "payload_input", "widget": input_port_connector})
            output_port_success_connector = ttk.Frame(widget_to_register, width=10, height=20, style="success.TFrame")
            output_port_success_connector.place(relx=1, rely=0.4, anchor='e')
            output_port_success_connector.node_id = node_id; output_port_success_connector.port_name = "success"; output_port_success_connector.port_type = 'output'
            output_ports_widgets.append({"name": "success", "widget": output_port_success_connector})
            output_port_error_connector = ttk.Frame(widget_to_register, width=10, height=20, style="danger.TFrame")
            output_port_error_connector.place(relx=1, rely=0.6, anchor='e')
            output_port_error_connector.node_id = node_id; output_port_error_connector.port_name = "error"; output_port_error_connector.port_type = 'output'
            output_ports_widgets.append({"name": "error", "widget": output_port_error_connector})
            ports_frame, info_frame, status_label = ttk.Frame(node_frame), ttk.Frame(node_frame), ttk.Label(node_frame)
        else:
            node_frame = ttk.Frame(self.canvas, style='Glass.Module.TFrame', padding=(0,0,0,5))
            widget_to_register = node_frame
            content_frame = ttk.Frame(node_frame, style='Glass.Module.TFrame')
            content_frame.pack(side="left", fill="both", expand=True, padx=5)
            header_frame = ttk.Frame(content_frame, style='Glass.Module.TFrame')
            header_frame.pack(fill='x', expand=True, padx=5, pady=(5,0))
            self._load_and_display_icon(header_frame, module_id, None) # Pass None for the manager, as the function now handles it
            main_label = ttk.Label(header_frame, text=name, style="Glass.TLabel", wraplength=180)
            main_label.pack(side="left", fill='x', expand=True)
            info_frame = ttk.Frame(content_frame, style='Glass.Module.TFrame')
            info_frame.pack(fill='x', padx=10, pady=(2,0))
            status_label = ttk.Label(content_frame, text="", name=f"status_{node_id}", font=("Helvetica", 7), anchor='center', style="Glass.TLabel", wraplength=180)
            status_label.pack(fill='x', padx=10, pady=(0,5))
            ports_frame = ttk.Frame(node_frame, style='Glass.Module.TFrame')
            ports_frame.pack(side="right", fill="y", padx=(0, 5))
        if node_shape not in ['circle', 'icon_box', 'agent_brain']:
            self.canvas.create_window(scaled_x, scaled_y, window=widget_to_register, anchor="nw", tags=(node_id, "node_widget_container"))
        widget_to_register.node_id = node_id
        canvas_nodes[node_id] = {
            "widget": widget_to_register, "main_label": main_label, "name": name, "x": x, "y": y,
            "description": description, "module_id": module_id, "config_values": config_values or {},
            "output_ports": output_ports_widgets, "input_ports": input_ports_widgets, "tool_ports": tool_ports_widgets,
            "ports_widget_frame": ports_frame, "info_widget_frame": info_frame, "border_frame": border_frame,
            "status_display_widget": status_text, "shape": node_shape, "oval_id": oval_id
        }
        if node_shape != 'agent_host' and node_shape not in ['circle', 'icon_box', 'agent_brain']:
             self.update_node_ports(node_id)
        self.update_node_visual_info(node_id)
        tooltips[node_id] = ToolTip(widget_to_register)
        tooltips[node_id].update_text(description)
        interaction_manager = self.canvas_manager.interaction_manager
        node_interaction_handler = interaction_manager.node_handler
        if node_shape in ['circle', 'icon_box', 'agent_brain']:
            def _bind_recursive_special(widget, event, command):
                 if widget and widget.winfo_exists():
                    widget.bind(event, command)
                    for child in widget.winfo_children():
                        _bind_recursive_special(child, event, command)
            _bind_recursive_special(widget_to_register, "<ButtonPress-1>", node_interaction_handler.on_node_press)
            _bind_recursive_special(widget_to_register, "<B1-Motion>", node_interaction_handler.on_node_motion)
            _bind_recursive_special(widget_to_register, "<ButtonRelease-1>", node_interaction_handler.on_node_release)
            _bind_recursive_special(widget_to_register, "<ButtonPress-3>", node_interaction_handler.show_node_context_menu)
            self.canvas.tag_bind(oval_id, "<ButtonPress-1>", node_interaction_handler.on_node_press)
            self.canvas.tag_bind(oval_id, "<B1-Motion>", node_interaction_handler.on_node_motion)
            self.canvas.tag_bind(oval_id, "<ButtonRelease-1>", node_interaction_handler.on_node_release)
            self.canvas.tag_bind(oval_id, "<ButtonPress-3>", node_interaction_handler.show_node_context_menu)
        else:
            def _bind_recursive(widget, event, command):
                if widget.winfo_exists():
                    widget.bind(event, command)
                    for child in widget.winfo_children():
                        _bind_recursive(child, event, command)
            _bind_recursive(widget_to_register, "<ButtonPress-1>", node_interaction_handler.on_node_press)
            _bind_recursive(widget_to_register, "<B1-Motion>", node_interaction_handler.on_node_motion)
            _bind_recursive(widget_to_register, "<ButtonRelease-1>", node_interaction_handler.on_node_release)
            _bind_recursive(widget_to_register, "<ButtonPress-3>", node_interaction_handler.show_node_context_menu)
        if node_shape == 'agent_host':
            connection_handler = self.canvas_manager.interaction_manager.connection_handler
            output_port_success_connector.bind("<ButtonPress-1>", lambda e, n=node_id, p="success", pt="output": connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
            output_port_error_connector.bind("<ButtonPress-1>", lambda e, n=node_id, p="error", pt="output": connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
            output_port_success_connector.bind("<Enter>", lambda e, w=output_port_success_connector: w.config(style="info.TFrame"))
            output_port_success_connector.bind("<Leave>", lambda e, w=output_port_success_connector: w.config(style="success.TFrame"))
            output_port_error_connector.bind("<Enter>", lambda e, w=output_port_error_connector: w.config(style="info.TFrame"))
            output_port_error_connector.bind("<Leave>", lambda e, w=output_port_error_connector: w.config(style="danger.TFrame"))
            for port_dict in tool_ports_widgets + input_ports_widgets:
                widget = port_dict['widget']
                widget.bind("<Enter>", lambda e, w=widget: w.config(relief="raised"))
                widget.bind("<Leave>", lambda e, w=widget: w.config(relief="flat"))
                widget.bind("<ButtonPress-1>", node_interaction_handler.on_node_press)
                widget.bind("<ButtonPress-3>", node_interaction_handler.show_node_context_menu)
        instance = self.kernel.get_component_instance(module_id)
        if instance and hasattr(instance, 'on_canvas_load'):
            instance.on_canvas_load(node_id)
        self.kernel.write_to_log(f"NODE CREATED: Name='{name}', ID='{node_id}'", "INFO")
        self.canvas_manager.visual_manager.hide_watermark()
    def _on_node_enter(self, event):
        item_ids = self.canvas.find_withtag("current")
        if not item_ids: return
        tags = self.canvas.gettags(item_ids[0])
        node_id = next((tag for tag in tags if tag in self.canvas_manager.canvas_nodes), None)
        if not node_id:
            widget = event.widget
            while widget and not hasattr(widget, 'node_id'):
                widget = widget.master
            if not widget or not widget.winfo_exists(): return
            node_id = widget.node_id
        if self.hovered_node_id == node_id: return
        self.hovered_node_id = node_id
        if node_id == self.canvas_manager.selected_node_id: return
        self._apply_style_to_node_widgets(node_id, "Hover.Glass.Module.TFrame")
    def _on_node_leave(self, event):
        if not self.hovered_node_id: return
        node_id = self.hovered_node_id
        if node_id not in self.canvas_manager.canvas_nodes: return
        self.hovered_node_id = None
        style_to_apply = "Selected.Glass.Module.TFrame" if node_id == self.canvas_manager.selected_node_id else "Glass.Module.TFrame"
        self._apply_style_to_node_widgets(node_id, style_to_apply)
    def select_node(self, node_id_to_select):
        if self.canvas_manager.selected_node_id and self.canvas_manager.selected_node_id in self.canvas_manager.canvas_nodes:
            self._apply_style_to_node_widgets(self.canvas_manager.selected_node_id, "Glass.Module.TFrame")
        self.canvas_manager.selected_node_id = node_id_to_select
        if self.canvas_manager.selected_node_id in self.canvas_manager.canvas_nodes:
            self._apply_style_to_node_widgets(self.canvas_manager.selected_node_id, "Selected.Glass.Module.TFrame")
    def deselect_all_nodes(self, event=None, from_delete=False):
        if event and self.canvas.find_withtag("current"): return
        if self.canvas_manager.selected_node_id and self.canvas_manager.selected_node_id in self.canvas_manager.canvas_nodes:
            self._apply_style_to_node_widgets(self.canvas_manager.selected_node_id, "Glass.Module.TFrame")
        self.canvas_manager.selected_node_id = None
        if not from_delete and self.canvas_manager.interaction_manager:
            self.canvas_manager.interaction_manager.connection_handler._cancel_line_drawing()
    def update_node_ports(self, node_id):
        canvas_nodes = self.canvas_manager.canvas_nodes
        if node_id not in canvas_nodes: return
        node_data = canvas_nodes[node_id]
        if node_data.get("shape") == 'agent_host' or node_data.get('shape') in ['circle', 'icon_box', 'agent_brain']:
            return
        ports_frame = node_data['ports_widget_frame']
        manager, component_data = self._get_component_data(node_data['module_id'])
        if not manager or not component_data: return
        manifest = component_data.get('manifest', {})
        config_values = node_data.get("config_values", {})
        for widget in ports_frame.winfo_children():
            widget.destroy()
        node_data['output_ports'] = []
        ports_to_create = []
        if manifest and "output_ports" in manifest:
            ports_to_create.extend(manifest["output_ports"])
        module_instance = self.kernel.get_component_instance(node_data['module_id'])
        if module_instance and hasattr(module_instance, 'get_dynamic_ports'):
            dynamic_ports = module_instance.get_dynamic_ports(config_values)
            if dynamic_ports:
                ports_to_create.extend(dynamic_ports)
        for port_info in ports_to_create:
            port_name = port_info.get("name")
            port_display_name = port_info.get("display_name", port_name)
            port_type = port_info.get("type", "output")
            port_label_frame = ttk.Frame(ports_frame, style='Glass.Module.TFrame')
            port_label_frame.pack(anchor='e', pady=1)
            label = ttk.Label(port_label_frame, text=port_display_name, style="Port.Glass.TLabel", anchor='e')
            label.pack(side="left")
            connector = ttk.Frame(port_label_frame, width=10, height=10, style="success.TFrame", relief="solid", borderwidth=1)
            connector.pack(side="left", padx=(5,0))
            connector.node_id = node_id
            connector.port_name = port_name
            node_data['output_ports'].append({"name": port_name, "widget": connector})
            connection_interaction_handler = self.canvas_manager.interaction_manager.connection_handler
            connector.bind("<ButtonPress-1>", lambda e, n=node_id, p=port_name, pt=port_type: connection_interaction_handler.start_line_drawing(n, port_name=p, port_type=pt))
            connector.bind("<Enter>", lambda e, w=connector: w.config(style="info.TFrame"))
            connector.bind("<Leave>", lambda e, w=connector: w.config(style="success.TFrame"))
            ToolTip(connector).update_text(port_info.get("tooltip", port_name))
        if self.canvas_manager.connection_manager:
            self.canvas_manager.connection_manager.update_connections_for_node(node_id)
    def update_node_visual_info(self, node_id):
        if node_id not in self.canvas_manager.canvas_nodes: return
        node_data = self.canvas_manager.canvas_nodes[node_id]
        if node_data.get("shape") == 'agent_host' or node_data.get('shape') in ['circle', 'icon_box', 'agent_brain']:
            status_widget = node_data.get('status_display_widget')
            if status_widget and status_widget.winfo_exists():
                objective = "Waiting for Mission..."
                status_widget.config(state="normal")
                status_widget.delete("1.0", "end")
                status_widget.insert("1.0", objective)
                status_widget.config(state="disabled")
            return
        info_frame = node_data.get("info_widget_frame")
        if not info_frame or not info_frame.winfo_exists(): return
        for widget in info_frame.winfo_children():
            widget.destroy()
        config = node_data.get("config_values", {})
        module_id = node_data.get("module_id")
        badges_frame = ttk.Frame(info_frame, style='Glass.Module.TFrame')
        badges_frame.pack(fill='x', pady=(2,0))
        if config.get('enable_loop', False):
            loop_count = config.get('loop_iterations', 1)
            loop_badge = ttk.Label(badges_frame, text=f"🔁 {loop_count}x", style="Glass.TLabel", font=("Helvetica", 7, "italic"))
            loop_badge.pack(side='left', padx=(0, 5))
            ToolTip(loop_badge).update_text(self.loc.get('badge_tooltip_loop', count=loop_count))
        retry_count = config.get('retry_attempts', 0)
        if retry_count > 0:
            retry_badge = ttk.Label(badges_frame, text=f"🔄 {retry_count}x", style="Glass.TLabel", font=("Helvetica", 7, "italic"))
            retry_badge.pack(side='left', padx=(0, 5))
            ToolTip(retry_badge).update_text(self.loc.get('badge_tooltip_retry', count=retry_count))
        summary_text = ""
        if module_id == 'if_module':
            var = config.get('variable_to_check', '?')
            op = config.get('comparison_operator', '??')
            val = config.get('value_to_compare', '?')
            summary_text = f"IF ({var} {op} {val})"
        elif module_id == 'sleep_module':
            sleep_type = config.get('sleep_type', 'static')
            if sleep_type == 'random_range':
                min_val = config.get('random_min', 1)
                max_val = config.get('random_max', 10)
                summary_text = f"Delay: {min_val}-{max_val}s (Random)"
            else:
                duration = config.get('duration_seconds', 3)
                summary_text = f"Delay: {duration}s"
        elif module_id == 'sub_workflow_module':
             presets = config.get('execution_order', [])
             if presets:
                summary_text = f"Run: {presets[0]}"
                if len(presets) > 1:
                    summary_text += f" (+{len(presets)-1} more)"
        if summary_text:
            summary_label = ttk.Label(info_frame, text=summary_text, style="Glass.TLabel", font=("Helvetica", 7), foreground="#a9a9a9", wraplength=180)
            summary_label.pack(fill='x', pady=(2,0))
    def delete_node(self, node_id_to_delete, feedback=True):
        self._stop_gif_animation(node_id_to_delete)
        node_data = self.canvas_manager.canvas_nodes.get(node_id_to_delete)
        if node_data and node_data.get('shape') == 'agent_brain':
            self.canvas_manager.visual_manager.stop_brain_pulse(node_id_to_delete)
        canvas_nodes = self.canvas_manager.canvas_nodes
        canvas_connections = self.canvas_manager.canvas_connections
        tooltips = self.canvas_manager.tooltips
        if node_id_to_delete not in canvas_nodes: return
        self.canvas.delete(node_id_to_delete)
        connections_to_remove = [cid for cid, cdata in canvas_connections.items() if cdata["from"] == node_id_to_delete or cdata["to"] == node_id_to_delete]
        for conn_id in connections_to_remove:
            self.canvas_manager.connection_manager.delete_connection(conn_id, feedback=False)
        if node_id_to_delete in tooltips:
            del tooltips[node_id_to_delete]
        if canvas_nodes[node_id_to_delete]["widget"] and canvas_nodes[node_id_to_delete]["widget"].winfo_exists():
            canvas_nodes[node_id_to_delete]["widget"].destroy()
        del canvas_nodes[node_id_to_delete]
        self.deselect_all_nodes(from_delete=True)
        if feedback:
            self.kernel.write_to_log(f"Node '{node_id_to_delete}' deleted successfully.", "INFO")
        if not canvas_nodes:
            self.canvas_manager.visual_manager.draw_watermark()
    def duplicate_node(self, node_id_to_duplicate):
        canvas_nodes = self.canvas_manager.canvas_nodes
        if node_id_to_duplicate not in canvas_nodes: return
        original_node_data = canvas_nodes[node_id_to_duplicate]
        new_config_values = json.loads(json.dumps(original_node_data.get('config_values', {})))
        new_x, new_y = original_node_data['x'] + 30, original_node_data['y'] + 30
        self.create_node_on_canvas(
            name=f"{original_node_data['name']} (Copy)",
            x=new_x, y=new_y,
            description=original_node_data.get('description', ''),
            module_id=original_node_data.get('module_id'),
            config_values=new_config_values
        )
        self.kernel.write_to_log(f"Node '{original_node_data['name']}' duplicated successfully.", "INFO")
