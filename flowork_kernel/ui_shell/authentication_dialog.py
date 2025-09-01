#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\authentication_dialog.py
# JUMLAH BARIS : 137
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, simpledialog # (DITAMBAHKAN)
from flowork_kernel.api_client import ApiClient
import threading
class AuthenticationDialog(ttk.Toplevel):
    """
    A single dialog window that handles both Login and Registration forms.
    (MODIFIED) Now stores user data in the kernel and publishes an event on successful login.
    """
    def __init__(self, parent, kernel):
        super().__init__(parent)
        self.kernel = kernel
        self.api_client = ApiClient(kernel=self.kernel)
        self.title("Login or Register")
        self.geometry("400x520") # (MODIFIKASI) Ditinggikan sedikit untuk tombol baru
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.login_email_var = ttk.StringVar()
        self.login_password_var = ttk.StringVar()
        self.reg_username_var = ttk.StringVar()
        self.reg_email_var = ttk.StringVar()
        self.reg_password_var = ttk.StringVar()
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.login_frame = self._create_login_frame(self.container)
        self.register_frame = self._create_register_frame(self.container)
        self.show_login()
        self.wait_window()
    def show_login(self):
        self.register_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
    def show_register(self):
        self.login_frame.pack_forget()
        self.register_frame.pack(fill="both", expand=True)
    def _create_login_frame(self, parent):
        frame = ttk.Frame(parent, padding=40)
        ttk.Label(frame, text="FLOWORK", font=("-size 24 -weight bold"), bootstyle="primary").pack(pady=(0, 10))
        ttk.Label(frame, text="Welcome Back!", font=("-size 12"), bootstyle="secondary").pack(pady=(0, 30))
        ttk.Label(frame, text="Email", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.login_email_var).pack(fill="x", pady=(0,15))
        ttk.Label(frame, text="Password", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.login_password_var, show="*").pack(fill="x", pady=(0,25))
        self.login_button = ttk.Button(frame, text="Login", command=self._perform_login_thread, bootstyle="primary")
        self.login_button.pack(fill="x", ipady=8, pady=(0,10))
        links_frame = ttk.Frame(frame)
        links_frame.pack(fill='x', pady=5)
        register_link = ttk.Button(links_frame, text="Don't have an account? Register", command=self.show_register, bootstyle="link-secondary")
        register_link.pack(side="left")
        forgot_password_link = ttk.Button(links_frame, text="Forgot Password?", command=self._prompt_for_password_reset, bootstyle="link-primary")
        forgot_password_link.pack(side="right")
        return frame
    def _create_register_frame(self, parent):
        frame = ttk.Frame(parent, padding=40)
        ttk.Label(frame, text="Create Account", font=("-size 24 -weight bold"), bootstyle="success").pack(pady=(0, 20))
        ttk.Label(frame, text="Username:", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.reg_username_var).pack(fill="x", pady=(0,10))
        ttk.Label(frame, text="Email:", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.reg_email_var).pack(fill="x", pady=(0,10))
        ttk.Label(frame, text="Password:", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.reg_password_var, show="*").pack(fill="x", pady=(0,20))
        self.register_button = ttk.Button(frame, text="Register", command=self._perform_register_thread, bootstyle="success")
        self.register_button.pack(fill="x", ipady=8, pady=(0,10))
        login_link = ttk.Button(frame, text="Already have an account? Login", command=self.show_login, bootstyle="link-secondary")
        login_link.pack()
        return frame
    def _prompt_for_password_reset(self):
        """Asks the user for their email to send a reset link."""
        email = simpledialog.askstring("Password Reset", "Please enter your registered email address:", parent=self)
        if email and email.strip():
            threading.Thread(target=self._perform_password_reset, args=(email.strip(),), daemon=True).start()
    def _perform_password_reset(self, email):
        """Calls the API client to initiate the password reset process."""
        self.kernel.write_to_log(f"Initiating password reset for email: {email}", "INFO")
        success, response = self.api_client.forgot_password(email)
        self.after(0, messagebox.showinfo, "Request Sent", "If an account exists for that email, a password reset link has been sent.")
    def _perform_login_thread(self):
        self.login_button.config(state="disabled", text="Logging in...")
        threading.Thread(target=self._perform_login, daemon=True).start()
    def _perform_login(self):
        email = self.login_email_var.get().strip()
        password = self.login_password_var.get().strip()
        if not email or not password:
            self.after(0, self._on_login_failed, "Email and Password are required.")
            return
        success, response = self.api_client.login_user(email, password)
        if success:
            response['email'] = email
            self.after(0, self._on_login_success, response)
        else:
            self.after(0, self._on_login_failed, response)
    def _on_login_success(self, login_data):
        self.kernel.write_to_log(f"User '{self.login_email_var.get()}' logged in successfully.", "SUCCESS")
        self.kernel.current_user = login_data
        user_tier = login_data.get('tier', 'free')
        self.kernel.license_tier = user_tier
        self.kernel.is_premium = self.kernel.TIER_HIERARCHY.get(user_tier, 0) > 0
        state_manager = self.kernel.get_service("state_manager")
        if state_manager:
            state_manager.set("user_session_token", login_data.get('session_token'))
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.publish("USER_LOGGED_IN", login_data)
        messagebox.showinfo("Login Success", f"Welcome back! You are logged in with '{user_tier}' tier access.", parent=self.master)
        self.destroy()
    def _on_login_failed(self, error_message):
        messagebox.showerror("Login Failed", f"Error: {error_message}", parent=self)
        self.login_button.config(state="normal", text="Login")
    def _perform_register_thread(self):
        self.register_button.config(state="disabled", text="Registering...")
        threading.Thread(target=self._perform_register, daemon=True).start()
    def _perform_register(self):
        username = self.reg_username_var.get().strip()
        email = self.reg_email_var.get().strip()
        password = self.reg_password_var.get().strip()
        if not all([username, email, password]):
            self.after(0, self._on_register_failed, "All fields are required.")
            return
        success, response = self.api_client.register_user(username, email, password)
        if success:
            self.after(0, self._on_register_success)
        else:
            self.after(0, self._on_register_failed, response)
    def _on_register_success(self):
        self.register_button.config(state="normal", text="Register")
        messagebox.showinfo("Success", "Registration successful! You can now log in.", parent=self)
        self.show_login()
    def _on_register_failed(self, error_message):
        messagebox.showerror("Registration Failed", f"Error: {error_message}", parent=self)
        self.register_button.config(state="normal", text="Register")
