#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\modules\video_player_popup\processor.py
# JUMLAH BARIS : 100
#######################################################################

import os
import sys
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox
try:
    import vlc
except ImportError:
    vlc = None
class VideoPlayerPopupModule(BaseModule, IExecutable, IConfigurableUI):
    """
    Module to play a video file from a payload path in a separate popup window.
    Requires VLC media player to be installed on the system.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.vlc_instance = None
        if vlc:
            try:
                self.vlc_instance = vlc.Instance('--no-xlib --quiet')
            except Exception as e:
                self.logger(f"Failed to initialize VLC instance: {e}", "ERROR")
        else:
            self.logger("Python-VLC library not found. Please ensure it's in requirements.txt.", "CRITICAL")
    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        if not vlc or not self.vlc_instance:
            error_msg = "VLC is not properly installed or configured. This module cannot function."
            self.logger(error_msg, "ERROR")
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        video_path_key = config.get('video_path_variable', 'data.merged_video_paths')
        video_data = get_nested_value(payload, video_path_key)
        video_path = None
        if isinstance(video_data, list):
            if video_data:
                video_path = video_data[0] # Ambil video pertama dari list
                self.logger(f"Found a list of videos. Playing the first one: {video_path}", "INFO")
            else:
                error_msg = f"Variable '{video_path_key}' is an empty list. No video to play."
                self.logger(error_msg, "ERROR")
                payload['error'] = error_msg
                return {"payload": payload, "output_name": "error"}
        elif isinstance(video_data, str):
            video_path = video_data # Jika sudah string, langsung gunakan
        if not video_path or not os.path.exists(video_path):
            error_msg = f"Video file not found at path '{video_path}' (from variable '{video_path_key}')."
            self.logger(error_msg, "ERROR")
            payload['error'] = error_msg
            return {"payload": payload, "output_name": "error"}
        ui_callback(self._create_player_window, video_path)
        status_updater("Video popup displayed successfully.", "SUCCESS")
        return {"payload": payload, "output_name": "success"}
    def _create_player_window(self, video_path):
        """Creates and runs the VLC player window."""
        popup = tk.Toplevel()
        popup.title(f"Flowork Video Player - {os.path.basename(video_path)}")
        popup.geometry("800x600")
        player_frame = ttk.Frame(popup)
        player_frame.pack(fill="both", expand=True)
        try:
            media_player = self.vlc_instance.media_player_new()
            media = self.vlc_instance.media_new(video_path)
            media_player.set_media(media)
            if sys.platform == "win32":
                media_player.set_hwnd(player_frame.winfo_id())
            else:
                media_player.set_xwindow(player_frame.winfo_id())
            media_player.play()
            def on_close():
                media_player.stop()
                popup.destroy()
            popup.protocol("WM_DELETE_WINDOW", on_close)
        except Exception as e:
            self.logger(f"Failed to create VLC player: {e}", "ERROR")
            error_label = ttk.Label(popup, text=f"Error: Could not load video.\n{e}")
            error_label.pack(pady=20, padx=20)
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}
        if not vlc:
            ttk.Label(parent_frame, text=self.loc.get('vlc_not_found_error'), bootstyle="danger", wraplength=300).pack(pady=10, padx=5, fill='x')
        else:
            ttk.Label(parent_frame, text=self.loc.get('vlc_ready'), bootstyle="success").pack(pady=5, padx=5, fill='x')
        input_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_input_settings_label'))
        input_frame.pack(fill='x', padx=5, pady=5, expand=True)
        video_path_var = StringVar(value=config.get('video_path_variable', 'data.merged_video_paths'))
        property_vars['video_path_variable'] = video_path_var
        LabelledCombobox(input_frame, self.loc.get('prop_video_path_variable_label'), video_path_var, list(available_vars.keys()))
        return property_vars
