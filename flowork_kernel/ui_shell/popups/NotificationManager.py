#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\popups\NotificationManager.py
# JUMLAH BARIS : 49
#######################################################################

from .NotificationToast import NotificationToast
class NotificationManager:
    """
    Manages the queue, positioning, and appearance of multiple NotificationToasts.
    """
    def __init__(self, main_window, kernel):
        self.main_window = main_window
        self.kernel = kernel
        self.active_toasts = []
        self.padding = 10  # Jarak antar popup dan dari tepi layar
        self.toast_width = 300
        self.toast_height = 80
    def show_toast(self, title, message, level="INFO"):
        """Fungsi utama untuk menampilkan notifikasi baru."""
        loc = self.kernel.get_service("localization_manager")
        if not loc:
            return
        if not loc.get_setting("notifications_enabled", True):
            return # Jangan tampilkan jika dinonaktifkan di pengaturan
        duration_seconds = loc.get_setting("notifications_duration_seconds", 5)
        duration_ms = int(duration_seconds * 1000)
        toast = NotificationToast(self.main_window, title, message, level, duration=duration_ms)
        self.active_toasts.append(toast)
        self._reposition_toasts()
        self.main_window.after(duration_ms + 1000, lambda: self._remove_toast_from_list(toast))
    def _reposition_toasts(self):
        """Menghitung ulang dan mengatur posisi semua toast yang aktif."""
        if not self.main_window.winfo_exists():
            return
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()
        start_x = screen_width - self.toast_width - self.padding
        current_y = screen_height - self.toast_height - self.padding
        for toast in self.active_toasts:
            if toast.winfo_exists():
                toast.set_position(start_x, current_y)
                current_y -= (self.toast_height + self.padding)
    def _remove_toast_from_list(self, toast_to_remove):
        """Menghapus referensi toast dari daftar setelah animasinya selesai."""
        if toast_to_remove in self.active_toasts:
            self.active_toasts.remove(toast_to_remove)
        self._reposition_toasts()
