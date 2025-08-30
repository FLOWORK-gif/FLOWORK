#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\dashboard_tab.py
# JUMLAH BARIS : 36
#######################################################################

import ttkbootstrap as ttk
class DashboardTab(ttk.Frame):
    """
    Frame untuk Dashboard. Sekarang berisi pengalih bahasa.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, style='TFrame')
        self.kernel = kernel_instance
        self.loc = self.kernel.loc
        container = ttk.Frame(self, style='TFrame', padding=20)
        container.pack(expand=True, fill='both', anchor='n')
        lang_frame = ttk.Frame(container, style='TFrame')
        lang_frame.pack(pady=10, anchor='w')
        lang_label = ttk.Label(lang_frame, text="Pilih Bahasa:", font=("Helvetica", 11, "bold"))
        lang_label.pack(side='left', padx=(0, 10))
        self.lang_combobox = ttk.Combobox(
            lang_frame,
            values=["id", "en"],
            state="readonly"
        )
        self.lang_combobox.set(self.loc.current_lang)
        self.lang_combobox.pack(side='left')
        self.lang_combobox.bind("<<ComboboxSelected>>", self.change_language)
    def change_language(self, event=None):
        """Memuat bahasa baru dan memuat ulang UI."""
        selected_lang = self.lang_combobox.get()
        print(f"Bahasa diubah ke: {selected_lang}")
        self.kernel.loc.load_language(selected_lang)
        self.kernel.reload_ui()
