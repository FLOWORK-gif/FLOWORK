#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\video_storyboard_stitcher_d5e6\processor.py
# JUMLAH BARIS : 305
#######################################################################

import os
import sys
import subprocess
import ttkbootstrap as ttk
from tkinter import StringVar, filedialog, BooleanVar, IntVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, EnumVarWrapper
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.file_helper import sanitize_filename
import random
import uuid
import json
class VideoStoryboardStitcherModule(BaseModule, IExecutable, IConfigurableUI):
    TIER = "architect"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.ffmpeg_path = self._find_ffmpeg()
        self.section_counter = 0
    def _find_ffmpeg(self):
        ffmpeg_executable = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
        path = os.path.join(self.kernel.project_root_path, "vendor", "ffmpeg", "bin", ffmpeg_executable)
        if os.path.exists(path):
            return path
        return None
    def _run_ffmpeg_stitch(self, clip_list, output_path, status_updater, music_path=None, music_volume_percent=20, original_audio_mode='replace', original_audio_volume=20): # ADDED: new parameters
        temp_list_path = os.path.join(self.kernel.data_path, f"concat_{uuid.uuid4()}.txt")
        with open(temp_list_path, 'w', encoding='utf-8') as f:
            for clip_path in clip_list:
                f.write(f"file '{os.path.abspath(clip_path)}'\n")
        command = [self.ffmpeg_path, "-y", "-f", "concat", "-safe", "0", "-i", temp_list_path]
        audio_filter_command = []
        if music_path and os.path.exists(music_path):
            status_updater("Adding background music...", "INFO") # English Log
            command.extend(["-i", music_path]) # MODIFICATION: Changed stream_loop to input
            if original_audio_mode == 'merge':
                self.logger("Audio mode: Merge", "DEBUG") # English Log
                original_vol = int(original_audio_volume) / 100.0
                music_vol = int(music_volume_percent) / 100.0
                filter_complex = f"[0:a]volume={original_vol}[a_orig]; [1:a]volume={music_vol}[a_music]; [a_orig][a_music]amix=inputs=2:duration=longest[a_out]"
                command.extend([
                    "-filter_complex", filter_complex,
                    "-map", "0:v:0", "-map", "[a_out]",
                    "-shortest"
                ])
            else: # Default to 'replace'
                self.logger("Audio mode: Replace", "DEBUG") # English Log
                command.extend(["-map", "0:v:0", "-map", "1:a:0"])
                command.extend(["-shortest"])
                try:
                    volume_level = int(music_volume_percent) / 100.0
                    if volume_level > 0 and volume_level != 1.0: # Only add filter if not default 100%
                        audio_filter_command = ["-af", f"volume={volume_level}"]
                except (ValueError, TypeError):
                    self.logger(f"Invalid music volume '{music_volume_percent}'. Using default.", "WARN") # English Log
        else:
            command.extend(["-map", "0:v:0", "-map", "0:a?"])
        base_command_end = [
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-c:a", "aac", "-r", "30", output_path
        ]
        command.extend(audio_filter_command)
        command.extend(base_command_end)
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            result = subprocess.run(command, check=True, capture_output=True, text=True, creationflags=creation_flags)
            self.logger(f"FFmpeg STDOUT: {result.stdout}", "DEBUG") # English Log
            self.logger(f"FFmpeg STDERR: {result.stderr}", "DEBUG") # English Log
        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(e.returncode, e.cmd, output=e.stdout, stderr=e.stderr)
        finally:
            if os.path.exists(temp_list_path):
                os.remove(temp_list_path)
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg is not available.")
        video_sections = config.get('video_sections', [])
        output_folder = config.get('output_folder')
        prefix = sanitize_filename(config.get('output_filename_prefix', 'storyboard'))
        generation_mode = config.get('generation_mode', 'match_largest')
        delete_after_use = config.get('delete_after_use', False)
        music_folder_path = config.get('music_folder_path')
        music_volume = config.get('music_volume_percent', 20)
        original_audio_mode = config.get('original_audio_mode', 'replace')
        original_audio_volume = config.get('original_audio_volume', 20)
        all_music_files = []
        if music_folder_path and os.path.isdir(music_folder_path):
            all_music_files = [os.path.join(music_folder_path, f) for f in os.listdir(music_folder_path) if f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a'))]
            if not all_music_files:
                self.logger(f"Music folder '{music_folder_path}' is provided but contains no valid audio files. Proceeding without music.", "WARN") # English Log
        if not video_sections: raise ValueError("No video sections configured.")
        if not output_folder or not os.path.isdir(output_folder): raise FileNotFoundError(f"Output folder is invalid: {output_folder}")
        if generation_mode == 'match_largest':
            if delete_after_use:
                self.logger("'Delete after use' is incompatible with 'Maximize Quantity' mode and will be ignored.", "WARN") # English Log
            result_payload = self._execute_match_largest(video_sections, output_folder, prefix, all_music_files, music_volume, original_audio_mode, original_audio_volume, status_updater) # MODIFIED: Pass music list
        else: # limit_by_smallest
            result_payload = self._execute_limit_by_smallest(video_sections, output_folder, prefix, delete_after_use, all_music_files, music_volume, original_audio_mode, original_audio_volume, status_updater) # MODIFIED: Pass music list
        if 'data' not in payload: payload['data'] = {}
        payload['data'].update(result_payload)
        return {"payload": payload, "output_name": "success"}
    def _execute_limit_by_smallest(self, sections, output_folder, prefix, delete_after_use, music_files_list, music_volume, original_audio_mode, original_audio_volume, status_updater): # MODIFIED: Accept music list
        section_clip_pools = []
        min_clips = float('inf')
        for section in sections:
            path = section.get('path')
            if not path or not os.path.isdir(path): raise FileNotFoundError(f"Folder for section '{section.get('name')}' not found.")
            clips = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(('.mp4', '.mov'))]
            if not clips: raise ValueError(f"Folder for section '{section.get('name')}' is empty.")
            random.shuffle(clips)
            section_clip_pools.append(clips)
            min_clips = min(min_clips, len(clips))
        status_updater(f"Found {min_clips} possible unique videos (limited by smallest folder).", "INFO")
        all_stitched_videos = []
        for i in range(min_clips):
            status_updater(f"Generating video {i+1}/{min_clips}...", "INFO")
            clips_for_this_video = []
            for clip_pool in section_clip_pools:
                clip = clip_pool.pop(0)
                clips_for_this_video.append(clip)
            selected_music = random.choice(music_files_list) if music_files_list else None
            output_filename = f"{prefix}_{i+1:03d}.mp4"
            output_path = os.path.normpath(os.path.join(output_folder, output_filename))
            self._run_ffmpeg_stitch(clips_for_this_video, output_path, status_updater, music_path=selected_music, music_volume_percent=music_volume, original_audio_mode=original_audio_mode, original_audio_volume=original_audio_volume) # ADDED PARAMS
            all_stitched_videos.append(output_path)
            if delete_after_use:
                for clip_path in clips_for_this_video:
                    try:
                        os.remove(clip_path)
                        self.logger(f"Deleted used clip: {os.path.basename(clip_path)}", "INFO") # English Log
                    except OSError as e:
                        self.logger(f"Failed to delete {clip_path}: {e}", "ERROR") # English Log
        return {"stitched_video_paths": all_stitched_videos}
    def _execute_match_largest(self, sections, output_folder, prefix, music_files_list, music_volume, original_audio_mode, original_audio_volume, status_updater): # MODIFIED: Accept music list
        pools = {}
        max_clips = 0
        for section in sections:
            path = section.get('path')
            if not path or not os.path.isdir(path): raise FileNotFoundError(f"Folder for section '{section.get('name')}' not found.")
            clips = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(('.mp4', '.mov'))]
            if not clips: raise ValueError(f"Folder for section '{section.get('name')}' is empty.")
            pools[section['name']] = {'original': clips, 'current': clips.copy()}
            random.shuffle(pools[section['name']]['current'])
            max_clips = max(max_clips, len(clips))
        status_updater(f"Will generate {max_clips} videos (matching largest folder).", "INFO")
        all_stitched_videos = []
        for i in range(max_clips):
            status_updater(f"Generating video {i+1}/{max_clips}...", "INFO")
            clips_for_this_video = []
            for section in sections:
                section_pool = pools[section['name']]
                if not section_pool['current']:
                    self.logger(f"Refilling pool for section '{section['name']}'.", "DEBUG") # English Log
                    section_pool['current'] = section_pool['original'].copy()
                    random.shuffle(section_pool['current'])
                clip = section_pool['current'].pop(0)
                clips_for_this_video.append(clip)
            selected_music = random.choice(music_files_list) if music_files_list else None
            output_filename = f"{prefix}_{i+1:03d}.mp4"
            output_path = os.path.normpath(os.path.join(output_folder, output_filename))
            self._run_ffmpeg_stitch(clips_for_this_video, output_path, status_updater, music_path=selected_music, music_volume_percent=music_volume, original_audio_mode=original_audio_mode, original_audio_volume=original_audio_volume) # ADDED PARAMS
            all_stitched_videos.append(output_path)
        return {"stitched_video_paths": all_stitched_videos}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        self.section_rows = []
        self.section_counter = 0
        output_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_storyboard_output_label'))
        output_frame.pack(fill='x', padx=5, pady=(0, 10))
        ttk.Label(output_frame, text=self.loc.get('prop_storyboard_output_folder_label')).pack(anchor='w', padx=10, pady=(5,0))
        output_folder_frame = ttk.Frame(output_frame)
        output_folder_frame.pack(fill='x', expand=True, padx=10, pady=(0,5))
        output_var = StringVar(value=config.get('output_folder', ''))
        property_vars['output_folder'] = output_var
        ttk.Entry(output_folder_frame, textvariable=output_var).pack(side='left', fill='x', expand=True)
        ttk.Button(output_folder_frame, text="...", width=4, command=lambda v=output_var: v.set(filedialog.askdirectory() or v.get())).pack(side='left', padx=(5,0))
        ttk.Label(output_frame, text=self.loc.get('prop_storyboard_output_prefix_label')).pack(anchor='w', padx=10)
        prefix_var = StringVar(value=config.get('output_filename_prefix', 'storyboard_video'))
        property_vars['output_filename_prefix'] = prefix_var
        ttk.Entry(output_frame, textvariable=prefix_var).pack(fill='x', padx=10, pady=(0,10))
        ttk.Label(output_frame, text=self.loc.get('prop_storyboard_music_folder_label')).pack(anchor='w', padx=10, pady=(5,0)) # English Log
        music_folder_frame = ttk.Frame(output_frame)
        music_folder_frame.pack(fill='x', expand=True, padx=10, pady=(0,5))
        music_folder_var = StringVar(value=config.get('music_folder_path', ''))
        property_vars['music_folder_path'] = music_folder_var
        ttk.Entry(music_folder_frame, textvariable=music_folder_var).pack(side='left', fill='x', expand=True)
        ttk.Button(music_folder_frame, text="...", width=4, command=lambda v=music_folder_var: v.set(filedialog.askdirectory() or v.get())).pack(side='left', padx=(5,0))
        music_volume_frame = ttk.Frame(output_frame)
        music_volume_frame.pack(fill='x', padx=10, pady=(0,10))
        ttk.Label(music_volume_frame, text=self.loc.get('prop_storyboard_music_volume_label')).pack(side='left', anchor='w')
        volume_var = IntVar(value=config.get('music_volume_percent', 20))
        property_vars['music_volume_percent'] = volume_var
        ttk.Entry(music_volume_frame, textvariable=volume_var, width=5).pack(side='left', padx=5)
        ttk.Label(music_volume_frame, text="%").pack(side='left')
        audio_mode_frame = ttk.Frame(output_frame)
        audio_mode_frame.pack(fill='x', expand=True, pady=5, padx=5)
        audio_mode_map = { self.loc.get('audio_mode_replace'): "replace", self.loc.get('audio_mode_merge'): "merge" }
        audio_mode_display_var = StringVar()
        audio_mode_wrapper = EnumVarWrapper(audio_mode_display_var, audio_mode_map, {v: k for k, v in audio_mode_map.items()})
        audio_mode_wrapper.set(config.get('original_audio_mode', 'replace'))
        property_vars['original_audio_mode'] = audio_mode_wrapper
        LabelledCombobox(audio_mode_frame, self.loc.get('prop_storyboard_original_audio_mode_label'), audio_mode_display_var, list(audio_mode_map.keys()))
        volume_frame_orig = ttk.Frame(output_frame)
        ttk.Label(volume_frame_orig, text=self.loc.get('prop_storyboard_original_audio_volume_label')).pack(side='left', padx=(10,5))
        property_vars['original_audio_volume'] = IntVar(value=config.get('original_audio_volume', 20))
        ttk.Scale(volume_frame_orig, from_=0, to=100, variable=property_vars['original_audio_volume']).pack(side='left', fill='x', expand=True)
        ttk.Label(volume_frame_orig, textvariable=property_vars['original_audio_volume'], width=4).pack(side='left', padx=(5,10))
        def _toggle_volume_slider(*args):
            if audio_mode_display_var.get() == self.loc.get('audio_mode_merge'):
                volume_frame_orig.pack(fill='x', pady=(0,10))
            else:
                volume_frame_orig.pack_forget()
        audio_mode_display_var.trace_add('write', _toggle_volume_slider)
        _toggle_volume_slider()
        mode_map = {
            self.loc.get('mode_match_largest'): "match_largest",
            self.loc.get('mode_limit_by_smallest'): "limit_by_smallest"
        }
        display_to_internal = {v: k for k, v in mode_map.items()}
        mode_display_var = StringVar()
        mode_wrapper = EnumVarWrapper(mode_display_var, display_to_internal, mode_map)
        mode_wrapper.set(config.get('generation_mode', 'match_largest'))
        property_vars['generation_mode'] = mode_wrapper
        LabelledCombobox(output_frame, self.loc.get('prop_storyboard_generation_mode_label'), mode_display_var, list(mode_map.keys()))
        delete_var = BooleanVar(value=config.get('delete_after_use', False))
        property_vars['delete_after_use'] = delete_var
        self.delete_checkbutton = ttk.Checkbutton(output_frame, text=self.loc.get('prop_stitcher_delete_after_use_label'), variable=delete_var)
        self.delete_checkbutton.pack(anchor='w', padx=10, pady=5)
        def _toggle_delete_option(*args):
            if mode_display_var.get() == self.loc.get('mode_match_largest'):
                self.delete_checkbutton.config(state="disabled")
            else:
                self.delete_checkbutton.config(state="normal")
        mode_display_var.trace_add("write", _toggle_delete_option)
        _toggle_delete_option()
        storyboard_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_storyboard_sections_label'))
        storyboard_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.sections_container = ttk.Frame(storyboard_frame)
        self.sections_container.pack(fill="both", expand=True, pady=5)
        def _add_section_row(name="", path=""):
            if not name:
                self.section_counter += 1
                name = f"{self.loc.get('prop_storyboard_section_default_name', fallback='Act')} {self.section_counter}"
            row_id = str(uuid.uuid4())
            row_frame = ttk.Frame(self.sections_container)
            row_frame.pack(fill='x', pady=2)
            name_var = StringVar(value=name)
            path_var = StringVar(value=path)
            row_data = {'id': row_id, 'frame': row_frame, 'name_var': name_var, 'path_var': path_var}
            self.section_rows.append(row_data)
            ttk.Label(row_frame, text=self.loc.get('prop_storyboard_section_name_label')).pack(side='left', padx=(0,5))
            ttk.Entry(row_frame, textvariable=name_var, width=15).pack(side='left', padx=(0,10))
            ttk.Entry(row_frame, textvariable=path_var).pack(side='left', fill='x', expand=True)
            ttk.Button(row_frame, text="...", width=3, command=lambda v=path_var: v.set(filedialog.askdirectory() or v.get())).pack(side='left', padx=(5,10))
            ttk.Button(row_frame, text="▲", width=2, command=lambda rid=row_id: _move_row(rid, -1)).pack(side='left')
            ttk.Button(row_frame, text="▼", width=2, command=lambda rid=row_id: _move_row(rid, 1)).pack(side='left')
            ttk.Button(row_frame, text="X", width=2, bootstyle="danger", command=lambda rid=row_id: _remove_row(rid)).pack(side='left', padx=5)
        def _remove_row(row_id):
            for i, row in enumerate(self.section_rows):
                if row['id'] == row_id:
                    row['frame'].destroy()
                    self.section_rows.pop(i)
                    break
        def _move_row(row_id, direction):
            for i, row in enumerate(self.section_rows):
                if row['id'] == row_id:
                    new_index = i + direction
                    if 0 <= new_index < len(self.section_rows):
                        self.section_rows.insert(new_index, self.section_rows.pop(i))
                        _redraw_rows()
                    break
        def _redraw_rows():
            for row in self.section_rows:
                row['frame'].pack_forget()
            for row in self.section_rows:
                row['frame'].pack(fill='x', pady=2)
        ttk.Button(storyboard_frame, text=self.loc.get('prop_storyboard_add_section_button'), command=_add_section_row, bootstyle="outline-success").pack(fill='x', pady=5)
        saved_sections = config.get('video_sections', [])
        if saved_sections:
            for section in saved_sections:
                _add_section_row(section.get('name', ''), section.get('path', ''))
                try:
                    name_parts = section.get('name', '').split()
                    if len(name_parts) > 1 and name_parts[0] == self.loc.get('prop_storyboard_section_default_name', fallback='Act'):
                        num = int(name_parts[1])
                        if num > self.section_counter:
                            self.section_counter = num
                except (ValueError, IndexError):
                    pass
        else:
            _add_section_row()
        class DynamicSectionsVar:
            def __init__(self, rows_data):
                self.rows_data = rows_data
            def get(self):
                return [{'name': r['name_var'].get(), 'path': r['path_var'].get()} for r in self.rows_data]
        property_vars['video_sections'] = DynamicSectionsVar(self.section_rows)
        return property_vars
