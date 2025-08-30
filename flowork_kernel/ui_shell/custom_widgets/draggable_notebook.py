#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\custom_widgets\draggable_notebook.py
# JUMLAH BARIS : 75
#######################################################################

import ttkbootstrap as ttk
from tkinter import TclError, Menu, messagebox
from tkinter import ttk as tk_ttk
class DraggableNotebook(tk_ttk.Notebook):
    def __init__(self, master=None, **kw):
        self.loc = kw.pop('loc', None)
        super().__init__(master, **kw)
        self.bind("<ButtonPress-1>", self.on_tab_press, True)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.drag_data = {"x": 0, "y": 0, "item": None, "tab_id": None}
        self.bind("<ButtonPress-3>", self.show_context_menu)
        self.kernel = master.winfo_toplevel().kernel
        self._close_tab_command = None
    def set_close_tab_command(self, command):
        self._close_tab_command = command
    def on_tab_press(self, event):
        try:
            index = self.index(f"@{event.x},{event.y}")
            if index == "":
                self.drag_data["item"] = None
                return
            tab_id = self.tabs()[index]
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.drag_data["item"] = index
            self.drag_data["tab_id"] = tab_id
        except TclError:
            self.drag_data["item"] = None
    def on_mouse_drag(self, event):
        if self.drag_data["item"] is not None:
            tab_id_to_move = self.drag_data["tab_id"]
            try:
                target_index = self.index(f"@{event.x},{event.y}")
                if target_index != "" and self.drag_data["item"] != target_index:
                    self.insert(target_index, tab_id_to_move)
                    self.drag_data["item"] = target_index
            except TclError:
                pass
    def on_mouse_release(self, event):
        self.drag_data = {"x": 0, "y": 0, "item": None, "tab_id": None}
    def show_context_menu(self, event):
        try:
            index = self.index(f"@{event.x},{event.y}")
            if index == "": return
            tab_id = self.tabs()[index]
            context_menu = Menu(self, tearoff=0)
            context_menu.add_command(label=self.loc.get('context_menu_rename_tab'), command=lambda: self.rename_tab(index))
            if self._close_tab_command:
                if len(self.tabs()) > 1:
                    context_menu.add_command(label=self.loc.get('menu_close_tab'), command=lambda: self._close_tab_command(tab_id))
                else:
                    context_menu.add_command(label=self.loc.get('menu_close_tab'), state='disabled')
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        except TclError:
            pass
    def rename_tab(self, index):
        current_name = self.tab(index, "text").strip()
        new_name = ttk.dialogs.dialogs.Querybox.get_string(
            title=self.loc.get('rename_tab_popup_title'),
            prompt=self.loc.get('rename_tab_popup_label'),
            initialvalue=current_name
        )
        if new_name and new_name.strip() != "":
            self.tab(index, text=f" {new_name.strip()} ")
