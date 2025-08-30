#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\modules\image_viewer_module\processor.py
# JUMLAH BARIS : 122
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, filedialog
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
import os
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
class ImageViewerModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    Displays an image in a popup window from a local file path.
    The path can be provided dynamically from the payload or set manually.
    (MODIFIED) Now manages a single popup instance to prevent stacking.
    """
    TIER = "free"
    _active_popup = None
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        if not PIL_AVAILABLE:
            self.logger("FATAL: Pillow library is not installed. Image Viewer module will not work.", "CRITICAL") # English Log
    def _show_image_on_ui_thread(self, image_path):
        """
        (MODIFIED) This function now creates, manages, and tracks the single popup instance.
        """
        try:
            if ImageViewerModule._active_popup and ImageViewerModule._active_popup.winfo_exists():
                ImageViewerModule._active_popup.destroy()
                self.logger("An existing image viewer popup was found and automatically closed.", "INFO")
            popup = ttk.Toplevel(title=f"Image Viewer - {os.path.basename(image_path)}")
            img = Image.open(image_path)
            max_width = self.kernel.root.winfo_screenwidth() * 0.8
            max_height = self.kernel.root.winfo_screenheight() * 0.8
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            popup.photo = ImageTk.PhotoImage(img)
            img_label = ttk.Label(popup, image=popup.photo)
            img_label.pack(padx=10, pady=10)
            ImageViewerModule._active_popup = popup
            def _on_popup_close():
                self.logger("Image viewer was closed manually by the user.", "DEBUG")
                ImageViewerModule._active_popup = None # Forget the popup
                popup.destroy()
            popup.protocol("WM_DELETE_WINDOW", _on_popup_close)
            popup.transient()
            popup.grab_set()
            popup.wait_window()
        except Exception as e:
            self.logger(f"Failed to display image in popup: {e}", "ERROR") # English Log
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not PIL_AVAILABLE:
            raise RuntimeError("Pillow library is required. Please install it using: pip install Pillow")
        path_mode = config.get('path_mode', 'dynamic')
        image_path = ""
        if path_mode == 'dynamic':
            variable_key = config.get('image_path_variable', 'data.image_path')
            image_path = get_nested_value(payload, variable_key)
            if not image_path:
                raise ValueError(f"Could not find a valid image path in payload at '{variable_key}'")
        else: # manual mode
            image_path = config.get('manual_image_path', '')
            if not image_path:
                raise ValueError("Manual image path is not set in the node properties.")
        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            raise FileNotFoundError(f"The specified image file does not exist: {image_path}")
        status_updater(f"Displaying image: {os.path.basename(image_path)}", "INFO") # English Log
        ui_callback(self._show_image_on_ui_thread, image_path)
        status_updater("Image display complete", "SUCCESS") # English Log
        if 'data' not in payload: payload['data'] = {}
        payload['data']['image_path'] = image_path
        return {"payload": payload, "output_name": "success"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        source_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_image_source_mode_label'))
        source_frame.pack(fill='x', padx=5, pady=10)
        property_vars['path_mode'] = StringVar(value=config.get('path_mode', 'dynamic'))
        dynamic_frame = ttk.Frame(source_frame)
        manual_frame = ttk.Frame(source_frame)
        def _toggle_source_mode():
            if property_vars['path_mode'].get() == 'dynamic':
                manual_frame.pack_forget()
                dynamic_frame.pack(fill='x', padx=10, pady=5)
            else:
                dynamic_frame.pack_forget()
                manual_frame.pack(fill='x', padx=10, pady=5)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_dynamic'), variable=property_vars['path_mode'], value='dynamic', command=_toggle_source_mode).pack(anchor='w', padx=10)
        ttk.Radiobutton(source_frame, text=self.loc.get('prop_mode_manual'), variable=property_vars['path_mode'], value='manual', command=_toggle_source_mode).pack(anchor='w', padx=10)
        property_vars['image_path_variable'] = StringVar(value=config.get('image_path_variable', 'data.image_path'))
        LabelledCombobox(
            parent=dynamic_frame,
            label_text=self.loc.get('prop_image_path_variable_label'),
            variable=property_vars['image_path_variable'],
            values=list(available_vars.keys())
        )
        property_vars['manual_image_path'] = StringVar(value=config.get('manual_image_path', ''))
        ttk.Label(manual_frame, text=self.loc.get('prop_manual_image_path_label')).pack(anchor='w')
        entry_frame = ttk.Frame(manual_frame)
        entry_frame.pack(fill='x', expand=True, pady=(2,0))
        ttk.Entry(entry_frame, textvariable=property_vars['manual_image_path']).pack(side='left', fill='x', expand=True)
        def _browse_file():
            filepath = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")])
            if filepath:
                property_vars['manual_image_path'].set(filepath)
        ttk.Button(entry_frame, text="...", command=_browse_file, width=4).pack(side='left', padx=(5,0))
        _toggle_source_mode()
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'Will display an image from the provided path.'}]
