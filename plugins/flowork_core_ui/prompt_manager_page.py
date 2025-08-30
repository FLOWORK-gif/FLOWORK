#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\prompt_manager_page.py
# JUMLAH BARIS : 164
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, scrolledtext, StringVar, Toplevel
from flowork_kernel.api_client import ApiClient
import re
class PromptManagerPage(ttk.Frame):
    def __init__(self, parent, kernel, **kwargs):
        super().__init__(parent, **kwargs)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.current_prompt_id = None
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        left_pane = ttk.Frame(self, padding=10)
        left_pane.grid(row=0, column=0, sticky="ns", padx=(0, 5))
        left_pane.rowconfigure(1, weight=1)
        list_toolbar = ttk.Frame(left_pane)
        list_toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        new_button = ttk.Button(list_toolbar, text=self.loc.get("button_new", fallback="New"), command=self._new_prompt)
        new_button.pack(side="left")
        delete_button = ttk.Button(list_toolbar, text=self.loc.get("button_delete", fallback="Delete"), command=self._delete_prompt, bootstyle="danger")
        delete_button.pack(side="left", padx=5)
        self.prompt_tree = ttk.Treeview(left_pane, columns=("name",), show="tree", selectmode="browse")
        self.prompt_tree.grid(row=1, column=0, sticky="ns")
        self.prompt_tree.bind("<<TreeviewSelect>>", self._on_prompt_select)
        self.right_pane = ttk.Frame(self, padding=10)
        self.right_pane.grid(row=0, column=1, sticky="nsew")
        self.right_pane.columnconfigure(0, weight=1)
        self.right_pane.rowconfigure(0, weight=1) # MODIFIKASI: Editor sekarang di row 0
        editor_frame = ttk.LabelFrame(self.right_pane, text=self.loc.get("prompt_manager_editor_title", fallback="Prompt Editor"))
        editor_frame.grid(row=0, column=0, sticky="nsew") # MODIFIKASI: Editor sekarang di row 0
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(3, weight=1)
        self.name_var = StringVar()
        ttk.Label(editor_frame, text=self.loc.get("prompt_manager_name_label", fallback="Template Name:")).grid(row=0, column=0, sticky="w", padx=10, pady=(10,2))
        ttk.Entry(editor_frame, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))
        ttk.Label(editor_frame, text=self.loc.get("prompt_manager_content_label", fallback="Template Content:")).grid(row=2, column=0, sticky="nw", padx=10, pady=(0,2))
        self.content_text = scrolledtext.ScrolledText(editor_frame, wrap="word", height=15, font=("Consolas", 10))
        self.content_text.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,10))
        save_button = ttk.Button(self.right_pane, text=self.loc.get("button_save_changes", fallback="Save Changes"), command=self._save_prompt, bootstyle="success")
        save_button.grid(row=1, column=0, sticky="e", pady=10) # MODIFIKASI: Save button sekarang di row 1
        self._build_guide_panel()
        self._load_prompt_list()
        self._populate_tutorial()
    def _build_guide_panel(self):
        guide_handle = ttk.Frame(self.right_pane, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        guide_handle.lift()
        self.guide_panel = ttk.Frame(self.right_pane, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        tutorial_frame = ttk.LabelFrame(self.guide_panel, text=self.loc.get("prompt_manager_tutorial_title", fallback="Guide & How-To"))
        tutorial_frame.pack(fill='both', expand=True, padx=5, pady=(0,5))
        tutorial_frame.columnconfigure(0, weight=1)
        tutorial_frame.rowconfigure(0, weight=1)
        self.tutorial_text = scrolledtext.ScrolledText(tutorial_frame, wrap="word", height=10, state="disabled", font="-size 9")
        self.tutorial_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tutorial_text.tag_configure("bold", font="-size 9 -weight bold")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
    def _populate_tutorial(self):
        tutorial_content = self.loc.get("prompt_manager_tutorial_content")
        self._apply_markdown_to_text_widget(self.tutorial_text, tutorial_content)
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
    def _load_prompt_list(self):
        for i in self.prompt_tree.get_children():
            self.prompt_tree.delete(i)
        success, data = self.api_client.get_prompts()
        if success:
            if isinstance(data, list):
                for prompt in data:
                    self.prompt_tree.insert("", "end", iid=prompt['id'], text=prompt['name'])
            else:
                self.prompt_tree.insert("", "end", text="Error: Invalid data format from API.")
        else:
            self.prompt_tree.insert("", "end", text="Error loading prompts...")
    def _on_prompt_select(self, event):
        selected_items = self.prompt_tree.selection()
        if not selected_items:
            return
        self.current_prompt_id = selected_items[0]
        success, data = self.api_client.get_prompt(self.current_prompt_id)
        if success:
            self.name_var.set(data.get('name', ''))
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", data.get('content', ''))
        else:
            error_message = data if isinstance(data, str) else data.get('error', 'Unknown error')
            messagebox.showerror("Error", f"Could not load prompt details: {error_message}", parent=self)
    def _new_prompt(self):
        self.current_prompt_id = None
        self.name_var.set("")
        self.content_text.delete("1.0", "end")
        self.prompt_tree.selection_set("")
    def _save_prompt(self):
        name = self.name_var.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()
        if not name or not content:
            messagebox.showwarning("Input Required", "Template Name and Content cannot be empty.", parent=self)
            return
        prompt_data = {"name": name, "content": content}
        if self.current_prompt_id:
            success, response = self.api_client.update_prompt(self.current_prompt_id, prompt_data)
        else:
            success, response = self.api_client.create_prompt(prompt_data)
        if success:
            messagebox.showinfo("Success", "Prompt template saved successfully.", parent=self)
            self._load_prompt_list()
        else:
            error_message = response if isinstance(response, str) else response.get('error', 'Unknown error')
            messagebox.showerror("Error", f"Failed to save prompt: {error_message}", parent=self)
    def _delete_prompt(self):
        if not self.current_prompt_id:
            messagebox.showwarning("Selection Required", "Please select a template to delete.", parent=self)
            return
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this prompt template?", parent=self):
            success, response = self.api_client.delete_prompt(self.current_prompt_id)
            if success:
                messagebox.showinfo("Success", "Prompt template deleted.", parent=self)
                self._new_prompt()
                self._load_prompt_list()
            else:
                error_message = response if isinstance(response, str) else response.get('error', 'Unknown error')
                messagebox.showerror("Error", f"Failed to delete prompt: {error_message}", parent=self)
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self.right_pane, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None
