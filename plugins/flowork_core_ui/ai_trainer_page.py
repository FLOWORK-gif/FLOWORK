#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\ai_trainer_page.py
# JUMLAH BARIS : 239
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, messagebox, scrolledtext
import os
import re
import threading
import time
from flowork_kernel.api_client import ApiClient
from widgets.dataset_manager_widget.dataset_manager_widget import DatasetManagerWidget
class AITrainerPage(ttk.Frame):
    """
    The main UI page for initiating and monitoring AI model fine-tuning jobs.
    [MODIFIED] Added a tutorial and guide panel.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, padding=15)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.base_model_var = StringVar()
        self.dataset_var = StringVar()
        self.new_model_name_var = StringVar()
        self.epochs_var = StringVar(value="1")
        self.batch_size_var = StringVar(value="4")
        self.job_id = None
        self.is_polling = False
        self._build_ui()
        self._load_initial_data()
        self._populate_guide()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        """ (ADDED) Helper function to parse simple markdown (bold). """
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
        guide_content = self.loc.get("ai_trainer_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.grid(row=0, column=0, sticky="nsew")
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
        guide_frame = ttk.LabelFrame(self.guide_panel, text=self.loc.get('ai_trainer_guide_title'), padding=15)
        guide_frame.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame.columnconfigure(0, weight=1)
        guide_frame.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame, wrap="word", height=12, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        left_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(left_pane, weight=2)
        config_frame = ttk.LabelFrame(left_pane, text="1. Training Configuration", padding=15)
        config_frame.pack(fill='x', expand=False)
        base_model_frame = ttk.Frame(config_frame)
        base_model_frame.pack(fill='x', pady=(2, 10))
        base_model_frame.columnconfigure(1, weight=1)
        ttk.Label(base_model_frame, text="Base Model (for new training only):").grid(row=0, column=0, columnspan=3, sticky='w')
        self.model_combo = ttk.Combobox(base_model_frame, textvariable=self.base_model_var, state="readonly")
        self.model_combo.grid(row=1, column=0, columnspan=2, sticky='ew')
        refresh_model_button = ttk.Button(base_model_frame, text="⟳", width=3, command=self._load_initial_data, style="secondary.TButton")
        refresh_model_button.grid(row=1, column=2, padx=(5,0))
        ttk.Label(config_frame, text="Dataset for Training:").pack(anchor='w')
        self.dataset_combo = ttk.Combobox(config_frame, textvariable=self.dataset_var, state="readonly")
        self.dataset_combo.pack(fill='x', pady=(2, 10))
        ttk.Label(config_frame, text="New or Existing Model Name:").pack(anchor='w')
        self.new_model_name_combo = ttk.Combobox(config_frame, textvariable=self.new_model_name_var)
        self.new_model_name_combo.pack(fill='x', pady=(2, 10))
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill='x', pady=5)
        ttk.Label(params_frame, text="Epochs:").pack(side='left')
        ttk.Entry(params_frame, textvariable=self.epochs_var, width=5).pack(side='left', padx=(5, 20))
        ttk.Label(params_frame, text="Batch Size:").pack(side='left')
        ttk.Entry(params_frame, textvariable=self.batch_size_var, width=5).pack(side='left', padx=5)
        self.dataset_manager = DatasetManagerWidget(
            left_pane,
            self.winfo_toplevel(),
            self.kernel,
            "ai_trainer_dataset_manager",
            refresh_callback=self._load_initial_data
        )
        self.dataset_manager.pack(fill='both', expand=True, pady=(10,0))
        right_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(right_pane, weight=3)
        monitor_frame = ttk.LabelFrame(right_pane, text="2. Training Monitor", padding=15)
        monitor_frame.pack(fill='both', expand=True)
        monitor_frame.rowconfigure(1, weight=1)
        monitor_frame.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(monitor_frame, text="Status: Idle", font="-size 10")
        self.status_label.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self.log_text = scrolledtext.ScrolledText(monitor_frame, wrap="word", state="disabled", height=15)
        self.log_text.grid(row=1, column=0, sticky='nsew')
        self.progress_bar = ttk.Progressbar(monitor_frame, mode='determinate')
        self.progress_bar.grid(row=2, column=0, sticky='ew', pady=(10, 10))
        self.start_button = ttk.Button(monitor_frame, text="🚀 Start Fine-Tuning Job", command=self._start_training_job, bootstyle="success")
        self.start_button.grid(row=3, column=0, sticky='ew', ipady=5)
    def _load_initial_data(self):
        threading.Thread(target=self._load_data_worker, daemon=True).start()
    def _load_data_worker(self):
        models_path = os.path.join(self.kernel.project_root_path, "ai_models", "text")
        local_models = []
        if os.path.isdir(models_path):
            local_models = [d for d in os.listdir(models_path) if os.path.isdir(os.path.join(models_path, d))]
        success, datasets_response = self.api_client.list_datasets()
        datasets = datasets_response if success else []
        self.after(0, self._populate_combos, local_models, datasets)
    def _populate_combos(self, models, datasets):
        sorted_models = sorted(models)
        self.model_combo['values'] = sorted_models
        self.new_model_name_combo['values'] = sorted_models
        if 'training' in sorted_models:
            self.base_model_var.set('training')
            self.new_model_name_var.set('training')
        elif sorted_models:
            if self.base_model_var.get() not in sorted_models:
                self.base_model_var.set(sorted_models[0])
        dataset_names = [ds['name'] for ds in datasets]
        self.dataset_combo['values'] = sorted(dataset_names)
        if dataset_names:
            if self.dataset_var.get() not in dataset_names:
                self.dataset_var.set(dataset_names[0])
        if hasattr(self, 'dataset_manager'):
            self.dataset_manager._populate_dataset_combo(True, datasets)
    def _start_training_job(self):
        base_model = self.base_model_var.get()
        dataset = self.dataset_var.get()
        new_model_name = self.new_model_name_var.get().strip()
        new_model_name = re.sub(r'[^a-zA-Z0-9_-]', '', new_model_name)
        if not all([base_model, dataset, new_model_name]):
            messagebox.showerror("Validation Error", "All fields (Base Model, Dataset, New/Existing Model Name) are required.", parent=self)
            return
        try:
            training_args = {
                "epochs": int(self.epochs_var.get()),
                "batch_size": int(self.batch_size_var.get())
            }
        except ValueError:
            messagebox.showerror("Validation Error", "Epochs and Batch Size must be numbers.", parent=self)
            return
        self.start_button.config(state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", "Sending training job request to the server...\n")
        self.log_text.config(state="disabled")
        threading.Thread(
            target=self._start_training_worker,
            args=(base_model, dataset, new_model_name, training_args),
            daemon=True
        ).start()
    def _start_training_worker(self, base_model, dataset, new_model_name, args):
        success, response = self.api_client.start_training_job(base_model, dataset, new_model_name, args)
        self.after(0, self._on_job_started, success, response)
    def _on_job_started(self, success, response):
        if success:
            self.job_id = response.get('job_id')
            self.status_label.config(text=f"Status: Job {self.job_id} is QUEUED.")
            self._log_message(f"Training job successfully queued with ID: {self.job_id}")
            self._start_polling()
        else:
            messagebox.showerror("Job Error", f"Failed to start training job: {response}", parent=self)
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
        success, response = self.api_client.get_training_job_status(self.job_id)
        self.after(0, self._update_status_ui, success, response)
    def _update_status_ui(self, success, response):
        if success:
            status = response.get('status', 'UNKNOWN')
            message = response.get('message', '')
            progress = response.get('progress', 0)
            self.status_label.config(text=f"Status: {status}")
            self._log_message(f"Update: {message}")
            self.progress_bar['value'] = progress
            if status in ["COMPLETED", "FAILED"]:
                self.is_polling = False
                self.start_button.config(state="normal")
                messagebox.showinfo("Training Finished", f"Job {self.job_id} finished with status: {status}", parent=self)
                self._load_initial_data()
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
