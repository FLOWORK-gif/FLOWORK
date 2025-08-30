#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\custom_widgets\StandardButtons.py
# JUMLAH BARIS : 33
#######################################################################

import ttkbootstrap as ttk
class StandardButton(ttk.Button):
    def __init__(self, parent, kernel, **kwargs):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, **kwargs)
class SaveButton(StandardButton):
    """A standard Save button that automatically gets its text and success style."""
    def __init__(self, parent, kernel, **kwargs):
        text = kernel.get_service("localization_manager").get('button_save', fallback="Simpan")
        super().__init__(parent, kernel, text=text, bootstyle="success", **kwargs)
class CancelButton(StandardButton):
    """A standard Cancel button that automatically gets its text and secondary style."""
    def __init__(self, parent, kernel, **kwargs):
        text = kernel.get_service("localization_manager").get('button_cancel', fallback="Batal")
        super().__init__(parent, kernel, text=text, bootstyle="secondary", **kwargs)
class DeleteButton(StandardButton):
    """A standard Delete button that automatically gets its text and danger style."""
    def __init__(self, parent, kernel, **kwargs):
        text = kernel.get_service("localization_manager").get('trigger_btn_delete', fallback="Hapus")
        super().__init__(parent, kernel, text=text, bootstyle="danger", **kwargs)
class EditButton(StandardButton):
    """A standard Edit button that automatically gets its text and info style."""
    def __init__(self, parent, kernel, **kwargs):
        text = kernel.get_service("localization_manager").get('trigger_btn_edit', fallback="Edit...")
        super().__init__(parent, kernel, text=text, bootstyle="info", **kwargs)
