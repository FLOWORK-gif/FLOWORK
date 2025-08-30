#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\generator_page.py
# JUMLAH BARIS : 564
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, messagebox, Text, StringVar, BooleanVar, Toplevel, scrolledtext, Menu
import os
import json
import re
import uuid
import zipfile
import tempfile
import shutil
import importlib
import inspect
from tkinter import filedialog
from collections import OrderedDict
from .generator_components.base_component import BaseGeneratorComponent
from .generator_components.logic_builder_canvas import LogicBuilderCanvas
class GeneratorPage(ttk.Frame):
    """
    Page for the Generator Tools.
    [UPGRADE] Added a comprehensive tutorial panel to guide users through module creation.
    """
    DESIGN_STATE_KEY = "generator_page_last_state"
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, style='TFrame')
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self._drag_data = {}
        self.designed_components = {}
        self.selected_component_id = None
        self._is_updating_from_selection = False
        self.registered_components = {}
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.item_name_var = StringVar()
        self.item_id_var = StringVar()
        self.item_author_var = StringVar(value="Flowork Contributor")
        self.item_email_var = StringVar(value="contributor@teetah.art")
        self.item_website_var = StringVar(value="https://www.teetah.art")
        self.item_desc_text = None
        self.comp_prop_frame_content = None
        self._discover_and_load_components()
        self.create_widgets()
        self.item_name_var.trace_add("write", self._update_id_field)
        theme_manager = self.kernel.get_service("theme_manager")
        if theme_manager:
            self.apply_styles(theme_manager.get_colors())
        self.refresh_content()
        self._populate_guide()
        self.after(100, self._load_saved_design_state)
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
    def _populate_guide(self):
        guide_content = self.loc.get("generator_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _save_current_design_state(self):
        state_manager = self.kernel.get_service("state_manager")
        if not state_manager:
            messagebox.showerror("Error", "StateManager service not available.")
            return
        state_data = {
            "metadata": {
                "name": self.item_name_var.get(),
                "id": self.item_id_var.get(),
                "author": self.item_author_var.get(),
                "email": self.item_email_var.get(),
                "website": self.item_website_var.get(),
                "description": self.item_desc_text.get("1.0", "end-1c").strip()
            },
            "ui_components": [],
            "logic_definition": self.logic_builder_canvas.get_logic_data()
        }
        for comp_id, comp_data in self.designed_components.items():
            widget = comp_data['widget']
            state_data["ui_components"].append({
                "id": comp_id,
                "type": comp_data['type'],
                "config": comp_data['config'],
                "x": widget.winfo_x(),
                "y": widget.winfo_y()
            })
        state_manager.set(self.DESIGN_STATE_KEY, state_data)
        self.kernel.write_to_log("Generator design session saved successfully.", "SUCCESS")
        messagebox.showinfo("Sukses", "Desain saat ini berhasil disimpan. Akan dimuat otomatis saat membuka halaman ini lagi.")
    def _load_saved_design_state(self):
        state_manager = self.kernel.get_service("state_manager")
        if not state_manager: return
        state_data = state_manager.get(self.DESIGN_STATE_KEY)
        if not state_data:
            self.kernel.write_to_log("No saved generator design found.", "INFO")
            return
        self.kernel.write_to_log("Loading saved generator design...", "INFO")
        try:
            self._clear_canvas(ask_confirmation=False)
            meta = state_data.get("metadata", {})
            self.item_name_var.set(meta.get("name", ""))
            self.item_id_var.set(meta.get("id", ""))
            self.item_author_var.set(meta.get("author", ""))
            self.item_email_var.set(meta.get("email", ""))
            self.item_website_var.set(meta.get("website", ""))
            self.item_desc_text.delete("1.0", "end")
            self.item_desc_text.insert("1.0", meta.get("description", ""))
            for comp_info in state_data.get("ui_components", []):
                self._add_component_to_canvas(
                    component_type=comp_info['type'],
                    x=comp_info['x'],
                    y=comp_info['y'],
                    existing_id=comp_info['id'],
                    existing_config=comp_info['config']
                )
            self.logic_builder_canvas.load_logic_data(state_data.get("logic_definition"))
            self.kernel.write_to_log("Generator design loaded successfully.", "SUCCESS")
        except Exception as e:
            self.kernel.write_to_log(f"Failed to load generator design state: {e}", "ERROR")
            messagebox.showerror("Error", f"Gagal memuat desain yang tersimpan. File state mungkin rusak.\n\nError: {e}")
    def _clear_saved_design_state(self):
        if not messagebox.askyesno("Konfirmasi", "Anda yakin ingin menghapus desain yang tersimpan? Ini tidak bisa diurungkan."):
            return
        state_manager = self.kernel.get_service("state_manager")
        if state_manager:
            state_manager.delete(self.DESIGN_STATE_KEY)
            self.kernel.write_to_log("Saved generator design has been deleted.", "WARN")
            messagebox.showinfo("Sukses", "Desain yang tersimpan telah dihapus.")
    def _discover_and_load_components(self):
        self.kernel.write_to_log("GeneratorPage: Discovering UI component generators...", "INFO")
        components_path = os.path.join(os.path.dirname(__file__), 'generator_components')
        if not os.path.exists(components_path): return
        for filename in os.listdir(components_path):
            if filename.endswith('.py') and not filename.startswith('__') and filename != 'logic_builder_canvas.py':
                module_name = f"plugins.flowork_core_ui.generator_components.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseGeneratorComponent) and obj is not BaseGeneratorComponent:
                            instance = obj(self.kernel)
                            comp_type = instance.get_component_type()
                            self.registered_components[comp_type] = instance
                            self.kernel.write_to_log(f"  -> Loaded generator component: '{comp_type}'", "SUCCESS")
                except Exception as e:
                    self.kernel.write_to_log(f"Failed to load generator component from {filename}: {e}", "ERROR")
    def apply_styles(self, colors):
        style = tk_ttk.Style(self)
        if not colors: return
        style.configure('TFrame', background=colors.get('bg'))
        style.configure('TLabel', background=colors.get('bg'), foreground=colors.get('fg'))
        style.configure('TLabelframe', background=colors.get('bg'), relief="solid", borderwidth=1, bordercolor=colors.get('border'))
        style.configure('TLabelframe.Label', background=colors.get('bg'), foreground=colors.get('fg'), font=('Helvetica', 11, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 10, 'bold'), foreground=colors.get('primary'))
        style.configure('Ghost.TLabel', background=colors.get('primary'), foreground=colors.get('fg'), padding=5, borderwidth=1, relief='solid')
        style.configure('SelectedComponent.TFrame', borderwidth=2, relief='solid', bordercolor=colors.get('info'))
        style.configure('NormalComponent.TFrame', borderwidth=1, relief='solid', bordercolor=colors.get('border'))
    def create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill="both", expand=True, padx=15, pady=15)
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        guide_handle.lift()
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('generator_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        left_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(left_pane, weight=2)
        design_notebook = ttk.Notebook(left_pane)
        design_notebook.pack(fill='both', expand=True)
        property_design_tab = ttk.Frame(design_notebook, padding=5)
        design_notebook.add(property_design_tab, text=" 1. Desain Properti (UI) ")
        toolbox_frame = ttk.LabelFrame(property_design_tab, text=self.loc.get('generator_toolbox_title', fallback="UI Component Toolbox"), padding=10)
        toolbox_frame.pack(side='left', fill='y', padx=(0, 10))
        for comp_type, component_instance in sorted(self.registered_components.items()):
            label = component_instance.get_toolbox_label()
            self._create_draggable_button(toolbox_frame, label, comp_type)
        design_container = ttk.Frame(property_design_tab)
        design_container.pack(side='left', fill='both', expand=True)
        self.design_canvas_frame = ttk.LabelFrame(design_container, text=self.loc.get('generator_canvas_title', fallback="Property Design Canvas"), padding=10)
        self.design_canvas_frame.pack(side='top', fill='both', expand=True)
        self.canvas_placeholder = ttk.Label(self.design_canvas_frame, text=self.loc.get('generator_canvas_placeholder', fallback="Drag components from the Toolbox here..."), bootstyle="secondary")
        self.canvas_placeholder.pack(expand=True)
        self.design_canvas_frame.bind("<Button-3>", self._show_context_menu)
        self.canvas_placeholder.bind("<Button-3>", self._show_context_menu)
        property_button_frame = ttk.Frame(design_container)
        property_button_frame.pack(side='bottom', fill='x', pady=(10,0))
        clear_button = ttk.Button(property_button_frame, text=self.loc.get('generator_clear_canvas_button', fallback="Clear Canvas"), command=self._clear_canvas, bootstyle="danger-outline")
        clear_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        save_design_button = ttk.Button(property_button_frame, text="Simpan Desain", command=self._save_current_design_state, bootstyle="primary-outline")
        save_design_button.pack(side='left', expand=True, fill='x', padx=(5,5))
        clear_saved_button = ttk.Button(property_button_frame, text="Hapus Desain Tersimpan", command=self._clear_saved_design_state, bootstyle="secondary-outline")
        clear_saved_button.pack(side='left', expand=True, fill='x', padx=(5,0))
        logic_design_tab = ttk.Frame(design_notebook, padding=5)
        design_notebook.add(logic_design_tab, text=" 2. Desain Logika (Execute) ")
        self.logic_builder_canvas = LogicBuilderCanvas(logic_design_tab, self.kernel)
        self.logic_builder_canvas.pack(fill='both', expand=True)
        right_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(right_pane, weight=1)
        metadata_frame = ttk.LabelFrame(right_pane, text=self.loc.get('generator_meta_title', fallback="3. Module Info"), padding=15)
        metadata_frame.pack(fill='x', expand=False, pady=(0, 15))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_name_label', fallback="Feature Name:")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_name_var).pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_id_label', fallback="Unique ID (automatic):")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_id_var, state="readonly").pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_author_label', fallback="Author:")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_author_var).pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_email_label', fallback="Email:")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_email_var).pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_website_label', fallback="Website:")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_website_var).pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_desc_label', fallback="Description:")).pack(fill='x', anchor='w')
        self.item_desc_text = Text(metadata_frame, height=3, font=("Helvetica", 9))
        self.item_desc_text.pack(fill='x', pady=(0,5))
        self.comp_prop_frame = ttk.LabelFrame(right_pane, text=self.loc.get('generator_comp_prop_title', fallback="4. Selected Component Properties"), padding=15)
        self.comp_prop_frame.pack(fill='x', expand=False, pady=(0, 15))
        generate_frame = ttk.LabelFrame(right_pane, text=self.loc.get('generator_finalize_title', fallback="5. Finalize"), padding=15)
        generate_frame.pack(fill='x', expand=False)
        ttk.Button(generate_frame, text=self.loc.get('generator_generate_button', fallback="Generate Module ZIP File"), command=self._start_generation_process, style="success.TButton").pack(fill='x', ipady=5)
    def _create_draggable_button(self, parent, text, component_type):
        button = ttk.Button(parent, text=text)
        button.pack(fill='x', pady=2)
        button.bind("<ButtonPress-1>", lambda event, c_type=component_type: self._on_drag_start(event, c_type))
    def _on_drag_start(self, event, component_type):
        self._drag_data = {'widget': ttk.Label(self, text=event.widget.cget('text'), style='Ghost.TLabel'), 'component_type': component_type, 'drag_type': 'new_component'}
        self.winfo_toplevel().bind("<B1-Motion>", self._on_drag_motion)
        self.winfo_toplevel().bind("<ButtonRelease-1>", self._on_drag_release)
    def _on_drag_motion(self, event):
        drag_type = self._drag_data.get('drag_type')
        if not drag_type: return
        if drag_type == 'new_component':
            if self._drag_data.get('widget'): self._drag_data['widget'].place(x=event.x_root - self.winfo_toplevel().winfo_rootx(), y=event.y_root - self.winfo_toplevel().winfo_rooty())
        elif drag_type == 'move_component':
            if self._drag_data.get('widget'):
                dx, dy = event.x - self._drag_data['x'], event.y - self._drag_data['y']
                x, y = self._drag_data['widget'].winfo_x() + dx, self._drag_data['widget'].winfo_y() + dy
                self._drag_data['widget'].place(x=x, y=y)
    def _on_drag_release(self, event):
        drag_type = self._drag_data.get('drag_type')
        if not drag_type: return
        if drag_type == 'new_component':
            if self._drag_data.get('widget'): self._drag_data['widget'].destroy()
            canvas_x, canvas_y = self.design_canvas_frame.winfo_rootx(), self.design_canvas_frame.winfo_rooty()
            canvas_width, canvas_height = self.design_canvas_frame.winfo_width(), self.design_canvas_frame.winfo_height()
            if canvas_x < event.x_root < canvas_x + canvas_width and canvas_y < event.y_root < canvas_y + canvas_height:
                drop_x, drop_y = event.x_root - canvas_x - 10, event.y_root - canvas_y - 30
                self._add_component_to_canvas(self._drag_data['component_type'], drop_x, drop_y)
        self._drag_data = {}
        self.winfo_toplevel().unbind("<B1-Motion>")
        self.winfo_toplevel().unbind("<ButtonRelease-1>")
    def _add_component_to_canvas(self, component_type, x, y, existing_id=None, existing_config=None):
        if self.canvas_placeholder: self.canvas_placeholder.destroy(); self.canvas_placeholder = None
        component_generator = self.registered_components.get(component_type)
        if not component_generator: self.kernel.write_to_log(f"Attempted to add unknown component type: {component_type}", "ERROR"); return
        comp_id = existing_id or f"comp_{str(uuid.uuid4())[:8]}"
        comp_frame = ttk.Frame(self.design_canvas_frame, padding=5, style='NormalComponent.TFrame')
        if existing_config:
            config = existing_config
        else:
            var_id = f"{component_type.replace('_input','')}_{str(uuid.uuid4())[:4]}"
            config = {'label': f"My {component_type.replace('_', ' ').title()}", 'id': var_id, 'default': '', 'options': []}
            if component_type == 'checkbox': config['default'] = False
        label_widget = component_generator.create_canvas_widget(comp_frame, comp_id, config)
        for widget in [comp_frame] + comp_frame.winfo_children():
            if widget:
                widget.bind("<ButtonPress-1>", lambda e, cid=comp_id: self._on_component_press(e, cid))
                widget.bind("<B1-Motion>", self._on_drag_motion)
                widget.bind("<ButtonRelease-1>", self._on_component_release)
        comp_frame.place(x=x, y=y)
        self.designed_components[comp_id] = {'widget': comp_frame, 'label_widget': label_widget, 'type': component_type, 'config': config}
        if not existing_id:
            self.kernel.write_to_log(f"Component '{component_type}' added to design canvas.", "INFO")
            self._on_canvas_component_selected(None, comp_id)
    def _on_component_press(self, event, component_id):
        self._on_canvas_component_selected(event, component_id)
        widget_to_move = self.designed_components[component_id]['widget']
        self._drag_data = {'widget': widget_to_move, 'x': event.x, 'y': event.y, 'drag_type': 'move_component'}
        return "break"
    def _on_component_release(self, event):
        self._drag_data = {}
    def _on_canvas_component_selected(self, event, component_id):
        self._is_updating_from_selection = True
        if self.selected_component_id and self.selected_component_id in self.designed_components:
            if self.designed_components[self.selected_component_id]['widget'].winfo_exists():
                self.designed_components[self.selected_component_id]['widget'].config(style='NormalComponent.TFrame')
        self.selected_component_id = component_id
        component_data = self.designed_components.get(component_id)
        if not component_data: self._is_updating_from_selection = False; return
        component_data['widget'].config(style='SelectedComponent.TFrame')
        if self.comp_prop_frame_content and self.comp_prop_frame_content.winfo_exists(): self.comp_prop_frame_content.destroy()
        self.comp_prop_frame_content = ttk.Frame(self.comp_prop_frame)
        self.comp_prop_frame_content.pack(fill='both', expand=True)
        comp_type, config = component_data.get('type'), component_data.get('config', {})
        component_generator = self.registered_components.get(comp_type)
        if component_generator:
            prop_vars = component_generator.create_properties_ui(self.comp_prop_frame_content, config)
            if prop_vars:
                component_data['prop_vars'] = prop_vars
                for var in prop_vars.values():
                    if isinstance(var, (StringVar, BooleanVar)): var.trace_add('write', self._update_component_properties)
                    elif isinstance(var, Text): var.bind("<<Modified>>", self._update_component_properties)
        self._is_updating_from_selection = False
        if event: return "break"
    def _update_component_properties(self, *args):
        if self._is_updating_from_selection or not self.selected_component_id: return
        component_data = self.designed_components.get(self.selected_component_id)
        if not component_data or not component_data.get('prop_vars'): return
        prop_vars = component_data['prop_vars']
        for key, var in prop_vars.items():
            if isinstance(var, (StringVar, BooleanVar)):
                component_data['config'][key] = var.get()
            elif isinstance(var, Text):
                component_data['config'][key] = var.get('1.0', 'end-1c')
        if 'options' in component_data['config'] and isinstance(component_data['config']['options'], str):
            options_list = component_data['config']['options'].strip().split('\n')
            component_data['config']['options'] = [opt.strip() for opt in options_list if opt.strip()]
            visual_widget = next((w for w in component_data['widget'].winfo_children() if isinstance(w, ttk.Combobox)), None)
            if visual_widget: visual_widget['values'] = component_data['config']['options']
        label_widget, new_label_text = component_data.get('label_widget'), component_data['config'].get('label', '')
        if label_widget and label_widget.winfo_exists(): label_widget.config(text=new_label_text)
        if 'options' in prop_vars and isinstance(prop_vars.get('options'), Text): prop_vars['options'].edit_modified(False)
    def _show_context_menu(self, event):
        context_menu = Menu(self, tearoff=0)
        add_menu = Menu(context_menu, tearoff=0)
        canvas_x, canvas_y = self.design_canvas_frame.winfo_rootx(), self.design_canvas_frame.winfo_rooty()
        drop_x, drop_y = event.x_root - canvas_x, event.y_root - canvas_y
        for comp_type, comp_instance in sorted(self.registered_components.items()):
            add_menu.add_command(label=comp_instance.get_toolbox_label(), command=lambda ct=comp_type: self._add_component_to_canvas(ct, drop_x, drop_y))
        context_menu.add_cascade(label=self.loc.get('generator_context_add', fallback="Add Component"), menu=add_menu)
        context_menu.add_separator()
        delete_state = "normal" if self.selected_component_id else "disabled"
        context_menu.add_command(label=self.loc.get('generator_context_delete', fallback="Delete Selected"), command=self._delete_selected_component, state=delete_state)
        try: context_menu.tk_popup(event.x_root, event.y_root)
        finally: context_menu.grab_release()
    def _delete_selected_component(self):
        if not self.selected_component_id: return
        component_to_delete = self.designed_components.pop(self.selected_component_id, None)
        if component_to_delete: component_to_delete['widget'].destroy()
        self.selected_component_id = None
        if self.comp_prop_frame_content and self.comp_prop_frame_content.winfo_exists():
            for child in self.comp_prop_frame_content.winfo_children(): child.destroy()
        if not self.designed_components and (not self.canvas_placeholder or not self.canvas_placeholder.winfo_exists()):
            self.canvas_placeholder = ttk.Label(self.design_canvas_frame, text=self.loc.get('generator_canvas_placeholder', fallback="Drag components from the Toolbox here..."), bootstyle="secondary")
            self.canvas_placeholder.pack(expand=True)
            self.canvas_placeholder.bind("<Button-3>", self._show_context_menu)
    def _clear_canvas(self, ask_confirmation=True):
        do_clear = False
        if ask_confirmation:
            if messagebox.askyesno(self.loc.get('messagebox_confirm_title', fallback="Confirm"), self.loc.get('generator_confirm_clear_canvas', fallback="Are you sure you want to clear all components from the canvas?")):
                do_clear = True
        else:
            do_clear = True
        if do_clear:
            for comp_id in list(self.designed_components.keys()):
                self.designed_components[comp_id]['widget'].destroy()
                del self.designed_components[comp_id]
            self._delete_selected_component()
    def refresh_content(self):
        self.kernel.write_to_log("Generator page refreshed.", "DEBUG")
    def _update_id_field(self, *args):
        name_text = self.item_name_var.get().lower()
        sanitized_name = re.sub(r'[^a-z0-9_]', '', name_text.replace(' ', '_'))
        if sanitized_name:
            if not hasattr(self, '_current_random_suffix'): self._current_random_suffix = str(uuid.uuid4())[:4]
            id_text = f"{sanitized_name}_{self._current_random_suffix}"
            self.item_id_var.set(id_text)
        else: self.item_id_var.set("")
    def _sync_ui_to_config(self):
        if not self.selected_component_id: return
        self._is_updating_from_selection = False
        self._update_component_properties()
    def _start_generation_process(self):
        if not self.kernel.is_tier_sufficient('pro'):
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name="Module Generator"),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager:
                tab_manager.open_managed_tab("pricing_page")
            return
        self._sync_ui_to_config()
        module_info = {'id': self.item_id_var.get(), 'name': self.item_name_var.get(), 'author': self.item_author_var.get(), 'email': self.item_email_var.get(), 'website': self.item_website_var.get(), 'description': self.item_desc_text.get("1.0", "end-1c").strip(), 'components': list(self.designed_components.values())}
        if not module_info['id'] or not module_info['name']:
            messagebox.showerror(self.loc.get('generator_err_missing_info_title', fallback="Info Missing"), self.loc.get('generator_err_missing_info_msg', fallback="Module Name and ID are required."))
            return
        save_path = filedialog.asksaveasfilename(title=self.loc.get('generator_save_zip_title', fallback="Save Module ZIP File"), initialfile=f"{module_info['id']}.zip", defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if not save_path: return
        try:
            logic_data = self.logic_builder_canvas.get_logic_data()
            manifest_content = self._generate_manifest_content(module_info)
            processor_content = self._generate_processor_content(module_info, logic_data)
            with tempfile.TemporaryDirectory() as temp_dir:
                module_root_path = os.path.join(temp_dir, module_info['id'])
                os.makedirs(os.path.join(module_root_path, 'locales'))
                with open(os.path.join(module_root_path, 'manifest.json'), 'w', encoding='utf-8') as f: json.dump(manifest_content, f, indent=4)
                with open(os.path.join(module_root_path, 'processor.py'), 'w', encoding='utf-8') as f: f.write(processor_content)
                with open(os.path.join(module_root_path, 'locales', 'id.json'), 'w', encoding='utf-8') as f: json.dump({"module_name": module_info['name']}, f, indent=4)
                with open(os.path.join(module_root_path, 'locales', 'en.json'), 'w', encoding='utf-8') as f: json.dump({"module_name": module_info['name']}, f, indent=4)
                with open(os.path.join(module_root_path, 'requirements.txt'), 'w', encoding='utf-8') as f: f.write("# Add any required Python packages here, one per line\n")
                shutil.make_archive(os.path.splitext(save_path)[0], 'zip', temp_dir)
            messagebox.showinfo(self.loc.get('messagebox_success_title', fallback="Success"), self.loc.get('generator_zip_success_msg', fallback=f"Module '{module_info['name']}' has been successfully packaged!"))
            self.kernel.write_to_log(f"Successfully generated and saved module ZIP to {save_path}", "SUCCESS")
        except Exception as e:
            messagebox.showerror(self.loc.get('messagebox_error_title', fallback="Error"), self.loc.get('generator_zip_error_msg', fallback=f"An error occurred while generating the ZIP file: {e}"))
            self.kernel.write_to_log(f"Failed to generate module ZIP: {e}", "ERROR")
    def _generate_manifest_content(self, info):
        class_name = "".join(word.capitalize() for word in info['id'].replace('_', ' ').split()).replace(' ', '') + "Module"
        properties = []
        for comp_data in info['components']:
            comp_type, comp_config = comp_data['type'], comp_data['config']
            component_generator = self.registered_components.get(comp_type)
            if component_generator:
                entry = component_generator.generate_manifest_entry(comp_config)
                if entry: properties.append(entry)
        manifest = OrderedDict()
        ideal_order = ["id", "name", "version", "icon_file", "author", "email", "website", "description", "type", "entry_point", "behaviors", "requires_services", "properties", "output_ports"]
        manifest_data = {"id": info['id'], "name": info['name'], "version": "1.0", "icon_file": "icon.png", "author": info['author'], "email": info['email'], "website": info['website'],"description": info['description'], "type": "ACTION", "entry_point": f"processor.{class_name}", "behaviors": ["loop", "retry"], "requires_services": ["logger", "loc"],"properties": properties, "output_ports": [{"name": "success", "display_name": "Success"}, {"name": "error", "display_name": "Error"}]}
        for key in ideal_order:
            if key in manifest_data: manifest[key] = manifest_data[key]
        return manifest
    def _generate_processor_content(self, info, logic_data):
        class_name = "".join(word.capitalize() for word in info['id'].replace('_', ' ').split()).replace(' ', '') + "Module"
        all_imports = {
            "from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer",
            "import ttkbootstrap as ttk",
            "from flowork_kernel.ui_shell import shared_properties",
            "from flowork_kernel.utils.payload_helper import get_nested_value",
            "import json"
        }
        for comp_data in info['components']:
            comp_type = comp_data['type']
            component_generator = self.registered_components.get(comp_type)
            if component_generator: all_imports.update(component_generator.get_required_imports())
        imports_str = "\n".join(sorted(list(all_imports)))
        execute_lines = [
            "    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):",
            f"        self.logger(f\"Executing '{info['name']}' module logic...\", \"INFO\")",
            "        # This logic was visually generated by the Logic Builder Canvas.",
            "        internal_payload = payload.copy()",
            "        node_results = {}",
            "        module_manager = self.kernel.get_service(\"module_manager_service\")",
            "",
            "        def run_logic_node(node_id, current_payload, node_config_str):",
            "            # Replace config placeholders with actual values from the main module's config",
            "            for key, value in config.items():",
            "                placeholder = f'{{{{config.{key}}}}}'",
            "                node_config_str = node_config_str.replace(placeholder, str(value))",
            "            node_config = json.loads(node_config_str)",
            "            module_id = node_config.get('module_id')",
            "            instance = module_manager.get_instance(module_id)",
            "            if not instance: raise Exception(f'Logic node module {{module_id}} not found')",
            "            return instance.execute(current_payload, node_config.get('config_values', {}), lambda m, l: None, ui_callback, mode)",
            ""
        ]
        nodes = {node['id']: node for node in logic_data['nodes']}
        connections = logic_data['connections']
        all_node_ids = set(nodes.keys())
        nodes_with_incoming = set(conn['to'] for conn in connections)
        start_nodes = list(all_node_ids - nodes_with_incoming)
        execution_flow = {}
        for conn in connections:
            if conn['from'] not in execution_flow:
                execution_flow[conn['from']] = []
            execution_flow[conn['from']].append(conn)
        nodes_to_process = start_nodes[:]
        processed_nodes = set()
        while nodes_to_process:
            node_id = nodes_to_process.pop(0)
            if node_id in processed_nodes:
                continue
            node_info = nodes[node_id]
            node_var = f"node_results['{node_id}']"
            incoming_conns = [c for c in connections if c['to'] == node_id]
            if not incoming_conns:
                input_payload = "internal_payload"
            else:
                prev_node_id = incoming_conns[0]['from']
                input_payload = f"node_results.get('{prev_node_id}', {{}})"
            execute_lines.append(f"        # --- Executing Logic Node: {node_info.get('name')} ---")
            execute_lines.append(f"        self.logger('  -> Running logic for: {node_info.get('name')}', 'DEBUG')")
            node_config_as_string_literal = repr(json.dumps(node_info))
            execute_lines.append(f"        {node_var} = run_logic_node('{node_id}', {input_payload}, {node_config_as_string_literal})")
            processed_nodes.add(node_id)
            if node_id in execution_flow:
                for conn in execution_flow[node_id]:
                    if conn['to'] not in processed_nodes:
                        nodes_to_process.append(conn['to'])
        end_nodes = list(all_node_ids - set(conn['from'] for conn in connections))
        if end_nodes:
            final_payload_source = f"node_results.get('{end_nodes[0]}', internal_payload)"
        else:
            final_payload_source = "internal_payload"
        execute_lines.append("")
        execute_lines.append(f"        final_payload = {final_payload_source}")
        execute_lines.append("        status_updater(\"Visual logic execution complete\", \"SUCCESS\")")
        execute_lines.append("        return {\"payload\": final_payload, \"output_name\": \"success\"}")
        execute_str = "\n".join(execute_lines)
        prop_ui_lines = ["    def create_properties_ui(self, parent_frame, get_current_config, available_vars):","        config = get_current_config()","        property_vars = {}","        # Custom UI elements are generated based on the visual design",]
        for comp_data in info['components']:
            comp_type, comp_config = comp_data['type'], comp_data['config']
            component_generator = self.registered_components.get(comp_type)
            if component_generator: prop_ui_lines.extend(component_generator.generate_processor_ui_code(comp_config))
        prop_ui_lines.extend(["        # Standard settings UI","        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)","        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)","        property_vars.update(debug_vars)","        loop_vars = shared_properties.create_loop_settings_ui(parent_frame, config, self.loc, available_vars)","        property_vars.update(loop_vars)","        return property_vars"])
        prop_ui_str = "\n".join(prop_ui_lines)
        code = f"""{imports_str}
class {class_name}(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "pro"
    \"\"\"
    Module '{info['name']}' generated by Flowork Module Factory.
    Author: {info['author']}
    \"\"\"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.logger("Module '{info['name']}' initialized.", "INFO")
{execute_str}
{prop_ui_str}
    def get_data_preview(self, config: dict):
        \"\"\"
        TODO: Implement the data preview logic for this module.
        \"\"\"
        self.logger(f"'get_data_preview' is not yet implemented for {{self.module_id}}", 'WARN')
        return [{{'status': 'preview not implemented'}}]
"""
        return code
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None
