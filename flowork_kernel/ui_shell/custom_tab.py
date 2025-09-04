#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\custom_tab.py
# JUMLAH BARIS : 73
#######################################################################

import ttkbootstrap as ttk
from tkinter import Menu, messagebox
from flowork_kernel.api_client import ApiClient
class CustomTab(ttk.Frame):
    """
    Sebuah frame kosong yang menjadi dasar untuk tab kustom.
    Berisi tombol untuk menambahkan modul.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, style='TFrame')
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        placeholder_label = ttk.Label(
            self,
            text=self.loc.get('custom_tab_placeholder_text', fallback="This is Your Custom Tab.\\n\\nRight-click to add modules or other widgets."),
            font=("Helvetica", 14, "italic"),
            justify="center"
        )
        placeholder_label.pack(expand=True, padx=20, pady=20)
        watermark_label = ttk.Label(
            self,
            text=self.loc.get('custom_tab_watermark', fallback="WWW.TEETAH.ART"),
            font=("Helvetica", 10, "italic"),
            foreground="grey",
            anchor="se"
        )
        watermark_label.pack(side="bottom", fill="x", padx=10, pady=5)
        self.bind("<Button-3>", self._show_context_menu)
        placeholder_label.bind("<Button-3>", self._show_context_menu)
    def _show_context_menu(self, event):
        context_menu = Menu(self, tearoff=0)
        success, loaded_modules_data = self.api_client.get_components('modules')
        modules_to_display = []
        if success:
            modules_to_display = sorted([
                (mod_data['id'], mod_data.get('name', mod_data['id']))
                for mod_data in loaded_modules_data
            ], key=lambda x: x[1].lower())
        if not modules_to_display:
            context_menu.add_command(label=self.loc.get('no_modules_found', fallback="No modules available."))
            context_menu.entryconfig(self.loc.get('no_modules_found', fallback="No modules available."), state="disabled")
        else:
            for module_id, module_name in modules_to_display:
                context_menu.add_command(
                    label=module_name,
                    command=lambda mid=module_id, mname=module_name: self._simulate_add_module_to_canvas(mid, mname)
                )
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    def _simulate_add_module_to_canvas(self, module_id, module_name):
        messagebox.showinfo(
            self.loc.get('info_title', fallback="Information"),
            self.loc.get(
                'simulate_add_module_message',
                module_name=module_name,
                module_id=module_id,
                fallback=f"Module '{module_name}' (ID: {module_id}) would be added to the workflow canvas if this feature were fully integrated."
            )
        )
        self.kernel.write_to_log(
            self.loc.get('log_simulate_add_module', module_name=module_name, module_id=module_id, fallback=f"Simulation: Module '{module_name}' (ID: {module_id}) 'added' from CustomTab."),
            "INFO"
        )
