#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\Dynamic Media Stitcher\processor.py
# JUMLAH BARIS : 410
#######################################################################

import os
import sys
import subprocess
import json
import math
import time
import random
import ttkbootstrap as ttk
from tkinter import StringVar, filedialog, BooleanVar, IntVar, colorchooser, scrolledtext # ADDED scrolledtext
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema, EnumVarWrapper
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.utils.file_helper import sanitize_filename
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
import uuid
import re # ADDED: Import regex for advanced stripping
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
class DynamicMediaStitcherModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema):
    """
    (REMASTERED V6.4 - Final Stable) Intelligently stitches media and generates advanced subtitles.
    Robust deletion logic and explicit stream mapping for ffmpeg.
    """
    TIER = "architect"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.ffmpeg_path, self.ffprobe_path = self._find_ffmpeg_tools()
        self.whisper_model_cache = {}
        self.fonts_path = os.path.join(self.kernel.data_path, "fonts")
        os.makedirs(self.fonts_path, exist_ok=True)
        self.job_rows = []
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not self.ffmpeg_path or not self.ffprobe_path:
            return self.error_payload("FFmpeg or FFprobe is not available. This module cannot function.")
        job_list = config.get('job_list', [])
        if not job_list:
            raise ValueError("No job has been configured. Please add at least one folder pair.")
        duration_reference = config.get('duration_reference', 'audio')
        original_audio_mode = config.get('original_audio_mode', 'replace')
        original_audio_volume = config.get('original_audio_volume', 20)
        add_subtitles = config.get('add_subtitles', True)
        all_results = []
        total_videos_created = 0
        for i, job in enumerate(job_list):
            video_folder = job.get('video_folder')
            audio_folder = job.get('audio_folder')
            output_folder = job.get('output_folder')
            job_name = f"Job {i+1}"
            status_updater(f"Starting {job_name}: Source '{os.path.basename(video_folder)}'", "INFO")
            if not all([video_folder, audio_folder, output_folder]) or not all(map(os.path.isdir, [video_folder, audio_folder, output_folder])):
                self.logger(f"{job_name} skipped: One or more folders are invalid.", "WARN") # English Log
                all_results.append({'job': job, 'status': 'skipped', 'reason': 'Invalid folder path(s).'})
                continue
            video_files = sorted([os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))])
            audio_files = sorted([os.path.join(audio_folder, f) for f in os.listdir(audio_folder) if f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a'))])
            if not video_files or not audio_files:
                self.logger(f"{job_name} skipped: Source folder(s) are empty.", "WARN") # English Log
                all_results.append({'job': job, 'status': 'skipped', 'reason': 'Source folder(s) empty.'})
                continue
            if duration_reference == 'audio':
                for audio_idx, audio_path in enumerate(audio_files):
                    status_updater(f"Job {i+1} - Processing Audio {audio_idx+1}/{len(audio_files)}: {os.path.basename(audio_path)}", "INFO") # English Log
                    try:
                        master_duration = self._get_media_duration(audio_path)
                        if master_duration == 0:
                            self.logger(f"Could not get duration for audio {os.path.basename(audio_path)}, skipping.", "WARN") # English Log
                            continue
                        clips_to_stitch, _ = self._gather_clips_to_duration(video_files, master_duration)
                        if not clips_to_stitch:
                            self.logger(f"Not enough video clips to match audio duration for {os.path.basename(audio_path)}", "WARN") # English Log
                            continue
                        temp_video_path = os.path.join(self.kernel.data_path, f"temp_stitch_{uuid.uuid4()}.mp4")
                        self._run_ffmpeg_stitch_video_only(clips_to_stitch, temp_video_path, status_updater)
                        output_filename = f"{sanitize_filename(os.path.splitext(os.path.basename(audio_path))[0])}.mp4"
                        final_output_path = os.path.join(output_folder, output_filename)
                        self._merge_video_audio_and_subtitle(temp_video_path, audio_path, final_output_path, config, status_updater)
                        os.remove(temp_video_path) # Clean up temp file
                        total_videos_created += 1
                        all_results.append({'source_audio': audio_path, 'used_videos': clips_to_stitch, 'output': final_output_path})
                    except Exception as e:
                        self.logger(f"Error processing audio {os.path.basename(audio_path)}: {e}", "ERROR") # English Log
            else: # duration_reference == 'video'
                for video_idx, video_path in enumerate(video_files):
                    status_updater(f"Job {i+1} - Processing Video {video_idx+1}/{len(video_files)}: {os.path.basename(video_path)}", "INFO") # English Log
                    try:
                        master_duration = self._get_media_duration(video_path)
                        if master_duration == 0: continue
                        clips_to_stitch, _ = self._gather_clips_to_duration(audio_files, master_duration)
                        if not clips_to_stitch: continue
                        temp_audio_path = os.path.join(self.kernel.data_path, f"temp_audio_{uuid.uuid4()}.mp3")
                        self._run_ffmpeg_stitch_audio_only(clips_to_stitch, temp_audio_path, status_updater)
                        output_filename = f"{sanitize_filename(os.path.splitext(os.path.basename(video_path))[0])}.mp4"
                        final_output_path = os.path.join(output_folder, output_filename)
                        self._merge_video_audio_and_subtitle(video_path, temp_audio_path, final_output_path, config, status_updater, use_temp_audio=True)
                        os.remove(temp_audio_path) # Clean up temp file
                        total_videos_created += 1
                        all_results.append({'source_video': video_path, 'used_audios': clips_to_stitch, 'output': final_output_path})
                    except Exception as e:
                        self.logger(f"Error processing video {os.path.basename(video_path)}: {e}", "ERROR") # English Log
        status_updater(f"All jobs complete. Total videos created: {total_videos_created}.", "SUCCESS")
        if 'data' not in payload or not isinstance(payload['data'], dict):
            payload['data'] = {}
        payload['data']['stitcher_results'] = all_results
        payload['data']['total_videos_created'] = total_videos_created
        return {"payload": payload, "output_name": "success"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        self.job_rows = []
        jobs_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_stitcher_job_list_label'))
        jobs_frame.pack(fill='both', expand=True, padx=5, pady=10)
        self.rows_container = ttk.Frame(jobs_frame)
        self.rows_container.pack(fill="both", expand=True, pady=5)
        def _add_job_row(video_folder="", audio_folder="", output_folder=""):
            row_id = str(uuid.uuid4())
            row_frame = ttk.Frame(self.rows_container)
            row_frame.pack(fill='x', pady=4, expand=True)
            row_frame.columnconfigure(0, weight=1)
            row_frame.columnconfigure(1, weight=1)
            row_frame.columnconfigure(2, weight=1)
            def create_folder_input(parent, col, label_key, initial_value):
                folder_frame = ttk.Frame(parent)
                folder_frame.grid(row=0, column=col, sticky='ew', padx=(0, 10))
                folder_frame.columnconfigure(0, weight=1)
                folder_var = StringVar(value=initial_value)
                ttk.Label(folder_frame, text=self.loc.get(label_key)).pack(anchor='w')
                entry_frame = ttk.Frame(folder_frame)
                entry_frame.pack(fill='x', expand=True)
                ttk.Entry(entry_frame, textvariable=folder_var).pack(side='left', fill='x', expand=True)
                ttk.Button(entry_frame, text="...", width=3, command=lambda v=folder_var: v.set(filedialog.askdirectory() or v.get())).pack(side='left', padx=5)
                return folder_var
            video_var = create_folder_input(row_frame, 0, 'prop_stitcher_video_folder_header', video_folder)
            audio_var = create_folder_input(row_frame, 1, 'prop_stitcher_audio_folder_header', audio_folder)
            output_var = create_folder_input(row_frame, 2, 'prop_stitcher_output_folder_header', output_folder)
            delete_button = ttk.Button(row_frame, text="X", bootstyle="danger", width=2, command=lambda rid=row_id: _remove_row(rid))
            delete_button.grid(row=0, column=3, padx=(10, 0), sticky='s')
            self.job_rows.append({'id': row_id, 'frame': row_frame, 'video_var': video_var, 'audio_var': audio_var, 'output_var': output_var})
        def _remove_row(row_id):
            for i, row in enumerate(self.job_rows):
                if row['id'] == row_id:
                    row['frame'].destroy()
                    self.job_rows.pop(i)
                    break
        ttk.Button(jobs_frame, text=self.loc.get('prop_stitcher_add_job_button'), command=lambda: _add_job_row(), bootstyle="outline-success").pack(fill='x', pady=5)
        saved_jobs = config.get('job_list', [])
        if saved_jobs:
            for job in saved_jobs:
                _add_job_row(job.get('video_folder', ''), job.get('audio_folder', ''), job.get('output_folder', ''))
        class DynamicJobsVar:
            def __init__(self, rows_data):
                self.rows_data = rows_data
            def get(self):
                return [{'video_folder': r['video_var'].get(), 'audio_folder': r['audio_var'].get(), 'output_folder': r['output_var'].get()} for r in self.rows_data]
        property_vars['job_list'] = DynamicJobsVar(self.job_rows)
        settings_frame = ttk.LabelFrame(parent_frame, text="Advanced Settings")
        settings_frame.pack(fill='x', padx=5, pady=10, expand=True)
        duration_ref_map = { self.loc.get('duration_ref_audio'): "audio", self.loc.get('duration_ref_video'): "video" }
        duration_ref_display_var = StringVar()
        duration_ref_wrapper = EnumVarWrapper(duration_ref_display_var, duration_ref_map, {v: k for k, v in duration_ref_map.items()})
        duration_ref_wrapper.set(config.get('duration_reference', 'audio'))
        property_vars['duration_reference'] = duration_ref_wrapper
        LabelledCombobox(settings_frame, self.loc.get('prop_stitcher_duration_reference_label'), duration_ref_display_var, list(duration_ref_map.keys()))
        audio_mode_frame = ttk.Frame(settings_frame)
        audio_mode_frame.pack(fill='x', expand=True, pady=5)
        audio_mode_map = { self.loc.get('audio_mode_replace'): "replace", self.loc.get('audio_mode_merge'): "merge" }
        audio_mode_display_var = StringVar()
        audio_mode_wrapper = EnumVarWrapper(audio_mode_display_var, audio_mode_map, {v: k for k, v in audio_mode_map.items()})
        audio_mode_wrapper.set(config.get('original_audio_mode', 'replace'))
        property_vars['original_audio_mode'] = audio_mode_wrapper
        LabelledCombobox(audio_mode_frame, self.loc.get('prop_stitcher_original_audio_mode_label'), audio_mode_display_var, list(audio_mode_map.keys()))
        volume_frame = ttk.Frame(settings_frame)
        ttk.Label(volume_frame, text=self.loc.get('prop_stitcher_original_audio_volume_label')).pack(side='left', padx=(5,5))
        property_vars['original_audio_volume'] = IntVar(value=config.get('original_audio_volume', 20))
        ttk.Scale(volume_frame, from_=0, to=100, variable=property_vars['original_audio_volume']).pack(side='left', fill='x', expand=True)
        ttk.Label(volume_frame, textvariable=property_vars['original_audio_volume'], width=4).pack(side='left')
        def _toggle_volume_slider(*args):
            if audio_mode_display_var.get() == self.loc.get('audio_mode_merge'):
                volume_frame.pack(fill='x', pady=5)
            else:
                volume_frame.pack_forget()
        audio_mode_display_var.trace_add('write', _toggle_volume_slider)
        _toggle_volume_slider()
        subtitle_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_stitcher_subtitle_settings_label'))
        subtitle_frame.pack(fill='x', padx=5, pady=10, expand=True)
        property_vars['add_subtitles'] = BooleanVar(value=config.get('add_subtitles', True))
        ttk.Checkbutton(subtitle_frame, text=self.loc.get('prop_stitcher_add_subtitles_label'), variable=property_vars['add_subtitles']).pack(anchor='w', padx=10, pady=5)
        ttk.Label(subtitle_frame, text=self.loc.get('prop_stitcher_correction_dictionary_label', fallback="Correction Dictionary (salah: benar)")).pack(anchor='w', padx=10, pady=(5,2))
        correction_text = scrolledtext.ScrolledText(subtitle_frame, height=4, font=("Consolas", 9))
        correction_text.pack(fill="x", expand=True, padx=10, pady=(0, 10))
        correction_text.insert('1.0', config.get('correction_dictionary', 'flowwork: Flowork\nflo work: Flowork\nteeta: Teetah'))
        property_vars['correction_dictionary'] = correction_text
        property_vars['subtitle_model_size'] = StringVar(value=config.get('subtitle_model_size', 'base'))
        LabelledCombobox(subtitle_frame, self.loc.get('prop_stitcher_subtitle_model_size_label'), property_vars['subtitle_model_size'], ['tiny', 'base', 'small', 'medium', 'large-v3'])
        font_files = ["Default"] + [f for f in os.listdir(self.fonts_path) if f.lower().endswith(('.ttf', '.otf'))]
        property_vars['subtitle_font'] = StringVar(value=config.get('subtitle_font', 'Default'))
        LabelledCombobox(subtitle_frame, self.loc.get('prop_stitcher_subtitle_font_label'), property_vars['subtitle_font'], font_files)
        def create_color_picker(parent, label_key, config_key, default_color):
            color_frame = ttk.Frame(parent)
            color_frame.pack(fill='x', padx=5, pady=2)
            ttk.Label(color_frame, text=self.loc.get(label_key)).pack(side='left', padx=(5,10))
            color_var = StringVar(value=config.get(config_key, default_color))
            property_vars[config_key] = color_var
            color_swatch = ttk.Frame(color_frame, width=30, height=20, relief='solid', borderwidth=1)
            color_swatch.pack(side='left')
            color_swatch.config(style=f"{config_key}.TFrame")
            style = ttk.Style.get_instance()
            style.configure(f"{config_key}.TFrame", background=color_var.get())
            def pick_color():
                _, color_hex = colorchooser.askcolor(parent=parent_frame, initialcolor=color_var.get())
                if color_hex:
                    color_var.set(color_hex.upper())
                    style.configure(f"{config_key}.TFrame", background=color_hex.upper())
            ttk.Button(color_frame, text="...", command=pick_color, width=3).pack(side='left', padx=5)
        create_color_picker(subtitle_frame, 'prop_stitcher_subtitle_primary_color_label', 'subtitle_primary_color', '#FFFFFF')
        create_color_picker(subtitle_frame, 'prop_stitcher_subtitle_secondary_color_label', 'subtitle_secondary_color', '#FFFF00')
        font_style_frame = ttk.Frame(subtitle_frame)
        font_style_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(font_style_frame, text=self.loc.get('prop_stitcher_subtitle_font_size_label')).pack(side='left', padx=(5,5))
        property_vars['subtitle_font_size'] = IntVar(value=config.get('subtitle_font_size', 32))
        ttk.Entry(font_style_frame, textvariable=property_vars['subtitle_font_size'], width=5).pack(side='left')
        property_vars['subtitle_style'] = StringVar(value=config.get('subtitle_style', 'Outline'))
        LabelledCombobox(subtitle_frame, self.loc.get('prop_stitcher_subtitle_style_label'), property_vars['subtitle_style'], ["Default", "Outline", "Shadow"])
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
    def get_data_preview(self, config: dict):
        return [{'status': 'preview_not_available', 'reason': 'Stitching is a complex, live process.'}]
    def get_dynamic_output_schema(self, config):
        return self.manifest.get('output_schema', [])
    def error_payload(self, error_message: str):
        self.logger(error_message, "ERROR")
        return {"payload": {"data": {"error": error_message}}, "output_name": "error"}
    def _find_ffmpeg_tools(self):
        ffmpeg_executable = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
        ffprobe_executable = "ffprobe.exe" if os.name == 'nt' else "ffprobe"
        ffmpeg_path = os.path.join(self.kernel.project_root_path, "vendor", "ffmpeg", "bin", ffmpeg_executable)
        ffprobe_path = os.path.join(self.kernel.project_root_path, "vendor", "ffmpeg", "bin", ffprobe_executable)
        if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
            return ffmpeg_path, ffprobe_path
        return None, None
    def _get_media_duration(self, file_path):
        if not self.ffprobe_path: return 0.0
        command = [self.ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        result = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=creation_flags)
        return float(result.stdout.strip())
    def _get_video_dimensions(self, file_path):
        if not self.ffprobe_path: return 1920, 1080
        command = [self.ffprobe_path, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", file_path]
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        result = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=creation_flags)
        width, height = map(int, result.stdout.strip().split('x'))
        return width, height
    def _gather_clips_to_duration(self, available_clips, target_duration):
        if not available_clips:
            return [], 0
        clips_to_use = []
        current_duration = 0.0
        random.shuffle(available_clips)
        clip_pool = available_clips.copy()
        while current_duration < target_duration:
            if not clip_pool: # If we run out of unique clips, restart the pool
                clip_pool = available_clips.copy()
                random.shuffle(clip_pool)
            clip_path = clip_pool.pop(0)
            try:
                clip_duration = self._get_media_duration(clip_path)
                if clip_duration > 0:
                    clips_to_use.append(clip_path)
                    current_duration += clip_duration
                else:
                    self.logger(f"Warning: Could not get duration for clip {os.path.basename(clip_path)}, skipping it.", "WARN") # English Log
            except Exception as e:
                self.logger(f"Error getting duration for {os.path.basename(clip_path)}: {e}", "ERROR") # English Log
        return clips_to_use, current_duration
    def _run_ffmpeg_stitch_video_only(self, clip_list, output_path, status_updater):
        temp_list_path = os.path.join(self.kernel.data_path, f"concat_video_{uuid.uuid4()}.txt")
        try:
            with open(temp_list_path, 'w', encoding='utf-8') as f:
                for clip_path in clip_list:
                    f.write(f"file '{os.path.abspath(clip_path)}'\n")
            command = [
                self.ffmpeg_path, "-y", "-f", "concat", "-safe", "0", "-i", temp_list_path,
                "-c", "copy", output_path
            ]
            status_updater("Stitching video clips...", "INFO") # English Log
            subprocess.run(command, check=True, capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0))
        finally:
            if os.path.exists(temp_list_path):
                os.remove(temp_list_path)
    def _run_ffmpeg_stitch_audio_only(self, clip_list, output_path, status_updater):
        temp_list_path = os.path.join(self.kernel.data_path, f"concat_audio_{uuid.uuid4()}.txt")
        try:
            with open(temp_list_path, 'w', encoding='utf-8') as f:
                for clip_path in clip_list:
                    f.write(f"file '{os.path.abspath(clip_path)}'\n")
            command = [
                self.ffmpeg_path, "-y", "-f", "concat", "-safe", "0", "-i", temp_list_path,
                output_path
            ]
            status_updater("Stitching audio clips...", "INFO") # English Log
            subprocess.run(command, check=True, capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0))
        finally:
            if os.path.exists(temp_list_path):
                os.remove(temp_list_path)
    def _merge_video_audio_and_subtitle(self, video_input_path, audio_input_path, final_output_path, config, status_updater, use_temp_audio=False):
        video_filters = []
        w, h = self._get_video_dimensions(video_input_path)
        video_filters.append(f"scale={'1080:1920' if h > w else '1920:1080'},setsar=1")
        temp_files_to_clean = []
        if config.get('add_subtitles', True):
            subtitle_model_size = config.get('subtitle_model_size', 'base')
            model = self._get_whisper_model(subtitle_model_size, status_updater)
            subtitle_path = self._generate_ass_subtitle(audio_input_path, model, config, status_updater)
            if subtitle_path:
                temp_files_to_clean.append(subtitle_path)
                safe_subtitle_path = subtitle_path.replace('\\', '/').replace(':', '\\:')
                video_filters.append(f"subtitles='{safe_subtitle_path}'")
        command = [self.ffmpeg_path, "-y", "-i", video_input_path, "-i", audio_input_path, "-shortest"]
        audio_mode = config.get('original_audio_mode', 'replace')
        if audio_mode == 'merge' and not use_temp_audio:
            volume = int(config.get('original_audio_volume', 20)) / 100.0
            command.extend([
                "-filter_complex", f"[0:a]volume={volume}[a0];[1:a]volume=1[a1];[a0][a1]amerge=inputs=2[a]",
                "-map", "0:v:0", "-map", "[a]"
            ])
        else: # Replace mode or when using temporary stitched audio
            command.extend(["-map", "0:v:0", "-map", "1:a:0"])
        command.extend([
            "-vf", ",".join(video_filters),
            "-c:v", "libx264", "-c:a", "aac", "-r", "30",
            final_output_path
        ])
        try:
            status_updater(f"Merging final video: {os.path.basename(final_output_path)}...", "INFO") # English Log
            subprocess.run(command, check=True, capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0))
        finally:
            for temp_file in temp_files_to_clean:
                try:
                    if os.path.exists(temp_file): os.remove(temp_file)
                except Exception: pass
    def _get_whisper_model(self, model_size, status_updater):
        if model_size in self.whisper_model_cache:
            return self.whisper_model_cache[model_size]
        if not FASTER_WHISPER_AVAILABLE:
            raise RuntimeError("The 'faster-whisper' library is not required but not installed.")
        status_updater(f"Loading Whisper '{model_size}' model for the first time...", "INFO")
        self.logger(f"DynamicStitcher: Loading faster-whisper model '{model_size}'.", "WARN")
        model = WhisperModel(model_size, device="auto", compute_type="default")
        self.whisper_model_cache[model_size] = model
        return model
    def _hex_to_ass_color(self, hex_color, alpha='00'):
        hex_color = hex_color.lstrip('#')
        r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        return f"&H{alpha}{b}{g}{r}".upper()
    def _format_timedelta_to_ass_timestamp(self, total_seconds_float):
        if total_seconds_float < 0: total_seconds_float = 0
        total_seconds_int = int(total_seconds_float)
        fractional_seconds = total_seconds_float - total_seconds_int
        hours, remainder = divmod(total_seconds_int, 3600)
        minutes, seconds = divmod(remainder, 60)
        centiseconds = int(fractional_seconds * 100)
        return f"{hours:d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
    def _generate_ass_subtitle(self, audio_path, model, config, status_updater):
        effect_style = 'Karaoke' # config.get('subtitle_effect_style', 'Karaoke')
        status_updater(f"Transcribing for '{effect_style}' effect...", "INFO")
        segments, info = model.transcribe(audio_path, language='id', word_timestamps=True)
        correction_dict_str = config.get('correction_dictionary', '')
        correction_map = {}
        if correction_dict_str:
            for line in correction_dict_str.split('\n'):
                if ':' in line:
                    wrong, correct = line.split(':', 1)
                    correction_map[wrong.strip().lower()] = correct.strip()
        font_name = config.get('subtitle_font', 'Arial')
        if font_name == 'Default': font_name = 'Arial'
        font_size = config.get('subtitle_font_size', 32)
        primary_color = self._hex_to_ass_color(config.get('subtitle_primary_color', '#FFFFFF'))
        secondary_color = self._hex_to_ass_color(config.get('subtitle_secondary_color', '#FFFF00'))
        style_type = config.get('subtitle_style', 'Outline')
        outline_or_shadow = 1 if style_type != 'Default' else 0
        ass_content = ["[Script Info]", "Title: Generated by Flowork", "ScriptType: v4.00+", "WrapStyle: 0", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]", "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding", f"Style: Default,{font_name},{font_size},{primary_color},{secondary_color},&H00000000,&H00000000,0,0,0,0,100,100,0,0,{outline_or_shadow},{outline_or_shadow},{outline_or_shadow},2,10,10,10,1", "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
        for segment in segments:
            if not hasattr(segment, 'words'): continue
            dialogue_line = []
            for word in segment.words:
                clean_word = re.sub(r'^\W+|\W+$', '', word.word.strip())
                corrected_word = correction_map.get(clean_word.lower(), word.word)
                k_duration = int((word.end - word.start) * 100)
                dialogue_line.append(f"{{\\k{k_duration}}}{corrected_word}")
            start_time = self._format_timedelta_to_ass_timestamp(segment.start)
            end_time = self._format_timedelta_to_ass_timestamp(segment.end)
            ass_content.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{''.join(dialogue_line)}")
        ass_filename = os.path.splitext(os.path.basename(audio_path))[0] + ".ass"
        temp_ass_path = os.path.join(self.kernel.data_path, ass_filename)
        with open(temp_ass_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ass_content))
        status_updater("Transcription complete, ASS file generated.", "INFO") # English Log
        return temp_ass_path
