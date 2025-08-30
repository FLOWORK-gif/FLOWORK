#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\custom_widgets\scrolled_frame.py
# JUMLAH BARIS : 46
#######################################################################

import ttkbootstrap as ttk
class ScrolledFrame(ttk.Frame):
    """
    A reusable frame that includes a vertical scrollbar.
    Widgets should be packed into the .scrollable_frame attribute.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.vscrollbar = ttk.Scrollbar(self, orient="vertical")
        self.vscrollbar.pack(fill="y", side="right", expand=False)
        self.canvas = ttk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.scrollable_frame,
                                       anchor="nw")
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    def destroy(self):
        """
        Custom destroy method to safely unlink canvas and scrollbar before destruction.
        This prevents race conditions and the 'invalid command name' TclError.
        """
        if self.canvas.winfo_exists():
            self.canvas.configure(yscrollcommand='')
        if self.vscrollbar.winfo_exists():
            self.vscrollbar.configure(command='')
        super().destroy()
    def _on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        if self.canvas.winfo_exists():
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
    def _on_canvas_configure(self, event):
        """Use the canvas width to configure the inner frame's width"""
        if self.canvas.winfo_exists():
            self.canvas.itemconfig(self.interior_id, width=event.width)
