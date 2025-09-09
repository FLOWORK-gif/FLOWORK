#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\image_viewer_module\processor.py
# JUMLAH BARIS : 134
#######################################################################

from flowork_kernel.core import build_security
from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import StringVar, Toplevel, messagebox, filedialog
import os
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
class ImageViewerModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    Displays an image in a popup window from a local file path.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
        self._active_popups = {} # (ADDED) Maps node_id to its active popup window.
        if not PIL_AVAILABLE:
            self.logger("FATAL: Pillow library is not installed for Image Viewer.", "CRITICAL") # English Log
    def _show_image_popup(self, node_instance_id, image_path):
        """Helper function to show the image in a Toplevel window, now aware of the node ID."""
        if node_instance_id in self._active_popups and self._active_popups[node_instance_id].winfo_exists():
            self._active_popups[node_instance_id].destroy()
            self.logger("An existing image viewer popup for this node was found and automatically closed.", "INFO") # English Log
        popup = Toplevel()
        popup.title(f"Image Preview: {os.path.basename(image_path)}")
        try:
            img = Image.open(image_path)
            max_size = (800, 600)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = ttk.Label(popup, image=photo)
            label.image = photo # Keep a reference!
            label.pack()
        except Exception as e:
            ttk.Label(popup, text=f"Failed to load image: {e}").pack(padx=20, pady=20)
        self._active_popups[node_instance_id] = popup
        def _on_close():
            self.logger("Image viewer was closed manually by the user.", "DEBUG") # English Log
            if node_instance_id in self._active_popups:
                del self._active_popups[node_instance_id]
            popup.destroy()
        popup.protocol("WM_DELETE_WINDOW", _on_close)
        popup.transient()
        popup.grab_set()
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        node_instance_id = config.get('__internal_node_id', self.module_id)
        if not PIL_AVAILABLE:
            error_msg = "Required library (Pillow) is not installed."
            status_updater(error_msg, "ERROR") # English Log
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        path_mode = config.get('path_mode', 'dynamic')
        image_path = ""
        variable_path = "" # For better error messages
        if path_mode == 'dynamic':
            variable_path = config.get('image_path_variable', 'data.image_path')
            image_path = get_nested_value(payload, variable_path)
        else: # manual
            image_path = config.get('manual_image_path', '')
        if not image_path or not isinstance(image_path, str):
            error_msg = f"Could not find a valid image path in payload at '{variable_path}'"
            status_updater(error_msg, "ERROR") # English Log
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        if not os.path.exists(image_path):
            error_msg = f"Image file does not exist at path: {image_path}"
            status_updater(error_msg, "ERROR") # English Log
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        status_updater(f"Displaying image: {os.path.basename(image_path)}", "INFO") # English Log
        ui_callback(self._show_image_popup, node_instance_id, image_path)
        status_updater("Image display complete.", "SUCCESS") # English Log
        if 'data' not in payload or not isinstance(payload['data'], dict):
            payload['data'] = {}
        payload['data']['image_path'] = image_path
        return {"payload": payload, "output_name": "success"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        source_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_image_source_mode_label'))
        source_frame.pack(fill='x', padx=5, pady=10)
        property_vars['path_mode'] = StringVar(value=config.get('path_mode', 'dynamic'))
        manual_path_frame = ttk.Frame(source_frame)
        dynamic_path_frame = ttk.Frame(source_frame)
        def _toggle_path_source():
            if property_vars['path_mode'].get() == 'manual':
                manual_path_frame.pack(fill='x', padx=5, pady=5)
                dynamic_path_frame.pack_forget()
            else:
                manual_path_frame.pack_forget()
                dynamic_path_frame.pack(fill='x', padx=5, pady=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_manual'), variable=property_vars['path_mode'], value='manual', command=_toggle_path_source).pack(anchor='w', padx=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_dynamic'), variable=property_vars['path_mode'], value='dynamic', command=_toggle_path_source).pack(anchor='w', padx=5)
        ttk.Label(manual_path_frame, text=self.loc.get('prop_manual_image_path_label')).pack(fill='x')
        manual_entry_frame = ttk.Frame(manual_path_frame)
        manual_entry_frame.pack(fill='x', expand=True)
        property_vars['manual_image_path'] = StringVar(value=config.get('manual_image_path', ''))
        ttk.Entry(manual_entry_frame, textvariable=property_vars['manual_image_path']).pack(side='left', fill='x', expand=True)
        def _browse_file():
            path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")])
            if path:
                property_vars['manual_image_path'].set(path)
        ttk.Button(manual_entry_frame, text="...", command=_browse_file, width=4).pack(side='left', padx=(5,0))
        property_vars['image_path_variable'] = StringVar(value=config.get('image_path_variable', 'data.image_path'))
        LabelledCombobox(
            parent=dynamic_path_frame,
            label_text=self.loc.get('prop_image_path_variable_label'),
            variable=property_vars['image_path_variable'],
            values=list(available_vars.keys())
        )
        _toggle_path_source()
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Displays a live image from a path.'}]
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
_UNUSED_SIGNATURE = 'AOLA_FLOWORK_OFFICIAL_BUILD_2025_TEETAH_ART' # Embedded Signature
