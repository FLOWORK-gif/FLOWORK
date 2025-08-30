#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\ai_architect_page.py
# JUMLAH BARIS : 144
#######################################################################

import ttkbootstrap as ttk
from tkinter import scrolledtext, messagebox
import threading
import re
class AiArchitectPage(ttk.Frame):
    """
    The user interface for the AI Architect feature, allowing users to generate
    workflows from natural language prompts.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, padding=0) # MODIFIKASI: padding diatur di frame konten
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self._build_ui()
        self._populate_guide()
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
        guide_content = self.loc.get("ai_architect_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _build_ui(self):
        """Builds the main widgets for the page."""
        main_content_frame = ttk.Frame(self, padding=20)
        main_content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.rowconfigure(1, weight=1)
        header_frame = ttk.Frame(main_content_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(header_frame, text=self.loc.get('ai_architect_page_title', fallback="AI Architect"), font=("Helvetica", 16, "bold")).pack(side="left", anchor="w")
        self.status_label = ttk.Label(header_frame, text=self.loc.get('ai_architect_status_ready', fallback="Ready."), bootstyle="secondary")
        self.status_label.pack(side="right", anchor="e")
        self.prompt_text = scrolledtext.ScrolledText(main_content_frame, wrap="word", height=10, font=("Helvetica", 11))
        self.prompt_text.grid(row=1, column=0, sticky="nsew")
        self.prompt_text.insert("1.0", self.loc.get('ai_architect_prompt_placeholder', fallback="Example: Create a workflow that gets data from a web scraper..."))
        button_container = ttk.Frame(main_content_frame)
        button_container.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        button_container.columnconfigure(0, weight=1)
        self.generate_button = ttk.Button(button_container, text=self.loc.get('ai_architect_generate_button', fallback="🚀 Generate Workflow"), command=self._start_generation_thread, bootstyle="success")
        self.generate_button.grid(row=0, column=0, sticky="ew", ipady=5)
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('ai_architect_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        guide_handle.lift() # Pastikan handle ada di lapisan paling atas
    def _start_generation_thread(self):
        if not self.kernel.is_tier_sufficient('architect'):
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name="AI Architect"),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager:
                tab_manager.open_managed_tab("pricing_page")
            return
        user_prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not user_prompt:
            messagebox.showwarning(
                self.loc.get('ai_architect_warn_empty_prompt_title', fallback="Empty Prompt"),
                self.loc.get('ai_architect_warn_empty_prompt_msg', fallback="Please describe the workflow you want to create.")
            )
            return
        self.generate_button.config(state="disabled")
        self.status_label.config(text=self.loc.get('ai_architect_status_thinking', fallback="Thinking..."), bootstyle="info")
        thread = threading.Thread(target=self._generate_workflow_worker, args=(user_prompt,), daemon=True)
        thread.start()
    def _generate_workflow_worker(self, user_prompt):
        try:
            architect_service = self.kernel.get_service("ai_architect_service")
            if not architect_service:
                raise RuntimeError("AiArchitectService not available.")
            workflow_json = architect_service.generate_workflow_from_prompt(user_prompt)
            self.after(0, self._on_generation_complete, True, workflow_json, user_prompt)
        except Exception as e:
            self.after(0, self._on_generation_complete, False, str(e), None)
    def _on_generation_complete(self, success, result, user_prompt):
        self.generate_button.config(state="normal")
        if success:
            self.status_label.config(text=self.loc.get('ai_architect_status_success', fallback="Success! New tab created."), bootstyle="success")
            tab_manager = self.kernel.get_service("tab_manager_service")
            new_tab = tab_manager.add_new_workflow_tab()
            self.after(100, lambda: self._populate_new_tab(new_tab, result, user_prompt))
        else:
            self.status_label.config(text=self.loc.get('ai_architect_status_failed', fallback="Failed."), bootstyle="danger")
            messagebox.showerror(
                self.loc.get('ai_architect_error_title', fallback="AI Architect Error"),
                self.loc.get('ai_architect_error_failed_to_create', error=result, fallback=f"Failed to create workflow:\n\n{result}")
            )
    def _populate_new_tab(self, new_tab_frame, workflow_json, user_prompt):
        if hasattr(new_tab_frame, 'canvas_area_instance') and new_tab_frame.canvas_area_instance:
            new_tab_frame.canvas_area_instance.canvas_manager.load_workflow_data(workflow_json)
            tab_title = user_prompt[:25] + '...' if len(user_prompt) > 25 else user_prompt
            self.kernel.get_service("tab_manager_service").notebook.tab(new_tab_frame, text=f" {tab_title} ")
        else:
            self.after(200, lambda: self._populate_new_tab(new_tab_frame, workflow_json, user_prompt))
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
