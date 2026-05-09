import tkinter as tk
from tkinter import ttk

class StyleManager:
    def __init__(self, root):
        self.style = ttk.Style(root)

        self.style.configure("TLabel", font=("Helvetica", 11))
        self.style.configure("TButton", font=("Helvetica", 10))
        self.style.configure("TFrame", padding=5)

        self.style.configure("Title.TLabel", font=("Helvetica", 20, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 10))
        self.style.configure("HUD.TLabel", font=("Helvetica", 12, "bold"))

        self.style.configure("TLabelframe.Label", font=("Helvetica", 12, "bold"))

        self.style.configure("TEntry", font=("Helvetica", 11))
        self.style.configure("TCombobox", font=("Helvetica", 11))
        self.style.configure("TRadiobutton", font=("Helvetica", 10))