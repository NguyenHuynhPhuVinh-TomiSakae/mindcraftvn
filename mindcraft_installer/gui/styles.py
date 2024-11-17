from tkinter import ttk

def setup_styles(root):
    root.configure(bg='white')
    style = ttk.Style()
    style.configure('TFrame', background='white')
    style.configure('TLabelframe', background='white') 
    style.configure('TLabelframe.Label', background='white')
    style.configure('TButton', padding=5)
    style.configure('TLabel', padding=5)