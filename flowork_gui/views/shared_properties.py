#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\views\shared_properties.py
# JUMLAH BARIS : 156
#######################################################################

import ttkbootstrap as ttk
from tkinter import Text, StringVar, BooleanVar, IntVar, TclError
from api_contract import LoopConfig # # PENAMBAHAN OTOMATIS
from views.custom_widgets.tooltip import ToolTip # # PENAMBAHAN OTOMATIS
from api_client.client import ApiClient # PENAMBAHAN OTOMATIS
def create_debug_and_reliability_ui(parent, config, loc):
    """
    Membuat bagian UI untuk pengaturan Debug (breakpoint, timeout) dan Keandalan (retry).
    """
    created_vars = {}
    debug_frame = ttk.LabelFrame(parent, text=loc.get('debug_settings_title', fallback="Debug & Reliability Settings"))
    debug_frame.pack(fill='x', padx=5, pady=10, expand=False)
    created_vars['has_breakpoint'] = ttk.BooleanVar(value=config.get('has_breakpoint', False))
    bp_check = ttk.Checkbutton(debug_frame, text=loc.get('set_breakpoint_checkbox', fallback="Set Breakpoint on This Node"), variable=created_vars['has_breakpoint'])
    bp_check.pack(anchor='w', pady=5, padx=10)
    ToolTip(bp_check).update_text(loc.get('set_breakpoint_tooltip'))
    timeout_frame = ttk.Frame(debug_frame)
    timeout_frame.pack(fill='x', padx=10, pady=(5,5))
    ttk.Label(timeout_frame, text=loc.get('execution_timeout_label')).pack(side='left', anchor='w')
    created_vars['timeout_seconds'] = ttk.IntVar(value=config.get('timeout_seconds', 0))
    timeout_entry = ttk.Entry(timeout_frame, textvariable=created_vars['timeout_seconds'], width=8)
    timeout_entry.pack(side='left', padx=5)
    ToolTip(timeout_entry).update_text(loc.get('execution_timeout_tooltip'))
    ttk.Separator(debug_frame).pack(fill='x', pady=5)
    retry_title_label = ttk.Label(debug_frame, text=loc.get('retry_settings_title'))
    retry_title_label.pack(anchor='w', padx=10, pady=(10,0))
    retry_frame = ttk.Frame(debug_frame)
    retry_frame.pack(fill='x', padx=10, pady=(5,10))
    ttk.Label(retry_frame, text=loc.get('retry_attempts_label')).pack(side='left', anchor='w')
    created_vars['retry_attempts'] = ttk.IntVar(value=config.get('retry_attempts', 0))
    retry_attempts_entry = ttk.Entry(retry_frame, textvariable=created_vars['retry_attempts'], width=5)
    retry_attempts_entry.pack(side='left', padx=5)
    ToolTip(retry_attempts_entry).update_text(loc.get('retry_attempts_tooltip'))
    ttk.Label(retry_frame, text=loc.get('retry_delay_label')).pack(side='left', padx=10, anchor='w')
    created_vars['retry_delay_seconds'] = ttk.IntVar(value=config.get('retry_delay_seconds', 5))
    retry_delay_entry = ttk.Entry(retry_frame, textvariable=created_vars['retry_delay_seconds'], width=5)
    retry_delay_entry.pack(side='left', padx=5)
    ToolTip(retry_delay_entry).update_text(loc.get('retry_delay_tooltip'))
    ttk.Separator(debug_frame).pack(fill='x', pady=5)
    checkpoint_title_label = ttk.Label(debug_frame, text=loc.get('checkpoint_settings_title'))
    checkpoint_title_label.pack(anchor='w', padx=10, pady=(10,0))
    created_vars['is_checkpoint'] = ttk.BooleanVar(value=config.get('is_checkpoint', False))
    checkpoint_check = ttk.Checkbutton(debug_frame, text=loc.get('enable_checkpoint_checkbox'), variable=created_vars['is_checkpoint'])
    checkpoint_check.pack(anchor='w', pady=5, padx=10)
    ToolTip(checkpoint_check).update_text(loc.get('checkpoint_tooltip'))
    return created_vars
