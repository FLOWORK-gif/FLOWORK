# File: test_silent.pyw
# A minimal Tkinter window to test if pythonw.exe is truly windowless.
import tkinter as tk

try:
    root = tk.Tk()
    root.title("Tes Senyap")
    root.geometry("200x100")
    label = tk.Label(root, text="Jika tidak ada CMD,\npythonw.exe AMAN.")
    label.pack(pady=20)
    root.mainloop()
except Exception:
    # If this fails, it doesn't matter for our test.
    # The key is whether a console appeared on launch.
    pass