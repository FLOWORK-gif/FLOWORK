#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\dashboard_frame.py
# JUMLAH BARIS : 55
#######################################################################

import ttkbootstrap as ttk
class DashboardFrame(ttk.Frame):
    """
    Sebuah bingkai yang membungkus setiap widget di dashboard.
    Menyediakan title bar untuk dragging, tombol close, dan pegangan resize.
    [FIXED V2] Now uses an explicit 'is_docked' flag to control drag/resize behavior correctly.
    """
    def __init__(self, parent, manager, widget_id, title, content_widget_class, content_widget_id: str, is_docked=False, **kwargs): # MODIFIED: Added is_docked parameter
        super().__init__(parent, style='primary.TFrame', borderwidth=1, relief="solid")
        self.manager = manager
        self.widget_id = widget_id
        self.is_docked = is_docked # ADDED: Store the docked state
        title_bar = ttk.Frame(self, style='primary.TFrame', height=30)
        title_bar.pack(side="top", fill="x", padx=1, pady=1)
        title_bar.pack_propagate(False)
        close_button = ttk.Button(title_bar, text="X", width=3, style="danger.TButton", command=self.close_widget)
        close_button.pack(side="right", padx=(0, 5), pady=2)
        title_label = ttk.Label(title_bar, text=title, style="primary.inverse.TLabel", font=("Helvetica", 10, "bold"))
        title_label.pack(side="left", padx=10)
        content_frame = ttk.Frame(self, style='light.TFrame', padding=5)
        content_frame.pack(expand=True, fill="both", padx=1, pady=(0, 1))
        if not self.is_docked:
            sizegrip = ttk.Sizegrip(self, style='primary.TSizegrip')
            sizegrip.place(relx=1.0, rely=1.0, anchor="se")
            sizegrip.bind("<ButtonPress-1>", self.on_resize_press)
            sizegrip.bind("<B1-Motion>", self.on_resize_motion)
            sizegrip.bind("<ButtonRelease-1>", self.on_resize_release)
        self.content_widget = content_widget_class(content_frame, self.manager.coordinator_tab, self.manager.kernel, widget_id=content_widget_id)
        self.content_widget.pack(expand=True, fill="both")
        title_bar.bind("<ButtonPress-1>", self.on_press)
        title_bar.bind("<B1-Motion>", self.on_drag)
        title_bar.bind("<ButtonRelease-1>", self.on_release)
        title_label.bind("<ButtonPress-1>", self.on_press)
        title_label.bind("<B1-Motion>", self.on_drag)
        title_label.bind("<ButtonRelease-1>", self.on_release)
    def on_press(self, event):
        if not self.is_docked:
            self.manager.start_drag(self, event)
    def on_drag(self, event):
        if not self.is_docked:
            self.manager.drag_widget(event)
    def on_release(self, event):
        if not self.is_docked:
            self.manager.stop_drag(event)
    def on_resize_press(self, event): self.manager.start_resize(self, event)
    def on_resize_motion(self, event): self.manager.resize_widget(event)
    def on_resize_release(self, event): self.manager.stop_resize(event)
    def close_widget(self): self.manager.remove_widget(self.widget_id)
