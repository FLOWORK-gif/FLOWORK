#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\video_uniquifier_module_d4e5\processor.py
# JUMLAH BARIS : 148
#######################################################################

from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.file_helper import sanitize_filename
import os
import random
import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar, IntVar, DoubleVar, filedialog
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
class VideoUniquifierModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    Module to apply random visual modifications to a batch of videos to make them unique.
    """
    TIER = "basic"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.LIBRARIES_AVAILABLE = False
        try:
            global mp, crop, mirror_x, colorx, np
            import moviepy.editor as mp
            from moviepy.video.fx.all import crop, mirror_x, colorx
            import numpy as np
            self.LIBRARIES_AVAILABLE = True
        except ImportError:
            self.logger("CRITICAL: 'moviepy' and 'numpy' libraries are required for the Video Uniquifier module but are not installed.", "CRITICAL")
            self.logger("This may be because the 'vendor' folder is missing or the installation failed during startup.", "CRITICAL")
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not self.LIBRARIES_AVAILABLE:
            raise ImportError("Required libraries (moviepy, numpy) are not installed for this module.")
        status_updater("Reading configuration...", "INFO")
        source_folder = config.get('source_folder')
        output_folder = config.get('output_folder')
        enable_crop = config.get('enable_crop', True)
        crop_px = int(config.get('crop_amount_px', 2))
        enable_color = config.get('enable_color_change', True)
        color_var = int(config.get('color_variation_percent', 1)) / 100.0
        enable_flip = config.get('enable_flip', True)
        enable_noise = config.get('enable_noise', True)
        noise_amount = float(config.get('noise_amount', 0.02))
        output_format = config.get('output_format', 'mp4')
        if not source_folder or not os.path.isdir(source_folder):
            raise FileNotFoundError(f"Source folder not found or is not a valid directory: {source_folder}")
        if not output_folder:
            output_folder = os.path.join(source_folder, "uniquified_output")
            self.logger(f"Output folder not specified. Defaulting to: {output_folder}", "WARN")
        os.makedirs(output_folder, exist_ok=True)
        video_files = [f for f in os.listdir(source_folder) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        total_files = len(video_files)
        processed_files = []
        self.logger(f"Starting to process {total_files} videos from '{os.path.basename(source_folder)}'.", "INFO")
        for i, filename in enumerate(video_files):
            input_path = os.path.join(source_folder, filename)
            sanitized_name = sanitize_filename(os.path.splitext(filename)[0])
            output_path = os.path.join(output_folder, f"{sanitized_name}_unique.{output_format}")
            status_updater(f"Processing ({i+1}/{total_files}): {filename}", "INFO")
            try:
                clip = mp.VideoFileClip(input_path)
                if enable_crop and clip.w > crop_px * 2 and clip.h > crop_px * 2:
                    clip = crop(clip, x1=crop_px, y1=crop_px, x2=clip.w - crop_px, y2=clip.h - crop_px)
                if enable_color:
                    color_factor = 1.0 + random.uniform(-color_var, color_var)
                    clip = colorx(clip, factor=color_factor)
                if enable_flip and random.choice([True, False]): # 50% chance to flip
                    clip = mirror_x(clip)
                if enable_noise and noise_amount > 0:
                    def add_noise_effect(frame):
                        noise = np.random.randint(-int(noise_amount * 255), int(noise_amount * 255), frame.shape, dtype=np.int16)
                        return np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
                    clip = clip.fl_image(add_noise_effect)
                clip.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
                processed_files.append(output_path)
                clip.close()
            except Exception as e:
                self.logger(f"Failed to process {filename}. Error: {e}", "ERROR")
                if 'clip' in locals() and clip:
                    clip.close()
                continue
        status_updater(f"Processing complete. {len(processed_files)} videos saved.", "SUCCESS")
        if 'data' not in payload or not isinstance(payload['data'], dict):
            payload['data'] = {}
        payload['data']['processed_files'] = processed_files
        payload['data']['total_processed'] = len(processed_files)
        return {"payload": payload, "output_name": "success"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        folder_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_folders_title'))
        folder_frame.pack(fill='x', padx=5, pady=10, expand=True)
        ttk.Label(folder_frame, text=self.loc.get('prop_source_folder_label')).pack(anchor='w', padx=5, pady=(5,0))
        source_path_frame = ttk.Frame(folder_frame)
        source_path_frame.pack(fill='x', expand=True, padx=5, pady=(0,5))
        property_vars['source_folder'] = StringVar(value=config.get('source_folder', ''))
        ttk.Entry(source_path_frame, textvariable=property_vars['source_folder']).pack(side='left', fill='x', expand=True)
        ttk.Button(source_path_frame, text="...", width=4, command=lambda: property_vars['source_folder'].set(filedialog.askdirectory() or property_vars['source_folder'].get())).pack(side='left', padx=(5,0))
        ttk.Label(folder_frame, text=self.loc.get('prop_output_folder_label')).pack(anchor='w', padx=5, pady=(5,0))
        output_path_frame = ttk.Frame(folder_frame)
        output_path_frame.pack(fill='x', expand=True, padx=5, pady=(0,5))
        property_vars['output_folder'] = StringVar(value=config.get('output_folder', ''))
        ttk.Entry(output_path_frame, textvariable=property_vars['output_folder']).pack(side='left', fill='x', expand=True)
        ttk.Button(output_path_frame, text="...", width=4, command=lambda: property_vars['output_folder'].set(filedialog.askdirectory() or property_vars['output_folder'].get())).pack(side='left', padx=(5,0))
        mods_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_mods_title'))
        mods_frame.pack(fill='x', padx=5, pady=10, expand=True)
        property_vars['enable_crop'] = BooleanVar(value=config.get('enable_crop', True))
        crop_frame = ttk.Frame(mods_frame)
        crop_frame.pack(fill='x', padx=5, pady=5)
        ttk.Checkbutton(crop_frame, text=self.loc.get('prop_enable_crop_label'), variable=property_vars['enable_crop']).pack(side='left')
        property_vars['crop_amount_px'] = IntVar(value=config.get('crop_amount_px', 2))
        crop_entry = ttk.Entry(crop_frame, textvariable=property_vars['crop_amount_px'], width=5)
        crop_entry.pack(side='left', padx=10)
        ttk.Label(crop_frame, text=self.loc.get('prop_pixels_label')).pack(side='left')
        property_vars['enable_color_change'] = BooleanVar(value=config.get('enable_color_change', True))
        color_frame = ttk.Frame(mods_frame)
        color_frame.pack(fill='x', padx=5, pady=5)
        ttk.Checkbutton(color_frame, text=self.loc.get('prop_enable_color_label'), variable=property_vars['enable_color_change']).pack(side='left')
        property_vars['color_variation_percent'] = IntVar(value=config.get('color_variation_percent', 1))
        color_entry = ttk.Entry(color_frame, textvariable=property_vars['color_variation_percent'], width=5)
        color_entry.pack(side='left', padx=10)
        ttk.Label(color_frame, text="%").pack(side='left')
        property_vars['enable_flip'] = BooleanVar(value=config.get('enable_flip', True))
        ttk.Checkbutton(mods_frame, text=self.loc.get('prop_enable_flip_label'), variable=property_vars['enable_flip']).pack(anchor='w', padx=5, pady=5)
        property_vars['enable_noise'] = BooleanVar(value=config.get('enable_noise', True))
        noise_frame = ttk.Frame(mods_frame)
        noise_frame.pack(fill='x', padx=5, pady=5)
        ttk.Checkbutton(noise_frame, text=self.loc.get('prop_enable_noise_label'), variable=property_vars['enable_noise']).pack(side='left')
        property_vars['noise_amount'] = DoubleVar(value=config.get('noise_amount', 0.02))
        noise_entry = ttk.Entry(noise_frame, textvariable=property_vars['noise_amount'], width=5)
        noise_entry.pack(side='left', padx=10)
        output_opts_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_output_opts_title'))
        output_opts_frame.pack(fill='x', padx=5, pady=10, expand=True)
        property_vars['output_format'] = StringVar(value=config.get('output_format', 'mp4'))
        LabelledCombobox(
            parent=output_opts_frame,
            label_text=self.loc.get('prop_output_format_label'),
            variable=property_vars['output_format'],
            values=['mp4', 'mov']
        )
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Video processing is a heavy operation.'}]
