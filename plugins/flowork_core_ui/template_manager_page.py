#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\template_manager_page.py
# JUMLAH BARIS : 197
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, messagebox, filedialog, scrolledtext
import os
import shutil
import json
import platform
import subprocess
import re
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
class TemplateManagerPage(ttk.Frame):
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, style='TFrame', padding=0)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.create_widgets()
        theme_manager = self.kernel.get_service("theme_manager")
        if theme_manager:
            self.apply_styles(theme_manager.get_colors())
        self.populate_template_list()
        self._populate_guide()
    def apply_styles(self, colors):
        style = tk_ttk.Style(self)
        style.configure('TFrame', background=colors.get('bg'))
        style.configure('TLabel', background=colors.get('bg'), foreground=colors.get('fg'))
        style.configure('TLabelframe', background=colors.get('bg'), borderwidth=1, relief='solid', bordercolor=colors.get('border'))
        style.configure('TLabelframe.Label', background=colors.get('bg'), foreground=colors.get('fg'), font=('Helvetica', 10, 'bold'))
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _populate_guide(self):
        guide_content = self.loc.get("theme_manager_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def create_widgets(self):
        main_content_frame = ttk.Frame(self, padding=20, style='TFrame')
        main_content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        theme_frame = ttk.LabelFrame(main_content_frame, text=self.loc.get('theme_management_title'), padding=15, style='TLabelframe')
        theme_frame.pack(fill="both", expand=True, pady=(0, 20))
        upload_theme_button = ttk.Button(theme_frame, text=self.loc.get('upload_theme_button'), command=self.upload_theme, style="info.TButton")
        upload_theme_button.pack(fill='x', pady=5)
        self.theme_list_frame = ttk.Frame(theme_frame, style='TFrame')
        self.theme_list_frame.pack(fill='both', expand=True, pady=(10,0))
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('theme_manager_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        guide_handle.lift()
    def populate_template_list(self):
        self.kernel.write_to_log(self.loc.get('log_populating_theme_list'), "DEBUG")
        for widget in self.theme_list_frame.winfo_children():
            widget.destroy()
        theme_manager = self.kernel.get_service("theme_manager")
        themes = theme_manager.get_all_themes() if theme_manager else {}
        if not themes:
            ttk.Label(self.theme_list_frame, text=self.loc.get('no_themes_installed_message'), style='TLabel').pack()
            self.kernel.write_to_log(self.loc.get('log_no_themes_found'), "INFO")
            return
        sorted_themes = sorted(themes.items(), key=lambda item: item[1].get('name', item[0]).lower())
        for theme_id, theme_data in sorted_themes:
            theme_name = theme_data.get('name', theme_id)
            item_frame = ttk.Frame(self.theme_list_frame, style='TFrame')
            item_frame.pack(fill='x', pady=2)
            label_text = self.loc.get('theme_list_item_format', name=theme_name, id=theme_id)
            ttk.Label(item_frame, text=label_text, style='TLabel').pack(side='left', anchor='w', fill='x', expand=True)
            buttons_frame = ttk.Frame(item_frame, style='TFrame')
            buttons_frame.pack(side='right')
            is_removable = (theme_id != "flowork_default")
            if is_removable:
                uninstall_button = ttk.Button(buttons_frame, text=self.loc.get('uninstall_button'), style="link", width=2, command=lambda tid=theme_id, tname=theme_name: self.uninstall_theme(tid, tname))
                ToolTip(uninstall_button).update_text(self.loc.get('tooltip_delete_theme'))
                uninstall_button.pack(side='right', padx=(5,0))
            edit_button = ttk.Button(buttons_frame, text=self.loc.get('edit_button'), style="info-link", width=2, command=lambda tid=theme_id: self.edit_theme(tid))
            ToolTip(edit_button).update_text(self.loc.get('tooltip_edit_theme'))
            edit_button.pack(side='right', padx=(5,0))
            self.kernel.write_to_log(self.loc.get('log_theme_added_to_list', name=theme_name, id=theme_id), "DEBUG")
        self.kernel.write_to_log(self.loc.get('log_theme_list_populated_success'), "INFO")
    def _open_path_in_explorer(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            self.kernel.write_to_log(self.loc.get('log_opening_folder', path=path), "INFO")
        except Exception as e:
            error_msg = self.loc.get('log_failed_to_open_folder', path=path, error=str(e))
            self.kernel.write_to_log(error_msg, "ERROR")
            messagebox.showerror(self.loc.get('error_title'), error_msg)
    def edit_theme(self, theme_id):
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        all_themes = theme_manager.get_all_themes()
        theme_data = all_themes.get(theme_id)
        if theme_data and 'path' in theme_data:
            self._open_path_in_explorer(theme_data['path'])
        else:
            messagebox.showerror(self.loc.get('error_title'), self.loc.get('theme_not_found_error', name=theme_id))
    def uninstall_theme(self, theme_id, theme_name):
        self.kernel.write_to_log(self.loc.get('log_uninstall_theme_attempt', name=theme_name, id=theme_id), "INFO")
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        all_themes = theme_manager.get_all_themes()
        theme_data = all_themes.get(theme_id)
        if not theme_data:
            messagebox.showerror(self.loc.get('error_title'), self.loc.get('theme_not_found_error', name=theme_name))
            self.kernel.write_to_log(self.loc.get('log_theme_not_found_for_uninstall', fallback="ERROR: Tema '{name}' ({id}) tidak ditemukan untuk di-uninstall.", name=theme_name, id=theme_id), "ERROR")
            return
        theme_path_to_delete = theme_data['path']
        if messagebox.askyesno(self.loc.get('confirm_delete_title'), self.loc.get('confirm_delete_theme_message', name=theme_name)):
            try:
                os.remove(theme_path_to_delete)
                self.kernel.write_to_log(self.loc.get('log_theme_deleted_success', name=theme_name), "SUCCESS")
                messagebox.showinfo(self.loc.get('success_title'), self.loc.get('theme_deleted_success_message', name=theme_name))
                self.populate_template_list()
                self.kernel.root.refresh_ui_components()
            except Exception as e:
                error_msg = self.loc.get('theme_delete_failed_error', name=theme_name, error=e)
                self.kernel.write_to_log(error_msg, "ERROR")
                messagebox.showerror(self.loc.get('failed_title'), error_msg)
        else:
            self.kernel.write_to_log(self.loc.get('log_theme_uninstall_cancelled', name=theme_name), "INFO")
    def upload_theme(self):
        self.kernel.write_to_log(self.loc.get('log_upload_theme_started'), "INFO")
        filepath = filedialog.askopenfilename(
            title=self.loc.get('select_theme_file_title'),
            filetypes=[(self.loc.get('json_files_label'), "*.json")]
        )
        if not filepath:
            self.kernel.write_to_log(self.loc.get('theme_upload_cancelled'), "WARN")
            return
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                if "name" not in theme_data or "colors" not in theme_data:
                    raise ValueError(self.loc.get('invalid_theme_format_error'))
            theme_filename = os.path.basename(filepath)
            target_path = os.path.join(self.kernel.themes_path, theme_filename)
            shutil.copyfile(filepath, target_path)
            success_msg = self.loc.get('theme_upload_success', name=theme_data['name'])
            messagebox.showinfo(self.loc.get('success_title'), success_msg)
            self.populate_template_list()
            self.kernel.root.refresh_ui_components()
        except Exception as e:
            error_msg_detail = str(e)
            error_msg_localized = self.loc.get('theme_upload_failed_error', filename=os.path.basename(filepath), error=error_msg_detail)
            self.kernel.write_to_log(error_msg_localized, "ERROR")
            messagebox.showerror(self.loc.get('theme_upload_failed_title'), error_msg_localized)
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None