def create_loop_settings_ui(parent, config, loc, available_vars):
    """
    Membuat bagian UI untuk pengaturan Looping dan Jeda (Sleep).
    """
    created_vars = {}
    loop_frame = ttk.LabelFrame(parent, text=loc.get('loop_settings_title', fallback="Looping Settings"))
    loop_frame.pack(fill='x', padx=5, pady=10, expand=False)
    created_vars['enable_loop'] = ttk.BooleanVar(value=config.get('enable_loop', False))
    enable_loop_check = ttk.Checkbutton(loop_frame, text=loc.get('enable_loop_checkbox', fallback="Enable Looping"), variable=created_vars['enable_loop'])
    enable_loop_check.pack(anchor='w', padx=5)
    loop_options_frame = ttk.Frame(loop_frame)
    created_vars['loop_type'] = ttk.StringVar(value=config.get('loop_type', LoopConfig.LOOP_TYPE_COUNT))
    count_details_frame = ttk.Frame(loop_options_frame)
    condition_details_frame = ttk.Frame(loop_options_frame)
    count_radio = ttk.Radiobutton(loop_options_frame, text=loc.get('loop_type_count_radio', fallback="Repeat N Times"), variable=created_vars['loop_type'], value=LoopConfig.LOOP_TYPE_COUNT)
    count_radio.pack(anchor='w')
    count_details_frame.pack(fill='x', anchor='w', padx=20, pady=2)
    created_vars['loop_iterations'] = ttk.IntVar(value=config.get('loop_iterations', 1))
    count_entry = ttk.Entry(count_details_frame, textvariable=created_vars['loop_iterations'], width=10)
    count_entry.pack(anchor='w')
    ToolTip(count_entry).update_text(loc.get('loop_iterations_tooltip', fallback="Number of loop iterations."))
    condition_radio = ttk.Radiobutton(loop_options_frame, text=loc.get('loop_type_condition_radio', fallback="Repeat Until Condition"), variable=created_vars['loop_type'], value=LoopConfig.LOOP_TYPE_CONDITION)
    condition_radio.pack(anchor='w', pady=(10,0))
    condition_details_frame.pack(fill='x', padx=20, pady=5)
    ttk.Label(condition_details_frame, text=loc.get('condition_var_label', fallback="Condition Variable:")).pack(side='left', padx=(0,5))
    created_vars['loop_condition_var'] = ttk.StringVar(value=config.get('loop_condition_var', ''))
    loop_condition_var_combobox = ttk.Combobox(condition_details_frame, textvariable=created_vars['loop_condition_var'], values=list(available_vars.keys()), state="readonly")
    loop_condition_var_combobox.pack(side='left', expand=True, fill='x', padx=(0,5))
    ToolTip(loop_condition_var_combobox).update_text(loc.get('condition_var_tooltip', fallback="The DataPayload variable to evaluate."))
    created_vars['loop_condition_op'] = ttk.StringVar(value=config.get('loop_condition_op', '=='))
    all_operators = ['==', '!=', '>', '<', '>=', '<=', loc.get('operator_contains_text', fallback='contains'), loc.get('operator_not_contains_text', fallback='not contains'), loc.get('operator_starts_with', fallback='starts with'), loc.get('operator_ends_with', fallback='ends with')]
    ttk.Combobox(condition_details_frame, textvariable=created_vars['loop_condition_op'], values=all_operators, state="readonly", width=15).pack(side='left', padx=(0,5))
    created_vars['loop_condition_val'] = ttk.StringVar(value=config.get('loop_condition_val', ''))
    condition_val_entry = ttk.Entry(condition_details_frame, textvariable=created_vars['loop_condition_val'])
    condition_val_entry.pack(side='left', expand=True, fill='x')
    ToolTip(condition_val_entry).update_text(loc.get('condition_val_tooltip', fallback="The value to compare against."))
    ttk.Separator(loop_frame).pack(fill='x', pady=10, padx=5)
    sleep_control_frame = ttk.Frame(loop_frame)
    created_vars['enable_sleep'] = ttk.BooleanVar(value=config.get('enable_sleep', False))
    sleep_options_frame = ttk.Frame(sleep_control_frame)
    static_sleep_frame = ttk.Frame(sleep_options_frame)
    random_sleep_details_frame = ttk.Frame(sleep_options_frame)
    ttk.Checkbutton(sleep_control_frame, text=loc.get('enable_sleep_checkbox', fallback="Enable Delay Between Iterations"), variable=created_vars['enable_sleep']).pack(anchor='w', pady=5, padx=10)
    created_vars['sleep_type'] = ttk.StringVar(value=config.get('sleep_type', 'static'))
    static_radio = ttk.Radiobutton(sleep_options_frame, text=loc.get('sleep_type_static_radio', fallback="Static Delay (seconds)"), variable=created_vars['sleep_type'], value="static")
    static_radio.pack(anchor='w')
    static_sleep_frame.pack(anchor='w', padx=20, pady=2)
    created_vars['static_duration'] = ttk.IntVar(value=config.get('static_duration', 1))
    static_duration_entry = ttk.Entry(static_sleep_frame, textvariable=created_vars['static_duration'], width=10)
    static_duration_entry.pack(anchor='w')
    ToolTip(static_duration_entry).update_text(loc.get('static_duration_tooltip', fallback="Duration of the delay in seconds."))
    random_radio = ttk.Radiobutton(sleep_options_frame, text=loc.get('sleep_type_random_radio', fallback="Random Delay (seconds)"), variable=created_vars['sleep_type'], value="random_range")
    random_radio.pack(anchor='w', pady=(10,0))
    random_sleep_details_frame.pack(fill='x', padx=20, pady=5)
    ttk.Label(random_sleep_details_frame, text=loc.get('random_min_label', fallback="Min:")).pack(side='left', padx=(0,5))
    created_vars['random_min'] = ttk.IntVar(value=config.get('random_min', 1))
    random_min_entry = ttk.Entry(random_sleep_details_frame, textvariable=created_vars['random_min'], width=5)
    random_min_entry.pack(side='left', padx=(0,5))
    ToolTip(random_min_entry).update_text(loc.get('random_min_tooltip', fallback="Minimum delay duration (seconds)."))
    ttk.Label(random_sleep_details_frame, text=loc.get('random_max_label', fallback="Max:")).pack(side='left', padx=(0,5))
    created_vars['random_max'] = ttk.IntVar(value=config.get('random_max', 5))
    random_max_entry = ttk.Entry(random_sleep_details_frame, textvariable=created_vars['random_max'], width=5)
    random_max_entry.pack(side='left', padx=(0,5))
    ToolTip(random_max_entry).update_text(loc.get('random_max_tooltip', fallback="Maximum delay duration (seconds)."))
    def _toggle_sleep_details():
        is_static = created_vars['sleep_type'].get() == "static"
        if is_static:
            static_sleep_frame.pack(anchor='w', padx=20, pady=2)
            random_sleep_details_frame.pack_forget()
        else:
            static_sleep_frame.pack_forget()
            random_sleep_details_frame.pack(fill='x', padx=20, pady=5)
    def _toggle_sleep_options():
        if created_vars['enable_sleep'].get():
            sleep_options_frame.pack(fill='x', padx=10, pady=5)
            _toggle_sleep_details()
        else:
            sleep_options_frame.pack_forget()
    def _toggle_loop_details():
        is_count = created_vars['loop_type'].get() == LoopConfig.LOOP_TYPE_COUNT
        if is_count:
            count_details_frame.pack(fill='x', anchor='w', padx=20, pady=2)
            condition_details_frame.pack_forget()
        else:
            count_details_frame.pack_forget()
            condition_details_frame.pack(fill='x', padx=20, pady=5)
    def _toggle_loop_options():
        if created_vars['enable_loop'].get():
            loop_options_frame.pack(fill='x', padx=10, pady=5)
            sleep_control_frame.pack(fill='x', padx=0, pady=0)
            _toggle_loop_details()
            _toggle_sleep_options()
        else:
            loop_options_frame.pack_forget()
            sleep_control_frame.pack_forget()
    enable_loop_check.config(command=_toggle_loop_options)
    static_radio.config(command=_toggle_sleep_details)
    random_radio.config(command=_toggle_sleep_details)
    created_vars['enable_sleep'].trace_add('write', lambda *args: _toggle_sleep_options())
    count_radio.config(command=_toggle_loop_details)
    condition_radio.config(command=_toggle_loop_details)
    _toggle_loop_options()
    return created_vars
