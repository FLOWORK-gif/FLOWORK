#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\components\recorder_control_panel.py
# JUMLAH BARIS : 105
#######################################################################

import ttkbootstrap as ttk
import pyaudio
import mss
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
class RecorderControlPanel(ttk.Toplevel):
    """
    The control panel for the screen recorder.
    [V5] Added a gain/amplification slider.
    """
    def __init__(self, parent, kernel, recorder_service):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.recorder_service = recorder_service
        self.transient(parent)
        self.title(self.loc.get("recorder_panel_title", fallback="Tutorial Studio"))
        self.geometry("400x320") # (MODIFIED) A bit taller for the gain slider
        self.resizable(False, False)
        self.selected_screen = ttk.IntVar(value=1)
        self.record_audio_var = ttk.BooleanVar(value=True)
        self.gain_var = ttk.DoubleVar(value=1.5) # Default gain is 1.5x
        self.mic_device_map = {}
        self._build_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._refresh_audio_devices()
    def _build_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        screen_frame = ttk.Frame(main_frame)
        screen_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(screen_frame, text=self.loc.get("recorder_select_screen", fallback="Record Screen:")).pack(side="left")
        with mss.mss() as sct:
            monitors = sct.monitors
        self.screen_combo = ttk.Combobox(screen_frame, textvariable=self.selected_screen, state="readonly", values=list(range(1, len(monitors))))
        self.screen_combo.pack(side="right", fill="x", expand=True, padx=(10,0))
        if len(monitors) > 1:
            self.screen_combo.set(1)
        audio_frame = ttk.Frame(main_frame)
        audio_frame.pack(fill='x', pady=(0, 5))
        self.audio_check = ttk.Checkbutton(
            audio_frame,
            text=self.loc.get("recorder_use_default_mic", fallback="Record Audio (uses default microphone)"),
            variable=self.record_audio_var,
            command=self._toggle_gain_slider_state # (ADDED) Link to toggle function
        )
        self.audio_check.pack(anchor='w')
        self.gain_frame = ttk.Frame(main_frame)
        self.gain_frame.pack(fill='x', pady=(0, 15), padx=20)
        self.gain_label = ttk.Label(self.gain_frame, text=self.loc.get("recorder_gain_label", fallback="Amplification (Gain):"))
        self.gain_label.pack(side="left")
        self.gain_slider = ttk.Scale(self.gain_frame, from_=1.0, to=5.0, variable=self.gain_var)
        self.gain_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.gain_value_label = ttk.Label(self.gain_frame, text=f"{self.gain_var.get():.1f}x", width=4)
        self.gain_value_label.pack(side="left")
        self.gain_slider.config(command=lambda val: self.gain_value_label.config(text=f"{float(val):.1f}x"))
        self.start_button = ttk.Button(main_frame, text=self.loc.get("recorder_start_button", fallback="Start Recording"), command=self._start_recording, bootstyle="danger")
        self.start_button.pack(fill="x", ipady=10, side="bottom")
    def _toggle_gain_slider_state(self):
        """(ADDED) Enables/disables the gain slider based on the checkbox."""
        if self.record_audio_var.get():
            self.gain_label.config(state="normal")
            self.gain_slider.config(state="normal")
            self.gain_value_label.config(state="normal")
        else:
            self.gain_label.config(state="disabled")
            self.gain_slider.config(state="disabled")
            self.gain_value_label.config(state="disabled")
    def _refresh_audio_devices(self):
        try:
            p = pyaudio.PyAudio()
            mic_count = 0
            for i in range(p.get_device_count()):
                if p.get_device_info_by_index(i).get('maxInputChannels') > 0:
                    mic_count += 1
            p.terminate()
            if mic_count == 0:
                self.audio_check.config(state="disabled")
                self.record_audio_var.set(False)
                self._toggle_gain_slider_state()
        except Exception as e:
            self.kernel.write_to_log(f"CRITICAL: Failed to query audio devices with PyAudio: {e}", "CRITICAL")
            self.audio_check.config(state="disabled")
            self.record_audio_var.set(False)
            self._toggle_gain_slider_state()
    def _start_recording(self):
        record_audio = self.record_audio_var.get()
        monitor_number = self.selected_screen.get()
        gain = self.gain_var.get()
        self.recorder_service.start_recording(
            monitor_num=monitor_number,
            record_audio=record_audio,
            gain=gain
        )
        self.destroy()
    def _on_close(self):
        if self.recorder_service.floating_widget:
            self.recorder_service.floating_widget.control_panel_closed()
        self.destroy()
