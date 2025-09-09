#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\batch_video_splitter_c3d4\processor.py
# JUMLAH BARIS : 160
#######################################################################

import os
import sys
import subprocess
import ttkbootstrap as ttk
from tkinter import StringVar, filedialog, IntVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.file_helper import sanitize_filename
import uuid
class BatchVideoSplitterModule(BaseModule, IExecutable, IConfigurableUI):
    """
    Splits all video files in a source folder into smaller segments based on duration.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.ffmpeg_path = self._find_ffmpeg()
        self.folder_pair_rows = []
    def _find_ffmpeg(self):
        ffmpeg_executable = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
        path = os.path.join(self.kernel.project_root_path, "vendor", "ffmpeg", "bin", ffmpeg_executable)
        if os.path.exists(path):
            return path
        self.logger("FATAL: FFmpeg executable not found in vendor directory.", "CRITICAL")
        return None
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg is not available. This module cannot function.")
        folder_pairs = config.get('folder_pairs', [])
        segment_duration = config.get('segment_duration', 3)
        if not folder_pairs:
            raise ValueError("No source/output folder pairs have been configured.")
        try:
            segment_duration = int(segment_duration)
            if segment_duration <= 0:
                raise ValueError("Segment duration must be a positive number.")
        except (ValueError, TypeError):
            raise ValueError("Segment duration must be a valid integer.")
        all_results = []
        total_processed_all_jobs = 0
        total_segments_all_jobs = 0
        for i, pair in enumerate(folder_pairs):
            source_folder = pair.get('source')
            output_folder = pair.get('output')
            status_updater(f"Starting job {i+1}/{len(folder_pairs)}: Source '{os.path.basename(source_folder)}'", "INFO")
            if not source_folder or not os.path.isdir(source_folder):
                self.logger(f"Job {i+1} skipped: Source folder not found or is not a directory: {source_folder}", "WARN")
                all_results.append({'source': source_folder, 'status': 'skipped', 'reason': 'Source not found'})
                continue
            if not output_folder:
                output_folder = os.path.join(source_folder, "split_output")
                self.logger(f"Job {i+1}: Output folder not specified, using default: {output_folder}", "WARN")
            os.makedirs(output_folder, exist_ok=True)
            video_files = [f for f in os.listdir(source_folder) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))]
            if not video_files:
                self.logger(f"Job {i+1}: No video files found in '{source_folder}'.", "WARN")
                all_results.append({'source': source_folder, 'status': 'skipped', 'reason': 'No videos in source'})
                continue
            processed_count_job = 0
            total_segments_job = 0
            for j, filename in enumerate(video_files):
                status_updater(f"Job {i+1} - Processing {j+1}/{len(video_files)}: {filename}", "INFO")
                input_path = os.path.join(source_folder, filename)
                sanitized_base_name = sanitize_filename(os.path.splitext(filename)[0])
                output_pattern = os.path.join(output_folder, f"{sanitized_base_name}_segment_%03d.mp4")
                command = [
                    self.ffmpeg_path, "-i", input_path, "-c", "copy", "-map", "0",
                    "-segment_time", str(segment_duration), "-f", "segment",
                    "-reset_timestamps", "1", output_pattern
                ]
                try:
                    creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                    subprocess.run(command, check=True, capture_output=True, text=True, creationflags=creation_flags)
                    segments_created = len([f for f in os.listdir(output_folder) if f.startswith(f"{sanitized_base_name}_segment_")])
                    total_segments_job += segments_created
                    processed_count_job += 1
                except subprocess.CalledProcessError as e:
                    self.logger(f"Failed to split video '{filename}'. FFmpeg error: {e.stderr}", "ERROR")
                    continue
            total_processed_all_jobs += processed_count_job
            total_segments_all_jobs += total_segments_job
            all_results.append({'source': source_folder, 'output': output_folder, 'status': 'completed', 'files_processed': processed_count_job, 'segments_created': total_segments_job})
        status_updater(f"Batch split complete. Total files processed: {total_processed_all_jobs}, Total segments created: {total_segments_all_jobs}.", "SUCCESS")
        if 'data' not in payload or not isinstance(payload['data'], dict):
            payload['data'] = {}
        payload['data']['batch_results'] = all_results
        payload['data']['total_files_processed'] = total_processed_all_jobs
        payload['data']['total_segments_created'] = total_segments_all_jobs
        return {"payload": payload, "output_name": "success"}
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        self.folder_pair_rows = []
        settings_frame = ttk.LabelFrame(parent_frame, text="Split Settings")
        settings_frame.pack(fill='x', padx=5, pady=5)
        duration_frame = ttk.Frame(settings_frame)
        duration_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(duration_frame, text=self.loc.get('prop_splitter_segment_duration_label')).pack(side='left', padx=(0,10))
        duration_var = IntVar(value=config.get('segment_duration', 3))
        property_vars['segment_duration'] = duration_var
        ttk.Entry(duration_frame, textvariable=duration_var, width=10).pack(side='left')
        dynamic_list_frame = ttk.LabelFrame(parent_frame, text="Folder Pairs (Source -> Output)")
        dynamic_list_frame.pack(fill='both', expand=True, padx=5, pady=10)
        self.rows_container = ttk.Frame(dynamic_list_frame)
        self.rows_container.pack(fill='both', expand=True, padx=5, pady=5)
        def _add_folder_pair_row(source="", output=""):
            row_id = str(uuid.uuid4())
            row_frame = ttk.Frame(self.rows_container)
            row_frame.pack(fill='x', pady=3, expand=True)
            row_frame.columnconfigure(0, weight=1)
            row_frame.columnconfigure(1, weight=1)
            source_frame = ttk.Frame(row_frame)
            source_frame.grid(row=0, column=0, sticky='ew', padx=(0, 10))
            source_frame.columnconfigure(0, weight=1)
            source_var = StringVar(value=source)
            ttk.Label(source_frame, text=self.loc.get('prop_splitter_source_folder_label')).pack(anchor='w')
            source_entry_frame = ttk.Frame(source_frame)
            source_entry_frame.pack(fill='x', expand=True)
            ttk.Entry(source_entry_frame, textvariable=source_var).pack(side='left', fill='x', expand=True)
            ttk.Button(source_entry_frame, text="...", width=3, command=lambda v=source_var: v.set(filedialog.askdirectory() or v.get())).pack(side='left', padx=5)
            output_frame = ttk.Frame(row_frame)
            output_frame.grid(row=0, column=1, sticky='ew', padx=(10, 0))
            output_frame.columnconfigure(0, weight=1)
            output_var = StringVar(value=output)
            ttk.Label(output_frame, text=self.loc.get('prop_splitter_output_folder_label')).pack(anchor='w')
            output_entry_frame = ttk.Frame(output_frame)
            output_entry_frame.pack(fill='x', expand=True)
            ttk.Entry(output_entry_frame, textvariable=output_var).pack(side='left', fill='x', expand=True)
            ttk.Button(output_entry_frame, text="...", width=3, command=lambda v=output_var: v.set(filedialog.askdirectory() or v.get())).pack(side='left', padx=5)
            delete_button = ttk.Button(row_frame, text="X", bootstyle="danger", width=2, command=lambda rid=row_id: _remove_row(rid))
            delete_button.grid(row=0, column=2, padx=(10, 0))
            self.folder_pair_rows.append({'id': row_id, 'frame': row_frame, 'source_var': source_var, 'output_var': output_var})
        def _remove_row(row_id):
            for i, row in enumerate(self.folder_pair_rows):
                if row['id'] == row_id:
                    row['frame'].destroy()
                    self.folder_pair_rows.pop(i)
                    break
        ttk.Button(dynamic_list_frame, text=self.loc.get('prop_splitter_add_pair_button'), command=lambda: _add_folder_pair_row(), bootstyle="outline-success").pack(fill='x', pady=5)
        saved_pairs = config.get('folder_pairs', [])
        if saved_pairs:
            for pair in saved_pairs:
                _add_folder_pair_row(pair.get('source', ''), pair.get('output', ''))
        class DynamicFolderPairsVar:
            def __init__(self, rows_data):
                self.rows_data = rows_data
            def get(self):
                return [{'source': r['source_var'].get(), 'output': r['output_var'].get()} for r in self.rows_data]
        property_vars['folder_pairs'] = DynamicFolderPairsVar(self.folder_pair_rows)
        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)
        return property_vars
