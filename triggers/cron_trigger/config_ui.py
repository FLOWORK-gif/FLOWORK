#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\triggers\cron_trigger\config_ui.py
# JUMLAH BARIS : 138
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, Frame
class CronConfigUI(ttk.Frame):
    """
    User-friendly Cronjob Configuration UI that translates simple inputs
    into a cron string automatically.
    """
    def __init__(self, parent, loc, initial_config):
        super().__init__(parent)
        self.loc = loc
        self.schedule_type_var = StringVar(value='daily') # Default to daily
        self.vars = {
            'every_x_minutes': StringVar(value='5'),
            'hourly_minute': StringVar(value='0'),
            'daily_hour': StringVar(value='9'),
            'daily_minute': StringVar(value='0'),
            'weekly_days': {i: ttk.BooleanVar(value=False) for i in range(7)}, # 0=Monday, 6=Sunday
            'weekly_hour': StringVar(value='9'),
            'weekly_minute': StringVar(value='0'),
        }
        self._parse_initial_config(initial_config.get('cron_string', '0 9 * * *'))
        self._create_widgets()
        self._on_schedule_type_change()
    def _create_widgets(self):
        """Creates all UI widgets."""
        type_frame = ttk.LabelFrame(self, text=self.loc.get('cron_ui_schedule_type', fallback="Schedule Type"))
        type_frame.pack(fill='x', expand=True, pady=(0, 10))
        ttk.Radiobutton(type_frame, text=self.loc.get('cron_ui_every_x_minutes', fallback="Every X Minutes"),
                        variable=self.schedule_type_var, value='minutes', command=self._on_schedule_type_change).pack(anchor='w', padx=5)
        ttk.Radiobutton(type_frame, text=self.loc.get('cron_ui_every_hour', fallback="Every Hour"),
                        variable=self.schedule_type_var, value='hourly', command=self._on_schedule_type_change).pack(anchor='w', padx=5)
        ttk.Radiobutton(type_frame, text=self.loc.get('cron_ui_daily', fallback="Daily"),
                        variable=self.schedule_type_var, value='daily', command=self._on_schedule_type_change).pack(anchor='w', padx=5)
        ttk.Radiobutton(type_frame, text=self.loc.get('cron_ui_weekly', fallback="Weekly"),
                        variable=self.schedule_type_var, value='weekly', command=self._on_schedule_type_change).pack(anchor='w', padx=5)
        self.details_frame = ttk.Frame(self)
        self.details_frame.pack(fill='x', expand=True, pady=10)
    def _on_schedule_type_change(self):
        """Displays the UI appropriate for the selected schedule type."""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        schedule_type = self.schedule_type_var.get()
        if schedule_type == 'minutes':
            self._create_minutes_ui()
        elif schedule_type == 'hourly':
            self._create_hourly_ui()
        elif schedule_type == 'daily':
            self._create_daily_ui()
        elif schedule_type == 'weekly':
            self._create_weekly_ui()
    def _create_minutes_ui(self):
        """UI for 'Every X Minutes' schedule."""
        frame = self.details_frame
        ttk.Label(frame, text=self.loc.get('cron_ui_run_every', fallback="Run every")).pack(side='left', padx=(0, 5))
        ttk.Entry(frame, textvariable=self.vars['every_x_minutes'], width=5).pack(side='left')
        ttk.Label(frame, text=self.loc.get('cron_ui_minutes_label', fallback="minutes")).pack(side='left', padx=5)
    def _create_hourly_ui(self):
        """UI for 'Every Hour' schedule."""
        frame = self.details_frame
        ttk.Label(frame, text=self.loc.get('cron_ui_run_at_minute', fallback="Run at minute:")).pack(side='left', padx=(0, 5))
        ttk.Entry(frame, textvariable=self.vars['hourly_minute'], width=5).pack(side='left')
    def _create_daily_ui(self):
        """UI for 'Daily' schedule."""
        frame = self.details_frame
        ttk.Label(frame, text=self.loc.get('cron_ui_run_at_time', fallback="Run at time:")).pack(side='left', padx=(0, 5))
        ttk.Entry(frame, textvariable=self.vars['daily_hour'], width=5).pack(side='left')
        ttk.Label(frame, text=":").pack(side='left', padx=2)
        ttk.Entry(frame, textvariable=self.vars['daily_minute'], width=5).pack(side='left')
    def _create_weekly_ui(self):
        """UI for 'Weekly' schedule."""
        frame = self.details_frame
        days_frame = ttk.Frame(frame)
        days_frame.pack(fill='x', pady=(0,10))
        days = [
            self.loc.get('day_mon', fallback="Mon"), self.loc.get('day_tue', fallback="Tue"),
            self.loc.get('day_wed', fallback="Wed"), self.loc.get('day_thu', fallback="Thu"),
            self.loc.get('day_fri', fallback="Fri"), self.loc.get('day_sat', fallback="Sat"),
            self.loc.get('day_sun', fallback="Sun")
        ]
        for i, day_text in enumerate(days):
            ttk.Checkbutton(days_frame, text=day_text, variable=self.vars['weekly_days'][i]).pack(side='left', expand=True)
        time_frame = ttk.Frame(frame)
        time_frame.pack(fill='x')
        ttk.Label(time_frame, text=self.loc.get('cron_ui_run_at_time', fallback="Run at time:")).pack(side='left', padx=(0, 5))
        ttk.Entry(time_frame, textvariable=self.vars['weekly_hour'], width=5).pack(side='left')
        ttk.Label(time_frame, text=":").pack(side='left', padx=2)
        ttk.Entry(time_frame, textvariable=self.vars['weekly_minute'], width=5).pack(side='left')
    def _parse_initial_config(self, cron_string):
        """Tries to parse the cron string to pre-fill the UI."""
        parts = cron_string.split()
        if len(parts) != 5: return
        minute, hour, day_month, month, day_week = parts
        if day_week != '*' and day_month == '*' and month == '*':
            self.schedule_type_var.set('weekly')
            self.vars['weekly_hour'].set(hour if hour != '*' else '9')
            self.vars['weekly_minute'].set(minute if minute != '*' else '0')
            selected_days = day_week.split(',')
            for i in range(7):
                if str(i) in selected_days:
                    self.vars['weekly_days'][i].set(True)
        elif minute.startswith('*/'):
            self.schedule_type_var.set('minutes')
            self.vars['every_x_minutes'].set(minute[2:])
        elif hour == '*' and day_month == '*' and month == '*':
            self.schedule_type_var.set('hourly')
            self.vars['hourly_minute'].set(minute)
        else: # Default to Daily
            self.schedule_type_var.set('daily')
            self.vars['daily_hour'].set(hour if hour != '*' else '9')
            self.vars['daily_minute'].set(minute if minute != '*' else '0')
    def get_config(self):
        """Builds the cron string from the UI inputs."""
        schedule_type = self.schedule_type_var.get()
        cron_string = "* * * * *" # Default
        if schedule_type == 'minutes':
            minute = self.vars['every_x_minutes'].get()
            cron_string = f"*/{minute} * * * *"
        elif schedule_type == 'hourly':
            minute = self.vars['hourly_minute'].get()
            cron_string = f"{minute} * * * *"
        elif schedule_type == 'daily':
            hour = self.vars['daily_hour'].get()
            minute = self.vars['daily_minute'].get()
            cron_string = f"{minute} {hour} * * *"
        elif schedule_type == 'weekly':
            hour = self.vars['weekly_hour'].get()
            minute = self.vars['weekly_minute'].get()
            days = [str(i) for i, var in self.vars['weekly_days'].items() if var.get()]
            day_string = ",".join(days) if days else '*'
            cron_string = f"{minute} {hour} * * {day_string}"
        return {"cron_string": cron_string}
