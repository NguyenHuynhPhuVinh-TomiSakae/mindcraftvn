import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from mindcraft_installer.utils.system_checker import check_nodejs, check_python
from mindcraft_installer.utils.installer import (
    install_nodejs, 
    install_mindcraft,
    check_installation, 
    repair_installation, 
    uninstall_mindcraft
)
from mindcraft_installer.utils.config_manager import load_config, save_config, load_last_install_dir, save_last_install_dir
from mindcraft_installer.utils.settings_manager import load_settings, save_settings
import subprocess
from mindcraft_installer.utils.api_manager import APIManager
from mindcraft_installer.utils.bot_config import BotConfig, save_bot_config
import json

class MindcraftInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mindcraft Installer")
        
        # Khởi tạo các biến trạng thái
        self.nodejs_installed = False
        self.python_installed = False
        
        # Khởi tạo các biến settings
        self.mc_version = tk.StringVar(value="1.20.4")
        self.host = tk.StringVar(value="127.0.0.1") 
        self.port = tk.StringVar(value="55916")
        self.auth = tk.StringVar(value="offline")
        self.profile = tk.StringVar(value="./tomisakae.json")
        self.load_memory = tk.BooleanVar(value=False)
        self.show_bot_views = tk.BooleanVar(value=False)
        self.allow_insecure_coding = tk.BooleanVar(value=False)
        self.init_message = tk.StringVar(value="xin chào thế giới và tên bạn")
        self.language = tk.StringVar(value="vi")
        
        # Khởi tạo biến install_dir
        self.install_dir = tk.StringVar()
        
        # Khởi tạo biến API
        self.api_types = ["Gemini"]  # Chỉ cho phép Gemini
        self.selected_api = tk.StringVar(value="Gemini")  # Mặc định là Gemini
        self.api_key = tk.StringVar()
        
        # Thêm biến cấu hình bot
        self.bot_name = tk.StringVar(value="TomiSakae")
        self.bot_modes = {
            "self_preservation": tk.BooleanVar(value=True),
            "unstuck": tk.BooleanVar(value=True),
            "cowardice": tk.BooleanVar(value=False),
            "self_defense": tk.BooleanVar(value=True),
            "hunting": tk.BooleanVar(value=True),
            "item_collecting": tk.BooleanVar(value=True),
            "torch_placing": tk.BooleanVar(value=True),
            "idle_staring": tk.BooleanVar(value=True),
            "cheat": tk.BooleanVar(value=False)
        }
        
        # Bind mousewheel
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Tạo giao diện (bao gồm run_btn)
        self.create_widgets()
        
        # Load đường dẫn và settings sau khi đã tạo giao diện
        last_dir = load_last_install_dir()
        if last_dir and os.path.exists(last_dir):
            self.install_dir.set(last_dir)
            self.check_and_show_run_button()
            
            # Load settings nếu có
            settings = load_settings(last_dir)
            if settings:
                try:
                    self.mc_version.set(settings.get("minecraft_version", "1.20.4"))
                    self.host.set(settings.get("host", "127.0.0.1"))
                    self.port.set(settings.get("port", 55916))
                    self.auth.set(settings.get("auth", "offline"))
                    self.profile.set(settings.get("profiles", ["./tomisakae.json"])[0])
                    self.load_memory.set(settings.get("load_memory", False))
                    self.show_bot_views.set(settings.get("show_bot_views", False))
                    self.allow_insecure_coding.set(settings.get("allow_insecure_coding", False))
                    self.init_message.set(settings.get("init_message", "xin chào thế giới và tên bạn"))
                    self.language.set(settings.get("language", "vi"))
                except Exception as e:
                    print(f"Lỗi khi load settings: {str(e)}")
        
        # Load API key nếu có
        last_dir = load_last_install_dir()
        if last_dir and os.path.exists(last_dir):
            self.install_dir.set(last_dir)
            self.check_and_show_run_button()
            
            # Load API key từ keys.json
            config = load_config(last_dir)
            if config:
                gemini_key = config.get("GEMINI_API_KEY", "")
                if gemini_key:
                    self.api_key.set(gemini_key)
        
    def create_widgets(self):
        # Frame chính
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # Tạo canvas và scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Cấu hình canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack các widget
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Tạo window trong canvas để chứa scrollable_frame
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=canvas.winfo_width())
        
        # Cập nhật kích thước scrollable region khi frame thay đổi
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        # Cập nhật chiều rộng của window khi canvas thay đổi kích thước
        def configure_window_size(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", configure_window_size)
        
        # Tạo frame cho nút chạy
        run_frame = ttk.Frame(self.scrollable_frame)
        run_frame.pack(fill="x", padx=10, pady=5)
        
        # Khởi tạo nút chạy (ẩn ban đầu)
        self.run_btn = ttk.Button(
            run_frame,
            text="Chạy Mindcraft",
            command=self.run_mindcraft,
            state='disabled'
        )
        self.run_btn.pack(side="right", padx=5)
        
        # Main container with scrollbar
        container = ttk.Frame(self.scrollable_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Add padding to main content
        main_frame = ttk.Frame(container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="Mindcraft Installer",
                 font=('Helvetica', 16, 'bold')).pack()
                 
        # System Requirements Frame
        req_frame = ttk.LabelFrame(main_frame, text="Yêu cầu hệ thống")
        req_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.nodejs_label = ttk.Label(req_frame, text="Node.js: Đang kiểm tra...")
        self.nodejs_label.pack(pady=5)
        
        self.python_label = ttk.Label(req_frame, text="Python: Đang kiểm tra...")
        self.python_label.pack(pady=5)
        
        # Installation Directory Frame
        dir_frame = ttk.LabelFrame(main_frame, text="Thư mục cài đặt")
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        dir_select_frame = ttk.Frame(dir_frame)
        dir_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.dir_entry = ttk.Entry(dir_select_frame, textvariable=self.install_dir)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.browse_btn = ttk.Button(dir_select_frame, 
                                   text="Chọn thư mục",
                                   command=self.browse_directory)
        self.browse_btn.pack(side=tk.RIGHT)
        
        # API Key Frame
        api_frame = ttk.LabelFrame(main_frame, text="Cấu hình API")
        api_frame.pack(fill=tk.X, pady=(0, 20))
        
        api_select_frame = ttk.Frame(api_frame)
        api_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(api_select_frame, text="Loại API:").pack(side=tk.LEFT)
        self.api_combo = ttk.Combobox(api_select_frame, 
                                   textvariable=self.selected_api,
                                   values=self.api_types,
                                   state="readonly")
        self.api_combo.pack(side=tk.LEFT, padx=5)
        self.api_combo.set("Gemini")
        
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(api_key_frame, text="API Key:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(api_key_frame, 
                                    textvariable=self.api_key,
                                    show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Status Frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, 
                                    text="Sẵn sàng cài đặt",
                                    wraplength=400)
        self.status_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, 
                                      length=200, 
                                      mode='determinate')
        self.progress.pack(side=tk.RIGHT)
        
        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        # Các nút khác
        self.install_btn = ttk.Button(btn_frame,
                                    text="Cài đặt",
                                    command=self.start_installation)
        self.install_btn.pack(side=tk.RIGHT, padx=5)
        
        self.repair_btn = ttk.Button(btn_frame,
                                   text="Sửa chữa",
                                   command=self.repair_installation)
        self.repair_btn.pack(side=tk.RIGHT, padx=5)
        
        self.uninstall_btn = ttk.Button(btn_frame,
                                      text="Gỡ cài đặt",
                                      command=self.uninstall)
        self.uninstall_btn.pack(side=tk.RIGHT, padx=5)
        
        # Thêm nút kiểm tra
        self.check_button = ttk.Button(
            req_frame,
            text="Kiểm tra yêu cầu hệ thống",
            command=self.check_requirements
        )
        self.check_button.pack(pady=10)
        
        # Settings Frame
        self.create_settings_frame()
        
    def create_settings_frame(self):
        settings_container = ttk.Frame(self.scrollable_frame)
        settings_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        settings_frame = ttk.LabelFrame(settings_container, text="Cấu hình")
        settings_frame.pack(fill="both", expand=True)
        
        # Frame chứa các nt
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        # Nút khôi phục mặc định
        self.restore_btn = ttk.Button(
            button_frame,
            text="Khôi phục mặc định",
            command=self.restore_default_settings
        )
        self.restore_btn.pack(side="left", padx=5)
        
        # Nút lưu cấu hình
        self.save_settings_btn = ttk.Button(
            button_frame,
            text="Lưu cấu hình",
            command=self.save_settings
        )
        self.save_settings_btn.pack(side="right", padx=5)
        
        # Thêm các widget cấu hình
        # Minecraft Version
        version_frame = ttk.Frame(settings_frame)
        version_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(version_frame, text="Phiên bản Minecraft:").pack(side="left")
        ttk.Entry(version_frame, textvariable=self.mc_version).pack(side="left", padx=5)
        
        # Host & Port
        host_frame = ttk.Frame(settings_frame)
        host_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(host_frame, text="Host:").pack(side="left")
        ttk.Entry(host_frame, textvariable=self.host).pack(side="left", padx=5)
        ttk.Label(host_frame, text="Port:").pack(side="left")
        ttk.Entry(host_frame, textvariable=self.port).pack(side="left", padx=5)
        
        # Auth
        auth_frame = ttk.Frame(settings_frame)
        auth_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(auth_frame, text="Xác thực:").pack(side="left")
        ttk.Radiobutton(auth_frame, text="Offline", variable=self.auth, value="offline").pack(side="left", padx=5)
        ttk.Radiobutton(auth_frame, text="Microsoft", variable=self.auth, value="microsoft").pack(side="left")
        
        # Profile
        profile_frame = ttk.Frame(settings_frame)
        profile_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(profile_frame, text="Profile:").pack(side="left")
        ttk.Entry(profile_frame, textvariable=self.profile).pack(side="left", padx=5, fill="x", expand=True)
        
        # Checkboxes
        options_frame = ttk.Frame(settings_frame)
        options_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Checkbutton(options_frame, text="Tải bộ nhớ từ phiên trước", variable=self.load_memory).pack(anchor="w")
        ttk.Checkbutton(options_frame, text="Hiển thị góc nhìn bot", variable=self.show_bot_views).pack(anchor="w")
        ttk.Checkbutton(options_frame, text="Cho phép chạy mã không an toàn", variable=self.allow_insecure_coding).pack(anchor="w")
        
        # Init message & Language
        msg_frame = ttk.Frame(settings_frame)
        msg_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(msg_frame, text="Tin nhắn khởi động:").pack(side="left")
        ttk.Entry(msg_frame, textvariable=self.init_message).pack(side="left", padx=5, fill="x", expand=True)
        
        lang_frame = ttk.Frame(settings_frame)
        lang_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(lang_frame, text="Ngôn ngữ:").pack(side="left")
        ttk.Entry(lang_frame, textvariable=self.language).pack(side="left", padx=5)
        
        # Thêm frame cấu hình bot
        self.create_bot_config_frame(settings_frame)
        
    def restore_default_settings(self):
        """Khôi phục cài đặt mặc định"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn khôi phục cài đặt mặc định?"):
            self.mc_version.set("1.20.4")
            self.host.set("127.0.0.1")
            self.port.set("55916")
            self.auth.set("offline")
            self.profile.set("./tomisakae.json")
            self.load_memory.set(False)
            self.show_bot_views.set(False)
            self.allow_insecure_coding.set(False)
            self.init_message.set("xin chào thế giới và tên bạn")
            self.language.set("vi")
            messagebox.showinfo("Thành công", "Đã khôi phục cài đặt mặc định!")
        
    def save_settings(self):
        """Lưu cài đặt hiện tại"""
        try:
            if not self.install_dir.get():
                messagebox.showerror("Lỗi", "Vui lòng chọn thư mục cài đặt")
                return
            
            settings = {
                "minecraft_version": self.mc_version.get(),
                "host": self.host.get(),
                "port": int(self.port.get()),
                "auth": self.auth.get(),
                "profile": self.profile.get(),
                "load_memory": self.load_memory.get(),
                "init_message": self.init_message.get(),
                "language": self.language.get(),
                "show_bot_views": self.show_bot_views.get(),
                "allow_insecure_coding": self.allow_insecure_coding.get()
            }
            
            # Lưu settings
            if save_settings(self.install_dir.get(), settings):
                # Lưu đường dẫn cài đặt
                save_last_install_dir(self.install_dir.get())
                messagebox.showinfo("Thành công", "Đã lưu cấu hình!")
            else:
                messagebox.showerror("Lỗi", "Không thể lưu cấu hình")
                
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        
    def check_requirements(self):
        """Kiểm tra các yêu cầu hệ thống khi nhấn nút"""
        self.nodejs_installed = check_nodejs()
        self.python_installed = check_python()
        
        # Cập nhật trạng thái hiển thị
        self.update_status_labels()
        
    def update_status_labels(self):
        """Cập nhật nhãn trạng thái sau khi kiểm tra"""
        nodejs_status = "✓" if self.nodejs_installed else "✗"
        python_status = "✓" if self.python_installed else "✗"
        
        self.nodejs_label.config(text=f"Node.js: {nodejs_status}")
        self.python_label.config(text=f"Python: {python_status}")
        
    def browse_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.install_dir.set(dir_path)
            # Kiểm tra và hiển thị nút chạy
            self.check_and_show_run_button()
            
            # Load settings nếu có
            settings = load_settings(dir_path)
            if settings:
                try:
                    self.mc_version.set(settings.get("minecraft_version", "1.20.4"))
                    self.host.set(settings.get("host", "127.0.0.1"))
                    self.port.set(settings.get("port", 55916))
                    self.auth.set(settings.get("auth", "offline"))
                    self.profile.set(settings.get("profiles", ["./tomisakae.json"])[0])
                    self.load_memory.set(settings.get("load_memory", False))
                    self.show_bot_views.set(settings.get("show_bot_views", False))
                    self.allow_insecure_coding.set(settings.get("allow_insecure_coding", False))
                    self.init_message.set(settings.get("init_message", "xin chào thế giới và tên bạn"))
                    self.language.set(settings.get("language", "vi"))
                except Exception as e:
                    print(f"Lỗi khi load settings: {str(e)}")
            
    def check_and_show_run_button(self):
        """Kiểm tra cài đặt và hiển thị nút chạy nếu hợp lệ"""
        install_dir = self.install_dir.get()
        if install_dir and check_installation(install_dir):
            self.run_btn.config(state='normal')
        else:
            self.run_btn.config(state='disabled')
            
    def run_mindcraft(self):
        """Chạy Mindcraft bằng node main.js"""
        try:
            install_dir = self.install_dir.get()
            if not install_dir:
                messagebox.showerror("Lỗi", "Không tìm thấy thư mục cài đặt")
                return
                
            # Lưu API key mới nếu có thay đổi
            current_key = self.api_key.get()
            config = load_config(install_dir)
            if config and config.get("GEMINI_API_KEY") != current_key:
                save_config(install_dir, "Gemini", current_key)
            
            # Lưu đường dẫn hiện tại
            current_dir = os.getcwd()
            
            # Chuyển đến thư mục cài đặt
            os.chdir(install_dir)
            
            # Chạy node main.js trong thread riêng
            def run_process():
                try:
                    process = subprocess.Popen(
                        ['node', 'main.js'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Đọc output 
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            print(output.strip())
                            
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không th chy Mindcraft: {str(e)}")
                finally:
                    # Trở về thư mục ban đầu
                    os.chdir(current_dir)
                    
            thread = threading.Thread(target=run_process)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            
    def update_status(self, message, progress=None):
        def update():
            self.status_label.config(text=message)
            if progress is not None:
                self.progress['value'] = progress
            
        self.root.after(0, update)
        
    def start_installation(self):
        install_dir = self.install_dir.get()
        api_type = self.selected_api.get()
        api_key = self.api_key.get()
        
        if not install_dir:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục cài đặt")
            return
            
        if not api_key:
            messagebox.showerror("Lỗi", "Vui lòng nhập API key")
            return
            
        def disable_buttons():
            self.install_btn.config(state='disabled')
            self.repair_btn.config(state='disabled')
            self.uninstall_btn.config(state='disabled')
            
        def enable_buttons():
            self.install_btn.config(state='normal')
            self.repair_btn.config(state='normal')
            self.uninstall_btn.config(state='normal')
            self.progress['value'] = 0
        
        self.root.after(0, disable_buttons)
        
        def install():
            try:
                # Kiểm tra và cài đặt Node.js nếu cần
                if not check_nodejs():
                    install_nodejs(self.update_status)
                
                # Kiểm tra Python
                if not check_python():
                    raise Exception("Không tìm thấy Python. Vui lòng cài đặt Python trước.")
                
                # Cài đặt Mindcraft
                install_mindcraft(install_dir, self.update_status)
                
                # Lưu config API và settings
                save_config(install_dir, api_type, api_key)
                self.save_all_settings()
                self.save_bot_config()
                
                # Hiển thị đường dẫn đến file settings.js
                settings_path = os.path.join(install_dir, "settings.js")
                self.update_status(f"File cấu hình được lưu tại:\n{settings_path}", 100)
                
                def show_success():
                    messagebox.showinfo("Thành công", 
                                      f"Cài đặt Mindcraft thành công!\nFile cấu hình: {settings_path}")
                    self.check_and_show_run_button()
                    
                self.root.after(0, show_success)
                
            except Exception as e:
                def show_error():
                    messagebox.showerror("Lỗi", str(e))
                self.root.after(0, show_error)
                
            finally:
                self.root.after(0, enable_buttons)
        
        thread = threading.Thread(target=install)
        thread.daemon = True
        thread.start()
        
    def repair_installation(self):
        if not self.install_dir.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục cài đặt")
            return
            
        if not check_installation(self.install_dir.get()):
            messagebox.showerror("Lỗi", "Không tìm thấy cài đặt Mindcraft trong thư mục này")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn sửa chữa cài đặt?"):
            self.repair_btn.config(state='disabled')
            self.install_btn.config(state='disabled')
            self.uninstall_btn.config(state='disabled')
            
            def repair():
                try:
                    repair_installation(self.install_dir.get(), self.update_status)
                    messagebox.showinfo("Thành công", "Sửa chữa cài đặt thành công!")
                except Exception as e:
                    messagebox.showerror("Lỗi", str(e))
                finally:
                    self.repair_btn.config(state='normal')
                    self.install_btn.config(state='normal')
                    self.uninstall_btn.config(state='normal')
                    self.progress['value'] = 0
                    
            thread = threading.Thread(target=repair)
            thread.start()
            
    def uninstall(self):
        if not self.install_dir.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục cài đặt")
            return
            
        if not check_installation(self.install_dir.get()):
            messagebox.showerror("Lỗi", "Không tìm thấy cài đặt Mindcraft trong thư mục này")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn gỡ cài đặt Mindcraft?"):
            try:
                uninstall_mindcraft(self.install_dir.get())
                messagebox.showinfo("Thành công", "Đã gỡ cài đặt Mindcraft!")
                self.install_dir.set("")
                self.api_key.set("")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
        
    def save_all_settings(self):
        try:
            if not self.install_dir.get():
                return False
            
            settings = {
                "minecraft_version": self.mc_version.get(),
                "host": self.host.get(),
                "port": int(self.port.get()),
                "auth": self.auth.get(),
                "profiles": [self.profile.get()],
                "load_memory": self.load_memory.get(),
                "show_bot_views": self.show_bot_views.get(),
                "allow_insecure_coding": self.allow_insecure_coding.get(),
                "init_message": self.init_message.get(),
                "language": self.language.get()
            }
            
            return save_settings(self.install_dir.get(), settings)
            
        except Exception as e:
            print(f"Lỗi khi lưu settings.js: {str(e)}")
            return False
        
    def _on_mousewheel(self, event):
        canvas = event.widget.master.master
        if isinstance(canvas, tk.Canvas):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_bot_config_frame(self, settings_frame):
        bot_frame = ttk.LabelFrame(settings_frame, text="Cấu hình Bot")
        bot_frame.pack(fill="x", padx=5, pady=5)
        
        # Frame chứa các nút
        button_frame = ttk.Frame(bot_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        # Nút khôi phục mặc định
        ttk.Button(
            button_frame,
            text="Khôi phục mặc định",
            command=self.restore_default_bot_config
        ).pack(side="left", padx=5)
        
        # Nút lưu cấu hình
        ttk.Button(
            button_frame,
            text="Lưu cấu hình bot",
            command=self.save_bot_config
        ).pack(side="right", padx=5)
        
        # Tên bot
        name_frame = ttk.Frame(bot_frame)
        name_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(name_frame, text="Tên bot:").pack(side="left")
        ttk.Entry(name_frame, textvariable=self.bot_name).pack(side="left", padx=5)
        
        # Modes
        modes_frame = ttk.LabelFrame(bot_frame, text="Chế độ hoạt động")
        modes_frame.pack(fill="x", padx=5, pady=5)
        
        mode_labels = {
            "self_preservation": "Tự bảo vệ",
            "unstuck": "Tự thoát kẹt",
            "cowardice": "Nhút nhát",
            "self_defense": "Tự vệ",
            "hunting": "Săn bắn",
            "item_collecting": "Thu thập vật phẩm", 
            "torch_placing": "Đặt đuốc",
            "idle_staring": "Nhìn chung quanh",
            "cheat": "Gian lận"
        }
        
        for mode, label in mode_labels.items():
            ttk.Checkbutton(modes_frame, 
                           text=label,
                           variable=self.bot_modes[mode]).pack(anchor="w")
        
    def restore_default_bot_config(self):
        self.bot_name.set("TomiSakae")
        default_modes = {
            "self_preservation": True,
            "unstuck": True,
            "cowardice": False,
            "self_defense": True,
            "hunting": True,
            "item_collecting": True,
            "torch_placing": True,
            "idle_staring": True,
            "cheat": False
        }
        for mode, value in default_modes.items():
            self.bot_modes[mode].set(value)
        
        # Lưu cấu hình mặc định
        self.save_bot_config()
        messagebox.showinfo("Thành công", "Đã khôi phục cấu hình bot về mặc định")
        
    def save_bot_config(self):
        try:
            install_dir = self.install_dir.get()
            if not install_dir:
                messagebox.showerror("Lỗi", "Vui lòng chọn thư mục cài đặt trước")
                return
            
            modes = {mode: var.get() for mode, var in self.bot_modes.items()}
            if save_bot_config(install_dir, self.bot_name.get(), modes):
                messagebox.showinfo("Thành công", "Đã lưu cấu hình bot")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cấu hình bot: {str(e)}")