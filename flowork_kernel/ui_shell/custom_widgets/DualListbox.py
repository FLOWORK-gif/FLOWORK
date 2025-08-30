#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\custom_widgets\DualListbox.py
# JUMLAH BARIS : 65
#######################################################################

import ttkbootstrap as ttk
from tkinter import Listbox, ANCHOR, END
class DualListbox(ttk.Frame):
    """
    A reusable widget featuring two listboxes and buttons to move items between them.
    Encapsulates the logic for selecting items from an available pool.
    """
    def __init__(self, parent, kernel, available_items: list = None, selected_items: list = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        available_items = available_items or []
        selected_items = selected_items or []
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0) # Button column should not expand
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text=self.loc.get('duallist_available', fallback="Tersedia")).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(self, text=self.loc.get('duallist_selected', fallback="Terpilih")).grid(row=0, column=2, sticky='w', padx=5)
        self.available_listbox = Listbox(self, selectmode='extended', exportselection=False)
        self.available_listbox.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        self.selected_listbox = Listbox(self, selectmode='extended', exportselection=False)
        self.selected_listbox.grid(row=1, column=2, sticky='nsew', padx=(5, 0))
        for item in sorted(list(set(available_items) - set(selected_items))):
            self.available_listbox.insert(END, item)
        for item in selected_items:
            self.selected_listbox.insert(END, item)
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=1, padx=10, sticky='ns')
        ttk.Button(button_frame, text=">", command=self._move_to_selected).pack(pady=5)
        ttk.Button(button_frame, text=">>", command=self._move_all_to_selected).pack(pady=5)
        ttk.Button(button_frame, text="<", command=self._move_to_available).pack(pady=5)
        ttk.Button(button_frame, text="<<", command=self._move_all_to_available).pack(pady=5)
    def _move_to_selected(self):
        selected_indices = self.available_listbox.curselection()
        for i in reversed(selected_indices):
            item = self.available_listbox.get(i)
            self.selected_listbox.insert(END, item)
            self.available_listbox.delete(i)
    def _move_all_to_selected(self):
        items = self.available_listbox.get(0, END)
        for item in items:
            self.selected_listbox.insert(END, item)
        self.available_listbox.delete(0, END)
    def _move_to_available(self):
        selected_indices = self.selected_listbox.curselection()
        for i in reversed(selected_indices):
            item = self.selected_listbox.get(i)
            self.available_listbox.insert(END, item)
            self.selected_listbox.delete(i)
    def _move_all_to_available(self):
        items = self.selected_listbox.get(0, END)
        for item in items:
            self.available_listbox.insert(END, item)
        self.selected_listbox.delete(0, END)
    def get_selected_items(self) -> list:
        """Returns the final list of items in the 'selected' box."""
        return list(self.selected_listbox.get(0, END))
