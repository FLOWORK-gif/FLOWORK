#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\plugins\flowork_core_ui\core_editor_page.py
# JUMLAH BARIS : 222
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk
import os
import json
from tkinter import messagebox, scrolledtext, Menu, Toplevel
import re
from flowork_gui.views.canvas_manager import CanvasManager
from flowork_gui.api_client.client import ApiClient
class CoreEditorPage(ttk.Frame):
    """
    The UI for the "Meta-Developer Mode" where core service
    workflows (.flowork files) can be visually edited.
    """
    def __init__(self, parent_notebook, api_client, loc_service, **kwargs): # PENAMBAHAN: New init signature.
        self.api_client = api_client
        super().__init__(parent_notebook, padding=10)
        self.loc = loc_service
        class MockKernel:
            def __init__(self, api_client_instance, loc_instance):
                self.api_client = api_client_instance
                self.loc = loc_instance
                self.services = {'localization_manager': self.loc}
                self.write_to_log = lambda msg, lvl="INFO": print(f"[INFO] (from MockKernel in CoreEditorPage): {msg}")
                self.project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            def get_service(self, service_name):
                if service_name not in self.services:
                    class MockService:
                        def __init__(self, api_client, kernel):
                            self.api_client = api_client
                            self.kernel = kernel
                        def get_colors(self): # Mock for theme manager
                            return {'bg': '#222', 'dark': '#343a40', 'success': '#28a745', 'info': '#17a2b8', 'border': 'grey'}
                    self.services[service_name] = MockService(self.api_client, self)
                return self.services.get(service_name)
        self.kernel = MockKernel(self.api_client, self.loc)
        self.canvas_manager = None
        self._drag_data = {}
        self.core_services_path = os.path.join(self.kernel.project_root_path, "core_services")
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self._build_ui()
        self._populate_service_dropdown()
        self._populate_guide()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        """ Helper function to parse simple markdown (bold). """
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
        """Populates the guide panel with localized content."""
        guide_content = self.loc.get("core_editor_guide_content", fallback="Guide content not found.")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _toggle_pin_guide(self):
        """Toggles the pinned state of the guide panel."""
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌" # Karakter pin solid
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        """Shows the guide panel."""
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self.canvas_container, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        """Schedules the guide panel to be hidden after a short delay."""
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        """Cancels a scheduled hide job."""
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None
    def _build_ui(self):
        """
        Builds the main layout with a service selector and a canvas.
        """
        control_frame = ttk.Frame(self)
        control_frame.pack(side="top", fill="x", padx=5, pady=(0, 10))
        ttk.Label(control_frame, text=self.loc.get('core_editor_select_service', fallback="Select Service to Edit:")).pack(side="left", padx=(0, 10))
        self.service_var = ttk.StringVar()
        self.service_dropdown = ttk.Combobox(control_frame, textvariable=self.service_var, state="readonly")
        self.service_dropdown.pack(side="left", fill="x", expand=True)
        self.service_dropdown.bind("<<ComboboxSelected>>", self._on_service_selected)
        self.save_button = ttk.Button(control_frame, text=self.loc.get('core_editor_save_button', fallback="Save Changes"), command=self._save_workflow_data, bootstyle="success", state="disabled")
        self.save_button.pack(side="left", padx=(10, 0))
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill="both", expand=True)
        toolbox_frame = ttk.LabelFrame(main_pane, text="Toolbox", padding=10)
        main_pane.add(toolbox_frame, weight=1)
        self.module_tree = tk_ttk.Treeview(toolbox_frame, show="tree", selectmode="browse")
        self.module_tree.pack(expand=True, fill='both')
        self._populate_module_toolbox()
        self.module_tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.module_tree.bind("<B1-Motion>", self._on_drag_motion)
        self.module_tree.bind("<ButtonRelease-1>", self._on_drag_release)
        canvas_container = ttk.LabelFrame(main_pane, text="Visual Workflow") # English Hardcode
        main_pane.add(canvas_container, weight=4)
        self.canvas_container = canvas_container
        guide_handle = ttk.Frame(self.canvas_container, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        self.guide_panel = ttk.Frame(self.canvas_container, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame = ttk.LabelFrame(self.guide_panel, text=self.loc.get('core_editor_guide_title'), padding=10)
        guide_frame.pack(fill='both', expand=True, padx=5, pady=(0,5))
        self.guide_text = scrolledtext.ScrolledText(guide_frame, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.pack(fill='both', expand=True)
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        class DummyCoordinatorTab(ttk.Frame):
            def __init__(self, kernel, editor_page):
                super().__init__()
                self.kernel = kernel
                self._execution_state = "IDLE"
                self.editor_page = editor_page
                self.bind = self.winfo_toplevel().bind
                self.unbind = self.winfo_toplevel().unbind
                self.unbind_all = self.winfo_toplevel().unbind_all
                self.after = self.winfo_toplevel().after
            def on_drag_release(self, event, item_id, tree_widget):
                self.editor_page._on_drag_release(event)
        dummy_tab = DummyCoordinatorTab(self.kernel, self)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        canvas_widget = ttk.Canvas(canvas_container, background=colors.get('bg', '#222'))
        canvas_widget.pack(expand=True, fill='both')
        guide_handle.lift()
        self.canvas_manager = CanvasManager(canvas_container, dummy_tab, canvas_widget, self.kernel)
    def _populate_module_toolbox(self):
        logic_modules = {}
        action_modules = {}
        self.module_tree.insert('', 'end', iid='logic_category', text='Logic Modules', open=True) # English Hardcode
        for mod_id, name in sorted(logic_modules.items(), key=lambda item: item[1]):
             self.module_tree.insert('logic_category', 'end', iid=mod_id, text=f" {name}")
        self.module_tree.insert('', 'end', iid='action_category', text='Action Modules', open=True) # English Hardcode
        for mod_id, name in sorted(action_modules.items(), key=lambda item: item[1]):
             self.module_tree.insert('action_category', 'end', iid=mod_id, text=f" {name}")
    def _on_drag_start(self, event):
        item_id = self.module_tree.identify_row(event.y)
        if not item_id or self.module_tree.tag_has('category', item_id): return
        self._drag_data = {"item_id": item_id, "widget": ttk.Label(self.winfo_toplevel(), text=self.module_tree.item(item_id, "text").strip(), bootstyle="inverse-info", padding=5, relief="solid"), "tree_widget": self.module_tree}
    def _on_drag_motion(self, event):
        if self._drag_data.get("widget"):
            self._drag_data['widget'].place(x=event.x_root - self.winfo_toplevel().winfo_rootx() + 10, y=event.y_root - self.winfo_toplevel().winfo_rooty() + 10)
    def _on_drag_release(self, event):
        if self.canvas_manager and self._drag_data.get("item_id"):
            self.canvas_manager.interaction_manager.on_drag_release(event, self._drag_data["item_id"], self._drag_data["tree_widget"])
        if self._drag_data.get("widget"):
            self._drag_data["widget"].destroy()
        self._drag_data = {}
    def _populate_service_dropdown(self):
        if not os.path.isdir(self.core_services_path):
            self.service_dropdown['values'] = ["'core_services' folder not found!"]
            return
        service_files = [f for f in os.listdir(self.core_services_path) if f.endswith(".flowork")]
        self.service_dropdown['values'] = sorted(service_files)
        if service_files:
            self.service_dropdown.set(service_files[0])
            self._load_workflow_data(service_files[0])
    def _on_service_selected(self, event=None):
        self.save_button.config(state="disabled")
        selected_file = self.service_var.get()
        if selected_file:
            self._load_workflow_data(selected_file)
    def _load_workflow_data(self, filename):
        if not self.canvas_manager: return
        file_path = os.path.join(self.core_services_path, filename)
        self.kernel.write_to_log(f"Core Editor: Loading '{filename}'...", "INFO") # English Log
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            self.canvas_manager.load_workflow_data(workflow_data)
            self.kernel.write_to_log(f"Core Editor: Successfully rendered '{filename}'.", "SUCCESS") # English Log
            self.save_button.config(state="normal")
        except Exception as e:
            self.canvas_manager.clear_canvas(feedback=False)
            self.kernel.write_to_log(f"Core Editor: Failed to load or parse '{filename}': {e}", "ERROR") # English Log
            self.save_button.config(state="disabled")
            messagebox.showerror(
                self.loc.get('error_title', fallback="Error"),
                f"Failed to load service workflow '{filename}'.\nThe file might be corrupted or empty. Saving is disabled to prevent data loss.",
                parent=self
            )
    def _save_workflow_data(self):
        if not self.canvas_manager:
            messagebox.showerror("Error", "Canvas is not ready.") # English Hardcode
            return
        selected_file = self.service_var.get()
        if not selected_file:
            messagebox.showwarning("Warning", "No service workflow is selected to save.") # English Hardcode
            return
        workflow_data = self.canvas_manager.get_workflow_data()
        file_path = os.path.join(self.core_services_path, selected_file)
        self.kernel.write_to_log(f"Core Editor: Saving changes to '{selected_file}'...", "INFO") # English Log
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=4, ensure_ascii=False)
            self.kernel.write_to_log(f"Core Editor: Successfully saved '{selected_file}'.", "SUCCESS") # English Log
            messagebox.showinfo("Success", f"Changes to '{selected_file}' have been saved.") # English Hardcode
        except Exception as e:
            self.kernel.write_to_log(f"Core Editor: Failed to save '{selected_file}': {e}", "ERROR") # English Log
            messagebox.showerror("Error", f"Failed to save file: {e}") # English Hardcode
