#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\widgets\dataset_manager_widget\dataset_manager_widget.py
# JUMLAH BARIS : 159
#######################################################################

import ttkbootstrap as ttk
from tkinter import simpledialog, messagebox
from tkinter.scrolledtext import ScrolledText
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_kernel.api_client import ApiClient
import threading
class DatasetManagerWidget(BaseDashboardWidget):
    """
    Provides a UI for managing fine-tuning datasets by communicating with the backend API.
    [UPGRADED] Now loads and displays existing data when a dataset is selected.
    """
    TIER = "pro"
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str, refresh_callback=None):
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.api_client = ApiClient(kernel=self.kernel)
        self.dataset_var = ttk.StringVar()
        self.refresh_callback = refresh_callback
        self._build_ui()
    def on_widget_load(self):
        """Load datasets when the widget appears."""
        self._load_datasets()
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        selection_frame = ttk.Frame(self)
        selection_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        selection_frame.columnconfigure(0, weight=1)
        self.dataset_combo = ttk.Combobox(selection_frame, textvariable=self.dataset_var, state="readonly")
        self.dataset_combo.grid(row=0, column=0, sticky="ew")
        self.dataset_combo.bind("<<ComboboxSelected>>", self._on_dataset_selected)
        button_toolbar = ttk.Frame(selection_frame)
        button_toolbar.grid(row=0, column=1, padx=(5,0))
        create_button = ttk.Button(button_toolbar, text="Create", command=self._create_new_dataset, bootstyle="outline-success", width=7)
        create_button.pack(side="left")
        self.delete_button = ttk.Button(button_toolbar, text="Delete", command=self._delete_selected_dataset, bootstyle="outline-danger", width=7)
        self.delete_button.pack(side="left", padx=(5,0))
        self.input_frame = ttk.LabelFrame(self, text="Add or Edit Data (prompt;response per line)")
        self.input_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.input_frame.rowconfigure(0, weight=1)
        self.input_frame.columnconfigure(0, weight=1)
        self.data_input_text = ScrolledText(self.input_frame, wrap="word", height=8)
        self.data_input_text.grid(row=0, column=0, sticky="nsew")
        self.save_button = ttk.Button(self, text="Save Data to Selected Dataset", command=self._save_data_to_dataset, bootstyle="primary")
        self.save_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.rowconfigure(1, weight=1)
    def _load_datasets(self):
        self.dataset_combo['values'] = ["Loading..."]
        self.dataset_var.set("Loading...")
        threading.Thread(target=self._load_datasets_worker, daemon=True).start()
    def _load_datasets_worker(self):
        success, response = self.api_client.list_datasets()
        self.after(0, self._populate_dataset_combo, success, response)
    def _populate_dataset_combo(self, success, response):
        if success:
            dataset_names = [ds['name'] for ds in response]
            self.dataset_combo['values'] = sorted(dataset_names)
            if dataset_names:
                self.dataset_var.set(sorted(dataset_names)[0])
                self._on_dataset_selected()
            else:
                self.dataset_var.set("No datasets found. Please create one.")
                self.data_input_text.config(state="normal")
                self.data_input_text.delete("1.0", "end")
                self.data_input_text.config(state="disabled")
        else:
            self.dataset_combo['values'] = ["Error loading datasets"]
            self.dataset_var.set("Error loading datasets")
            self.kernel.write_to_log(f"Failed to load datasets: {response}", "ERROR")
    def _on_dataset_selected(self, event=None):
        selected_dataset = self.dataset_var.get()
        if not selected_dataset or "Loading" in selected_dataset or "Error" in selected_dataset or "No datasets" in selected_dataset:
            return
        self.data_input_text.config(state="normal")
        self.data_input_text.delete("1.0", "end")
        self.data_input_text.insert("1.0", f"Loading data for '{selected_dataset}'...")
        self.data_input_text.config(state="disabled")
        threading.Thread(target=self._load_dataset_content_worker, args=(selected_dataset,), daemon=True).start()
    def _load_dataset_content_worker(self, dataset_name):
        success, data = self.api_client.get_dataset_data(dataset_name)
        self.after(0, self._populate_data_text_area, success, data, dataset_name)
    def _populate_data_text_area(self, success, data, dataset_name):
        self.data_input_text.config(state="normal")
        self.data_input_text.delete("1.0", "end")
        if success:
            formatted_text = ""
            for item in data:
                formatted_text += f"{item.get('prompt', '')};{item.get('response', '')}\n"
            self.data_input_text.insert("1.0", formatted_text)
            self.input_frame.config(text=f"Data for '{dataset_name}' ({len(data)} records)")
        else:
            self.data_input_text.insert("1.0", f"Error loading data for '{dataset_name}'.")
            self.kernel.write_to_log(f"Failed to load content for dataset '{dataset_name}': {data}", "ERROR")
    def _create_new_dataset(self):
        new_name = simpledialog.askstring("Create Dataset", "Enter a name for the new dataset:", parent=self)
        if new_name and new_name.strip():
            success, response = self.api_client.create_dataset(new_name.strip())
            if success:
                self.kernel.write_to_log(f"Successfully created dataset: {new_name}", "SUCCESS")
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Error", f"Failed to create dataset: {response}", parent=self)
        else:
            self.kernel.write_to_log("Dataset creation cancelled.", "WARN")
    def _delete_selected_dataset(self):
        selected_dataset = self.dataset_var.get()
        if not selected_dataset or "Loading" in selected_dataset or "Error" in selected_dataset or "No datasets" in selected_dataset:
            messagebox.showerror("Error", "Please select a valid dataset to delete.", parent=self)
            return
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete the dataset '{selected_dataset}'?", parent=self):
            self.delete_button.config(state="disabled", text="Deleting...")
            threading.Thread(target=self._delete_dataset_worker, args=(selected_dataset,), daemon=True).start()
    def _delete_dataset_worker(self, dataset_name):
        success, response = self.api_client.delete_dataset(dataset_name)
        self.after(0, self._on_delete_complete, success, response, dataset_name)
    def _on_delete_complete(self, success, response, dataset_name):
        self.delete_button.config(state="normal", text="Delete")
        if success:
            messagebox.showinfo("Success", f"Dataset '{dataset_name}' has been deleted.", parent=self)
            if self.refresh_callback:
                self.refresh_callback()
        else:
            messagebox.showerror("Error", f"Failed to delete dataset: {response}", parent=self)
    def _save_data_to_dataset(self):
        selected_dataset = self.dataset_var.get()
        data_to_add = self.data_input_text.get("1.0", "end-1c").strip()
        if not selected_dataset or "Loading" in selected_dataset or "Error" in selected_dataset or "No datasets" in selected_dataset:
            messagebox.showerror("Error", "Please select or create a valid dataset first.", parent=self)
            return
        if not data_to_add:
            messagebox.showerror("Error", "The data input area is empty.", parent=self)
            return
        parsed_data = []
        for i, line in enumerate(data_to_add.split('\n')):
            if not line.strip(): continue
            if ';' not in line:
                messagebox.showerror("Error", f"Invalid format on line {i+1}: '{line}'. Each line must be 'prompt;response'.", parent=self)
                return
            prompt, response = line.split(';', 1)
            parsed_data.append({"prompt": prompt.strip(), "response": response.strip()})
        self.save_button.config(state="disabled", text="Saving...")
        threading.Thread(target=self._save_data_worker, args=(selected_dataset, parsed_data), daemon=True).start()
    def _save_data_worker(self, dataset_name, data):
        success, response = self.api_client.add_data_to_dataset(dataset_name, data)
        self.after(0, self._on_save_data_complete, success, response, len(data), dataset_name)
    def _on_save_data_complete(self, success, response, count, dataset_name):
        self.save_button.config(state="normal", text="Save Data to Selected Dataset")
        if success:
            messagebox.showinfo("Success", f"{count} records have been successfully saved to dataset '{dataset_name}'.", parent=self)
            if self.refresh_callback:
                self.refresh_callback()
        else:
            messagebox.showerror("Error", f"Failed to save data: {response}", parent=self)
