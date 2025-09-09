#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\components\main_window.py
# JUMLAH BARIS : 27
#######################################################################

import tkinter as tk
from tkinter import ttk
class MainWindow(tk.Tk):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.title("FLOWORK GUI - API Driven")
        self.geometry("800x600")
        self.create_widgets()
        self.check_server_status()
    def create_widgets(self):
        self.label = ttk.Label(self, text="Connecting to FLOWORK Server...", font=("Helvetica", 16))
        self.label.pack(pady=50, padx=20)
    def check_server_status(self):
        status_data = self.api_client.get_server_status()
        if status_data and status_data.get("status") == "ok":
            self.label.config(text=f"Server Status: {status_data.get('message', 'Connected')}", foreground="green")
        else:
            message = status_data.get('message', 'Connection failed')
            self.label.config(text=f"Server Status: Error - {message}", foreground="red")
