#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\canvas_components\visual_manager.py
# JUMLAH BARIS : 343
#######################################################################

import ttkbootstrap as ttk
from tkinter import TclError
from ..custom_widgets.tooltip import ToolTip
class VisualManager:
    """
    Manages all visual aspects and effects on the canvas.
    (MODIFIED V3) Added a pulsing animation for 'agent_brain' nodes and redesigned default node style.
    """
    def __init__(self, canvas_manager, kernel, canvas_widget):
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.canvas = canvas_widget
        self.loc = self.kernel.get_service("localization_manager")
        self._watermark_id = None
        self._sleeping_animation_jobs = {}
        self.suggestion_indicators = {}
        self.processing_animations = {}
        self.brain_pulse_jobs = {}
        self._animation_frames = ['|', '/', '-', '\\']
        self._last_timeline_highlight_id = None
        self._define_highlight_styles()
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.draw_grid()
    def _get_original_style(self, node_id):
        """Determines the correct default style for a node (selected or normal)."""
        if node_id == self.canvas_manager.selected_node_id:
            return "Selected.Glass.Module.TFrame"
        else:
            return "Glass.Module.TFrame"
    def start_brain_pulse(self, node_id):
        if node_id in self.brain_pulse_jobs or not self.canvas.winfo_exists():
            return
        node_data = self.canvas_manager.canvas_nodes.get(node_id)
        if not node_data or node_data.get('shape') != 'agent_brain':
            return
        shape_id = node_data.get('oval_id')
        if not shape_id or not self.canvas.find_withtag(shape_id):
            return
        pulse_config = {
            'shape_id': shape_id,
            'min_width': 1.0,
            'max_width': 3.0,
            'step': 0.2,
            'direction': 1
        }
        self.brain_pulse_jobs[node_id] = pulse_config
        self._animate_brain_pulse(node_id)
    def _animate_brain_pulse(self, node_id):
        if node_id not in self.brain_pulse_jobs or not self.canvas.winfo_exists():
            return
        pulse_config = self.brain_pulse_jobs[node_id]
        shape_id = pulse_config['shape_id']
        if not self.canvas.find_withtag(shape_id):
            if node_id in self.brain_pulse_jobs:
                del self.brain_pulse_jobs[node_id]
            return
        current_width = self.canvas.itemcget(shape_id, "width")
        try:
            current_width_float = float(current_width)
        except ValueError:
            current_width_float = pulse_config['min_width']
        new_width = current_width_float + (pulse_config['step'] * pulse_config['direction'])
        if new_width >= pulse_config['max_width']:
            new_width = pulse_config['max_width']
            pulse_config['direction'] = -1
        elif new_width <= pulse_config['min_width']:
            new_width = pulse_config['min_width']
            pulse_config['direction'] = 1
        self.canvas.itemconfig(shape_id, width=new_width)
        job_id = self.canvas.after(50, self._animate_brain_pulse, node_id)
        self.brain_pulse_jobs[node_id]['job_id'] = job_id
    def stop_brain_pulse(self, node_id):
        if node_id in self.brain_pulse_jobs:
            job_id = self.brain_pulse_jobs[node_id].get('job_id')
            if job_id:
                try:
                    self.canvas.after_cancel(job_id)
                except TclError:
                    pass
            del self.brain_pulse_jobs[node_id]
    def _on_canvas_resize(self, event=None):
        self.canvas.delete("grid_dot")
        self.draw_grid()
        self.draw_watermark()
    def draw_grid(self):
        if not self.canvas.winfo_exists():
            return
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            self.canvas_manager.coordinator_tab.after(100, self.draw_grid)
            return
        grid_spacing = 30
        dot_size = 1
        dot_color = "#4a4a4a"
        for x in range(0, canvas_width, grid_spacing):
            for y in range(0, canvas_height, grid_spacing):
                x1, y1 = x - dot_size, y - dot_size
                x2, y2 = x + dot_size, y + dot_size
                self.canvas.create_oval(x1, y1, x2, y2, fill=dot_color, outline="", tags="grid_dot")
        self.canvas.tag_lower("grid_dot")
    def _define_highlight_styles(self):
        style = ttk.Style.get_instance()
        colors = self.canvas_manager.colors
        glass_bg = '#222831'
        glass_border = '#393E46'
        style.configure('Glass.Module.TFrame', background=glass_bg, bordercolor=glass_border, borderwidth=1, relief='solid')
        style.configure('Glass.TLabel', background=glass_bg, foreground=colors.get('fg'))
        style.configure('Port.Glass.TLabel', background=glass_bg, foreground=colors.get('fg'))
        style.configure('Selected.Glass.Module.TFrame', background=glass_bg, bordercolor=colors.get('success'), borderwidth=2, relief='solid')
        style.configure('Selected.Glass.TLabel', background=glass_bg, foreground=colors.get('success'))
        style.configure('Hover.Glass.Module.TFrame', background=glass_bg, bordercolor=colors.get('info'), borderwidth=2, relief='solid')
        style.configure('Hover.Glass.TLabel', background=glass_bg, foreground=colors.get('info'))
        style.configure('Droppable.Module.TFrame', background=glass_bg, bordercolor=colors.get('success'), borderwidth=2, relief='solid')
        style.configure('Droppable.TLabel', background=glass_bg, foreground=colors.get('success'))
        style.configure('Executing.Module.TFrame', background=colors.get('warning', '#ffc107'), bordercolor=colors.get('light', '#FFFFFF'))
        style.configure('Sleeping.Module.TFrame', background=colors.get('info', '#17a2b8'), bordercolor=colors.get('light', '#FFFFFF'))
    def draw_watermark(self):
        self.hide_watermark()
        if not self.canvas.winfo_exists():
            return
        if not self.canvas_manager.canvas_nodes:
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                self.canvas_manager.coordinator_tab.after(100, self.draw_watermark)
                return
            x = canvas_width / 2
            y = canvas_height / 2
            self._watermark_id = self.canvas.create_text(
                x, y,
                text="WWW.TEETAH.ART",
                font=("Helvetica", int(min(canvas_width, canvas_height) * 0.15), "bold"),
                fill="#3a3a3a",
                state="disabled",
                tags="watermark_tag",
                anchor="center"
            )
            self.canvas.tag_lower(self._watermark_id)
    def hide_watermark(self):
        if self._watermark_id:
            if self.canvas.winfo_exists() and self.canvas.find_withtag(self._watermark_id):
                self.canvas.delete(self._watermark_id)
            self._watermark_id = None
    def start_processing_animation(self, node_id):
        self.stop_processing_animation(node_id)
        if node_id not in self.canvas_manager.canvas_nodes: return
        node_widget = self.canvas_manager.canvas_nodes[node_id]['widget']
        if not node_widget.winfo_exists(): return
        light_length = 30
        light_thickness = 4
        color = self.canvas_manager.colors.get('warning', '#ffc107')
        x = node_widget.winfo_x()
        y = node_widget.winfo_y()
        light_id = self.canvas.create_rectangle(
            x, y - light_thickness / 2, x + light_length, y + light_thickness / 2,
            fill=color,
            outline=""
        )
        self.canvas.tag_raise(light_id)
        self.processing_animations[node_id] = {
            "light_id": light_id,
            "after_id": None,
            "position": 0,
            "speed": 5,
            "length": light_length,
            "thickness": light_thickness
        }
        self._animate_processing_border(node_id)
    def _animate_processing_border(self, node_id):
        if node_id not in self.processing_animations:
            return
        animation_data = self.processing_animations[node_id]
        light_id = animation_data['light_id']
        node_widget = self.canvas_manager.canvas_nodes.get(node_id, {}).get('widget')
        if not self.canvas.find_withtag(light_id) or not node_widget or not node_widget.winfo_exists():
            self.stop_processing_animation(node_id)
            return
        x, y = node_widget.winfo_x(), node_widget.winfo_y()
        w, h = node_widget.winfo_width(), node_widget.winfo_height()
        perimeter = (w * 2) + (h * 2)
        if perimeter == 0:
            after_id = self.canvas.after(50, self._animate_processing_border, node_id)
            animation_data['after_id'] = after_id
            return
        pos = (animation_data['position'] + animation_data['speed']) % perimeter
        animation_data['position'] = pos
        length = animation_data['length']
        thickness = animation_data['thickness']
        half_thick = thickness / 2
        if 0 <= pos < w:
            x1, y1 = x + pos, y - half_thick
            x2, y2 = x + pos - length, y + half_thick
            self.canvas.coords(light_id, x1, y1, x2, y2)
        elif w <= pos < w + h:
            x1, y1 = x + w - half_thick, y + (pos - w)
            x2, y2 = x + w + half_thick, y + (pos - w) - length
            self.canvas.coords(light_id, x1, y1, x2, y2)
        elif w + h <= pos < w + h + w:
            x1, y1 = x + w - (pos - (w + h)), y + h - half_thick
            x2, y2 = x + w - (pos - (w + h)) + length, y + h + half_thick
            self.canvas.coords(light_id, x1, y1, x2, y2)
        else:
            x1, y1 = x - half_thick, y + h - (pos - (w + h + w))
            x2, y2 = x + half_thick, y + h - (pos - (w + h + w)) + length
            self.canvas.coords(light_id, x1, y1, x2, y2)
        if node_id in self.processing_animations:
            after_id = self.canvas.after(20, self._animate_processing_border, node_id)
            self.processing_animations[node_id]['after_id'] = after_id
    def stop_processing_animation(self, node_id):
        if node_id in self.processing_animations:
            animation_data = self.processing_animations.pop(node_id)
            after_id = animation_data.get('after_id')
            if after_id:
                try:
                    self.canvas.after_cancel(after_id)
                except TclError:
                    pass
            if self.canvas.winfo_exists() and self.canvas.find_withtag(animation_data['light_id']):
                self.canvas.delete(animation_data['light_id'])
    def highlight_timeline_step(self, connection_id_to_highlight):
        self.clear_timeline_highlight()
        if connection_id_to_highlight in self.canvas_manager.canvas_connections:
            line_id = self.canvas_manager.canvas_connections[connection_id_to_highlight]['line_id']
            if self.canvas.find_withtag(line_id):
                colors = self.canvas_manager.colors
                highlight_color = colors.get('info', '#17a2b8')
                self.canvas.itemconfig(line_id, fill=highlight_color, width=4, dash=())
                self._last_timeline_highlight_id = line_id
    def clear_timeline_highlight(self):
        if self._last_timeline_highlight_id:
            if self.canvas.find_withtag(self._last_timeline_highlight_id):
                colors = self.canvas_manager.colors
                original_color = colors.get('success', '#76ff7b')
                self.canvas.itemconfig(self._last_timeline_highlight_id, fill=original_color, width=2, dash=(4, 4))
            self._last_timeline_highlight_id = None
    def show_suggestion_indicator(self, node_id, suggestion_text):
        self.hide_suggestion_indicator(node_id)
        canvas_nodes = self.canvas_manager.canvas_nodes
        if node_id not in canvas_nodes: return
        node_widget = canvas_nodes[node_id].get("widget")
        if not node_widget or not node_widget.winfo_exists(): return
        indicator_label = ttk.Label(node_widget, text="💡", font=("Segoe UI Emoji", 10), bootstyle="warning")
        indicator_label.place(relx=1.0, rely=0.0, x=-5, y=-5, anchor="ne")
        ToolTip(indicator_label).update_text(suggestion_text)
        self.suggestion_indicators[node_id] = indicator_label
    def hide_suggestion_indicator(self, node_id):
        if node_id in self.suggestion_indicators:
            indicator = self.suggestion_indicators.pop(node_id)
            if indicator and indicator.winfo_exists(): indicator.destroy()
    def clear_all_suggestion_indicators(self):
        for node_id in list(self.suggestion_indicators.keys()): self.hide_suggestion_indicator(node_id)
    def highlight_element(self, element_type, element_id):
        self.stop_sleeping_animation(element_id)
        if element_type == 'node':
            self.start_processing_animation(element_id)
        elif element_type == 'tool_node':
            if element_id not in self.canvas_manager.canvas_nodes: return
            node_data = self.canvas_manager.canvas_nodes[element_id]
            widget = node_data.get('widget')
            if not widget or not widget.winfo_exists(): return
            original_style = self._get_original_style(element_id)
            self.canvas_manager.node_manager._apply_style_to_node_widgets(element_id, "Executing.Module.TFrame")
            self.canvas.after(1500, lambda: self.canvas_manager.node_manager._apply_style_to_node_widgets(element_id, original_style))
        elif element_type == 'sleeping_node':
            if element_id not in self.canvas_manager.canvas_nodes: return
            widget = self.canvas_manager.canvas_nodes[element_id]['widget']
            if widget.cget('style') == 'Selected.Module.TFrame': return
            widget.config(style='Sleeping.Module.TFrame')
            self.start_sleeping_animation(element_id)
        elif element_type == 'connection':
            if element_id not in self.canvas_manager.canvas_connections: return
            line_id = self.canvas_manager.canvas_connections[element_id]['line_id']
            colors = self.canvas_manager.colors
            original_color = colors.get('success', '#76ff7b')
            highlight_color = colors.get('warning', '#ffc107')
            self.canvas.itemconfig(line_id, fill=highlight_color, width=3, dash=())
            self.canvas_manager.coordinator_tab.after(1500, lambda: self.canvas.itemconfig(line_id, fill=original_color, width=2) if self.canvas.find_withtag(line_id) else None)
    def update_node_status(self, node_id, message, level):
        if node_id not in self.canvas_manager.canvas_nodes: return
        if level.upper() in ["SUCCESS", "ERROR", "WARN"]:
            self.stop_processing_animation(node_id)
        node_frame = self.canvas_manager.canvas_nodes[node_id]['widget']
        if node_id in self._sleeping_animation_jobs and "jeda" not in message.lower() and "sleep" not in message.lower():
            self.stop_sleeping_animation(node_id)
        try:
            if not node_frame.winfo_exists():
                return
            content_frame = node_frame.winfo_children()[0]
            status_label = next((w for w in content_frame.winfo_children() if isinstance(w, ttk.Label) and 'status_' in w.winfo_name()), None)
            if status_label:
                if not hasattr(node_frame, '_original_status_message') or (status_label.cget("text").replace(" |", "").replace(" /", "").replace(" -", "").replace(" \\", "").strip() != message.strip()):
                    node_frame._original_status_message = message
                colors = self.canvas_manager.colors
                color_map = {"SUCCESS": colors.get('success'), "ERROR": colors.get('danger'), "WARN": colors.get('warning'), "INFO": colors.get('info'), "DEBUG": colors.get('secondary')}
                current_style = node_frame.cget('style')
                if current_style == 'Selected.Glass.Module.TFrame': bg_color, fg_color = colors.get('dark'), colors.get('success')
                elif current_style == 'Hover.Glass.Module.TFrame': bg_color, fg_color = colors.get('dark'), colors.get('info')
                elif current_style == 'Executing.Module.TFrame': bg_color, fg_color = colors.get('warning'), colors.get('dark')
                elif current_style == 'Sleeping.Module.TFrame': bg_color, fg_color = colors.get('info'), colors.get('light')
                else: bg_color, fg_color = colors.get('dark'), colors.get('fg')
                status_label.config(text=message, foreground=color_map.get(level, fg_color), background=bg_color)
        except (TclError, IndexError): pass
    def start_sleeping_animation(self, node_id):
        self.stop_sleeping_animation(node_id)
        node_data = self.canvas_manager.canvas_nodes.get(node_id)
        if not node_data or not node_data['widget'].winfo_exists(): return
        status_label = next((w for w in node_data['widget'].winfo_children()[0].winfo_children() if isinstance(w, ttk.Label) and 'status_' in w.winfo_name()), None)
        if not status_label: return
        if not hasattr(node_data['widget'], '_original_status_message'):
            node_data['widget']._original_status_message = status_label.cget("text")
        self._update_sleeping_animation_frame(node_id, 0)
    def _update_sleeping_animation_frame(self, node_id, frame_index):
        node_data = self.canvas_manager.canvas_nodes.get(node_id)
        if not node_data or not node_data['widget'].winfo_exists():
            self.stop_sleeping_animation(node_id)
            return
        status_label = next((w for w in node_data['widget'].winfo_children()[0].winfo_children() if isinstance(w, ttk.Label) and 'status_' in w.winfo_name()), None)
        if not status_label: return
        original_msg = getattr(node_data['widget'], '_original_status_message', "")
        animated_char = self._animation_frames[frame_index % len(self._animation_frames)]
        status_label.config(text=f"{original_msg} {animated_char}")
        next_frame_index = (frame_index + 1) % len(self._animation_frames)
        job_id = self.canvas_manager.coordinator_tab.after(150, self._update_sleeping_animation_frame, node_id, next_frame_index)
        self._sleeping_animation_jobs[node_id] = job_id
    def stop_sleeping_animation(self, node_id):
        if node_id in self._sleeping_animation_jobs:
            self.canvas_manager.coordinator_tab.after_cancel(self._sleeping_animation_jobs[node_id])
            del self._sleeping_animation_jobs[node_id]
            node_data = self.canvas_manager.canvas_nodes.get(node_id)
            if node_data and node_data['widget'].winfo_exists():
                status_label = next((w for w in node_data['widget'].winfo_children()[0].winfo_children() if isinstance(w, ttk.Label) and 'status_' in w.winfo_name()), None)
                if status_label:
                    status_label.config(text=getattr(node_data['widget'], '_original_status_message', status_label.cget("text").rstrip(' |/-\\')))
