import tkinter as tk
from mindcraft_installer.gui.installer_gui import MindcraftInstallerGUI
from mindcraft_installer.gui.styles import setup_styles

def main():
    root = tk.Tk()
    # Đặt vị trí cửa sổ
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 700
    window_height = 600
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    setup_styles(root)
    app = MindcraftInstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Lỗi không mong muốn: {str(e)}")
        input("Nhấn Enter để thoát...")