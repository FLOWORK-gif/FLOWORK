import os
import sys
import pandas as pd
import mimetypes
import struct
import re
import ttkbootstrap as ttk
from tkinter import StringVar, filedialog
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema
from flowork_kernel.ui_shell import shared_properties
from flowork_kernel.utils.file_helper import sanitize_filename
from flowork_kernel.utils.payload_helper import get_nested_value
from flowork_kernel.ui_shell.components.LabelledCombobox import LabelledCombobox

# (COMMENT) We no longer need the 'types' module
# from google.genai import types

# (COMMENT) Import time module for potential delays if needed in the future.
import time

class GeminiTtsBatchModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer, IDynamicOutputSchema):
    """
    Processes a CSV file or payload data to convert text lines into speech using Google Gemini's TTS model.
    """
    TIER = "pro"

    def __init__(self, module_id, services):
        super().__init__(module_id, services)

    def _parse_audio_mime_type(self, mime_type: str) -> dict[str, int | None]:
        # (COMMENT) This function is correct.
        bits_per_sample = 16
        rate = 24000
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try: rate = int(param.split("=", 1)[1])
                except (ValueError, IndexError): pass
            elif param.startswith("audio/L"):
                try: bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError): pass
        return {"bits_per_sample": bits_per_sample, "rate": rate}

    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        # (COMMENT) This function is correct.
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b("RIFF"), chunk_size, b("WAVE"), b("fmt "), 16, 1,
            num_channels, sample_rate, byte_rate, block_align, bits_per_sample,
            b("data"), data_size
        )
        return header + audio_data

    # (COMMENT) The _error_payload function is removed because we will now raise exceptions directly,
    # which is the correct way to signal an error to the WorkflowExecutor and its behaviors like RetryHandler.
    # def _error_payload(self, payload, error_message, status_updater):
    #     self.logger(f"Gemini TTS Batch failed: {error_message}", "ERROR") # English Log
    #     status_updater(error_message, "ERROR")
    #     if 'data' not in payload or not isinstance(payload['data'], dict):
    #         payload['data'] = {}
    #     payload['data']['error'] = error_message
    #     return {"payload": payload, "output_name": "error"}

    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):
        try:
            import google.generativeai as genai
        except ImportError:
            # (MODIFIED) Raise an error instead of returning a payload, to be caught by the executor.
            raise ImportError("Required library 'google-genai' is not installed in the module's vendor folder.")

        input_mode = config.get('input_source_mode', 'csv')
        text_column_name = config.get('text_column_name', 'text')
        status_column_name = config.get('status_column_name', 'status')
        output_folder = config.get('output_folder')
        voice_model = config.get('voice_model', 'Zephyr')

        if not output_folder:
            raise ValueError("Output Folder must be configured.")
        os.makedirs(output_folder, exist_ok=True)

        variable_manager = self.kernel.get_service("variable_manager_service")

        tasks_to_process = []
        df = None
        source_csv_path = None

        if input_mode == 'csv':
            source_csv_path = config.get('source_csv_path')
            if not source_csv_path or not os.path.exists(source_csv_path):
                raise FileNotFoundError(f"Source CSV file not found at: {source_csv_path}")
            try:
                df = pd.read_csv(source_csv_path, sep=';', keep_default_na=False, skip_blank_lines=True)
                if status_column_name not in df.columns:
                    df[status_column_name] = ""
                for index, row in df.iterrows():
                     tasks_to_process.append({'index': index, 'row': row})
            except Exception as e:
                raise ValueError(f"Failed to read CSV. Error: {e}")
        else: # payload mode
            payload_variable = config.get('payload_variable', 'data.texts_to_process')
            source_data = get_nested_value(payload, payload_variable)
            if not source_data or not isinstance(source_data, list):
                raise ValueError(f"Data not found or is not a list at payload path: '{payload_variable}'")
            for i, item in enumerate(source_data):
                if isinstance(item, str):
                    tasks_to_process.append({'index': i, 'row': {text_column_name: item}})
                elif isinstance(item, dict):
                    tasks_to_process.append({'index': i, 'row': item})

        if not tasks_to_process:
            status_updater("No text items found to process.", "WARN")
            return {"payload": payload, "output_name": "success"}

        results_log = []
        processed_count = 0

        # (COMMENT) We must initialize the model outside the loop to be efficient.
        try:
            tts_model = genai.GenerativeModel("gemini-1.5-pro-latest")
        except Exception as e:
             raise RuntimeError(f"Failed to initialize Gemini Model. Error: {e}")

        for task in tasks_to_process:
            index = task['index']
            row = task['row']

            if input_mode == 'csv' and str(row.get(status_column_name, "")).lower() == 'success':
                continue

            text_to_speak = row.get(text_column_name)
            if not text_to_speak or (isinstance(text_to_speak, float) and pd.isna(text_to_speak)):
                self.logger(f"Skipping row {index+1}: Text in column '{text_column_name}' is empty or invalid.", "WARN") # English Log
                continue

            text_to_speak = str(text_to_speak)
            status_updater(f"Processing item {index + 1}/{len(tasks_to_process)}: '{text_to_speak[:40]}...'", "INFO")

            try:
                api_key = variable_manager.get_variable("GEMINI_API_KEY")
                if not api_key:
                    self.logger(f"Skipping row {index+1}: No available GEMINI_API_KEY from pool.", "WARN") # English Log
                    continue

                genai.configure(api_key=api_key)

                generation_config = {"speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": voice_model}}}}

                response = tts_model.generate_content(
                    text_to_speak,
                    generation_config=generation_config
                )

                if not (response.candidates and response.candidates[0].content and response.candidates[0].content.parts):
                    raise ValueError("AI response structure is invalid or empty.")

                audio_part = response.candidates[0].content.parts[0]
                if not hasattr(audio_part, 'inline_data') or not hasattr(audio_part.inline_data, 'data'):
                    raise ValueError("AI did not return audio data in the expected format (inline_data).")

                raw_audio_data = audio_part.inline_data.data
                mime_type = audio_part.inline_data.mime_type

                wav_data = self._convert_to_wav(raw_audio_data, mime_type)

                output_filename = f"{index+1:04d}_{sanitize_filename(text_to_speak[:25])}.wav"
                output_path = os.path.join(output_folder, output_filename)

                with open(output_path, "wb") as f: f.write(wav_data)

                results_log.append({"text": text_to_speak, "output_path": output_path, "status": "success"})
                processed_count += 1

                if input_mode == 'csv':
                    df.loc[index, status_column_name] = 'success'
                    df.to_csv(source_csv_path, index=False, sep=';')

                self.logger(f"Successfully processed item {index+1}. Breaking loop.", "INFO") # English Log
                break

            except Exception as e:
                self.logger(f"Error processing item {index+1}: {e}", "ERROR") # English Log
                if input_mode == 'csv':
                    df.loc[index, status_column_name] = f"error: {str(e)[:100]}"
                    df.to_csv(source_csv_path, index=False, sep=';')

                # (MODIFIED) This is the final, correct way to signal an error.
                # It raises a real Exception that the RetryHandler and WorkflowExecutor can understand.
                raise RuntimeError(f"Error processing item {index+1}: {e}")

        status_updater(f"Processing complete for this run. Generated {processed_count} audio file(s).", "SUCCESS")

        if 'data' not in payload or not isinstance(payload['data'], dict):
            payload['data'] = {}

        payload['data']['tts_results'] = results_log
        payload['data']['total_processed'] = processed_count

        return {"payload": payload, "output_name": "success"}

    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        config = get_current_config()
        property_vars = {}

        source_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_tts_input_source_label'))
        source_frame.pack(fill='x', padx=5, pady=5)

        property_vars['input_source_mode'] = StringVar(value=config.get('input_source_mode', 'csv'))

        csv_frame = ttk.Frame(source_frame)
        payload_frame = ttk.Frame(source_frame)

        def _toggle_source_ui():
            mode = property_vars['input_source_mode'].get()
            if mode == 'csv':
                payload_frame.pack_forget()
                csv_frame.pack(fill='x', padx=5, pady=5)
            else:
                csv_frame.pack_forget()
                payload_frame.pack(fill='x', padx=5, pady=5)

        ttk.Radiobutton(source_frame, text=self.loc.get('input_mode_csv'), variable=property_vars['input_source_mode'], value='csv', command=_toggle_source_ui).pack(anchor='w', padx=10, pady=(5,0))
        ttk.Radiobutton(source_frame, text=self.loc.get('input_mode_payload'), variable=property_vars['input_source_mode'], value='payload', command=_toggle_source_ui).pack(anchor='w', padx=10)

        csv_path_var = StringVar(value=config.get('source_csv_path', ''))
        property_vars['source_csv_path'] = csv_path_var
        ttk.Label(csv_frame, text=self.loc.get('prop_tts_source_csv_label')).pack(anchor='w')
        entry_frame = ttk.Frame(csv_frame)
        entry_frame.pack(fill='x', expand=True)
        ttk.Entry(entry_frame, textvariable=csv_path_var).pack(side='left', fill='x', expand=True)
        ttk.Button(entry_frame, text="...", width=4, command=lambda: csv_path_var.set(filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")]) or csv_path_var.get())).pack(side='left', padx=(5,0))

        property_vars['payload_variable'] = StringVar(value=config.get('payload_variable', 'data.texts_to_process'))
        LabelledCombobox(payload_frame, self.loc.get('prop_tts_payload_variable_label'), property_vars['payload_variable'], list(available_vars.keys()))

        columns_frame = ttk.LabelFrame(parent_frame, text="Data Column/Key Configuration")
        columns_frame.pack(fill='x', padx=5, pady=5)
        property_vars['text_column_name'] = StringVar(value=config.get('text_column_name', 'text'))
        PropertyField(columns_frame, self.loc.get('prop_tts_text_column_label'), property_vars['text_column_name'])
        property_vars['status_column_name'] = StringVar(value=config.get('status_column_name', 'status'))
        PropertyField(columns_frame, self.loc.get('prop_tts_status_column_label'), property_vars['status_column_name'])

        output_frame = ttk.LabelFrame(parent_frame, text=self.loc.get('prop_tts_output_folder_label'))
        output_frame.pack(fill='x', padx=5, pady=5)
        output_path_var = StringVar(value=config.get('output_folder', ''))
        property_vars['output_folder'] = output_path_var
        out_entry_frame = ttk.Frame(output_frame)
        out_entry_frame.pack(fill='x', expand=True, padx=5, pady=5)
        ttk.Entry(out_entry_frame, textvariable=output_path_var).pack(side='left', fill='x', expand=True)
        ttk.Button(out_entry_frame, text="...", width=4, command=lambda: output_path_var.set(filedialog.askdirectory() or output_path_var.get())).pack(side='left', padx=(5,0))

        property_vars['voice_model'] = StringVar(value=config.get('voice_model', 'Zephyr'))
        LabelledCombobox(parent_frame, self.loc.get('prop_tts_voice_model_label'), property_vars['voice_model'], ["Zephyr", "Puck", "Aura", "Lyra", "Luna", "Titan"])

        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)
        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)
        property_vars.update(debug_vars)

        _toggle_source_ui()
        return property_vars

    def get_dynamic_output_schema(self, config):
        return self.manifest.get('output_schema', [])

    def get_data_preview(self, config: dict):
        input_mode = config.get('input_source_mode', 'csv')
        if input_mode == 'csv':
            csv_path = config.get('source_csv_path')
            if not csv_path or not os.path.exists(csv_path):
                return [{'error': 'Source CSV file not set or not found.'}]
            try:
                df = pd.read_csv(csv_path, nrows=5, sep=';')
                return df.to_dict('records')
            except Exception as e:
                return [{'error': f"Failed to read CSV for preview: {e}"}]
        else:
            return [{'status': 'preview_not_available', 'reason': 'Data source is dynamic from payload.'}]

class PropertyField(ttk.Frame):
    def __init__(self, parent, label_text: str, variable, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text=label_text).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(self, textvariable=variable).grid(row=0, column=1, sticky="ew")
        self.pack(fill='x', pady=5, padx=5)