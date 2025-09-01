#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\model_converter_page.py
# JUMLAH BARIS : 231
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, messagebox, scrolledtext, filedialog
import os
import re
import threading
import time
from flowork_kernel.api_client import ApiClient
class ModelConverterPage(ttk.Frame):
    """
    The user interface for the Model Factory, allowing users to convert
    fine-tuned models into the efficient GGUF format.
    [MODIFIED] Added a tutorial and guide panel.
    [FIXED] Correctly identifies the notebook widget to get the active tab.
    """
    TIER = "pro" # (ADDED) Define the required license tier for this feature
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, padding=0)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.source_model_var = StringVar()
        self.output_name_var = StringVar()
        self.source_gguf_var = StringVar()
        self.requantize_output_name_var = StringVar()
        self.quantize_method_var = StringVar(value="Q4_K_M")
        self.job_id = None
        self.is_polling = False
        self.main_notebook = None # (ADDED) Initialize main_notebook attribute
        self._build_ui()
        self._load_initial_data()
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
        guide_content = self.loc.get("model_converter_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _build_ui(self):
        """Builds the main widgets for the page."""
        main_content_frame = ttk.Frame(self, padding=20)
        main_content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.rowconfigure(1, weight=1)
        self.main_notebook = ttk.Notebook(main_content_frame) # (MODIFIED) Assign to self.main_notebook
        self.main_notebook.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        convert_tab = ttk.Frame(self.main_notebook, padding=15)
        self.main_notebook.add(convert_tab, text="Convert HF to GGUF")
        convert_tab.columnconfigure(1, weight=1)
        ttk.Label(convert_tab, text=self.loc.get('model_converter_source_label', fallback="Fine-Tuned Model Folder:")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.model_combo = ttk.Combobox(convert_tab, textvariable=self.source_model_var, state="readonly")
        self.model_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(convert_tab, text=self.loc.get('model_converter_output_label', fallback="New .gguf Filename (no extension):")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.output_entry = ttk.Entry(convert_tab, textvariable=self.output_name_var)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        requantize_tab = ttk.Frame(self.main_notebook, padding=15)
        self.main_notebook.add(requantize_tab, text="Re-Quantize Existing GGUF")
        requantize_tab.columnconfigure(1, weight=1)
        ttk.Label(requantize_tab, text="Source .gguf File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        source_gguf_frame = ttk.Frame(requantize_tab)
        source_gguf_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        source_gguf_frame.columnconfigure(0, weight=1)
        self.source_gguf_entry = ttk.Entry(source_gguf_frame, textvariable=self.source_gguf_var)
        self.source_gguf_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(source_gguf_frame, text="Browse...", command=self._browse_gguf_file).pack(side="left", padx=(5,0))
        ttk.Label(requantize_tab, text="New Quantized Filename (no extension):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.requantize_output_entry = ttk.Entry(requantize_tab, textvariable=self.requantize_output_name_var)
        self.requantize_output_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self._add_common_settings_to_tab(convert_tab, 2)
        self._add_common_settings_to_tab(requantize_tab, 2)
        monitor_frame = ttk.LabelFrame(main_content_frame, text=self.loc.get('model_converter_monitor_title', fallback="2. Conversion Monitor"), padding=15)
        monitor_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        monitor_frame.rowconfigure(0, weight=1)
        monitor_frame.columnconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(monitor_frame, wrap="word", state="disabled", height=15, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.start_button = ttk.Button(main_content_frame, text=self.loc.get('model_converter_start_btn', fallback="Start Conversion Job"), command=self._start_job, bootstyle="success")
        self.start_button.grid(row=2, column=0, sticky="ew", pady=(10, 0), ipady=5)
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
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('model_converter_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        guide_handle.lift()
    def _add_common_settings_to_tab(self, parent_tab, start_row):
        ttk.Label(parent_tab, text=self.loc.get('model_converter_quant_label', fallback="Quantization Method:")).grid(row=start_row, column=0, sticky="w", padx=5, pady=5)
        quant_methods = ["Q2_K", "Q3_K_M", "Q4_0", "Q4_K_M", "Q5_0", "Q5_K_M", "Q6_K", "Q8_0", "F16", "F32"]
        self.quant_combo = ttk.Combobox(parent_tab, textvariable=self.quantize_method_var, values=quant_methods, state="readonly")
        self.quant_combo.grid(row=start_row, column=1, sticky="ew", padx=5, pady=5)
    def _browse_gguf_file(self):
        filepath = filedialog.askopenfilename(title="Select GGUF model file", filetypes=[("GGUF Model", "*.gguf")])
        if filepath:
            self.source_gguf_var.set(filepath)
            base_name = os.path.basename(filepath).replace(".gguf", "")
            self.requantize_output_name_var.set(f"{base_name}-quantized")
    def _load_initial_data(self):
        models_path = os.path.join(self.kernel.project_root_path, "ai_models", "text")
        local_models = []
        if os.path.isdir(models_path):
            local_models = [d for d in os.listdir(models_path) if os.path.isdir(os.path.join(models_path, d))]
        self.model_combo['values'] = sorted(local_models)
        if local_models:
            self.source_model_var.set(local_models[0])
    def _start_job(self):
        if not self.kernel.is_tier_sufficient(self.TIER):
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name="Model Factory"),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager:
                tab_manager.open_managed_tab("pricing_page")
            return
        selected_tab_index = self.main_notebook.index("current") # (FIXED) Correctly get the index from the notebook widget instance.
        quant_method = self.quantize_method_var.get()
        if selected_tab_index == 0:
            source_model = self.source_model_var.get()
            output_name = self.output_name_var.get().strip()
            if not source_model or not output_name:
                messagebox.showerror("Validation Error", "Source Model and Output Filename are required.", parent=self)
                return
            self.start_button.config(state="disabled")
            self._log_message("Sending conversion job request to the server...")
            threading.Thread(target=self._start_conversion_worker, args=(source_model, output_name, quant_method), daemon=True).start()
        elif selected_tab_index == 1:
            source_gguf = self.source_gguf_var.get()
            output_name = self.requantize_output_name_var.get().strip()
            if not source_gguf or not output_name:
                messagebox.showerror("Validation Error", "Source GGUF File and Output Filename are required.", parent=self)
                return
            self.start_button.config(state="disabled")
            self._log_message("Sending re-quantization job request to the server...")
            threading.Thread(target=self._start_requantize_worker, args=(source_gguf, output_name, quant_method), daemon=True).start()
    def _start_conversion_worker(self, source, output, method):
        success, response = self.api_client.start_model_conversion(source, output, method)
        self.after(0, self._on_job_started, success, response)
    def _start_requantize_worker(self, source, output, method):
        success, response = self.api_client.start_model_requantize(source, output, method)
        self.after(0, self._on_job_started, success, response)
    def _on_job_started(self, success, response):
        if success:
            self.job_id = response.get('job_id')
            self._log_message(f"Job successfully queued with ID: {self.job_id}")
            self._start_polling()
        else:
            messagebox.showerror("Job Error", f"Failed to start job: {response}", parent=self)
            self.start_button.config(state="normal")
    def _start_polling(self):
        if not self.is_polling:
            self.is_polling = True
            self._poll_job_status()
    def _poll_job_status(self):
        if not self.job_id:
            self.is_polling = False
            return
        threading.Thread(target=self._poll_worker, daemon=True).start()
    def _poll_worker(self):
        success, response = self.api_client.get_conversion_status(self.job_id)
        self.after(0, self._update_status_ui, success, response)
    def _update_status_ui(self, success, response):
        if success:
            status = response.get('status', 'UNKNOWN')
            full_log = response.get('log', [])
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.insert("1.0", f"Current Status: {status}\n--- LOG ---\n")
            for line in full_log:
                self.log_text.insert("end", f"{line}\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
            if status in ["COMPLETED", "FAILED"]:
                self.is_polling = False
                self.start_button.config(state="normal")
                messagebox.showinfo("Job Finished", f"Job {self.job_id} finished with status: {status}", parent=self)
            else:
                self.after(5000, self._poll_job_status)
        else:
            self._log_message(f"Error polling status: {response}")
            self.after(5000, self._poll_job_status)
    def _log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
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
