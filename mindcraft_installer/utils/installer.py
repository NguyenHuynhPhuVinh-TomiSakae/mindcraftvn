import os
import sys
import tempfile
import requests
import subprocess
import zipfile
import shutil
from threading import Thread
import json
from .bot_profiles import get_tomisakae_profile

def download_file(url, dest, update_status=None):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    downloaded = 0
    
    with open(dest, 'wb') as f:
        for data in response.iter_content(block_size):
            downloaded += len(data)
            f.write(data)
            if update_status and total_size:
                progress = (downloaded / total_size) * 100
                update_status(f"Đang tải... {int(progress)}%", progress)

def install_nodejs(update_status):
    try:
        update_status("Đang tải Node.js...", 10)
        nodejs_url = "https://nodejs.org/dist/v14.17.0/node-v14.17.0-x64.msi"
        temp_file = os.path.join(tempfile.gettempdir(), "nodejs_install.msi")
        download_file(nodejs_url, temp_file, update_status)
        
        update_status("Đang cài đặt Node.js...", 30)
        subprocess.run(['msiexec', '/i', temp_file, '/qn'], check=True)
        
        # Cài đặt các package cần thiết
        update_status("Đang cài đặt các package Node.js...", 40)
        subprocess.run(['npm', 'install', '-g', 'yarn'], check=True)
        
        return True
    except Exception as e:
        raise Exception(f"Không thể cài đặt Node.js: {str(e)}")

def install_mindcraft(install_dir, update_status):
    try:
        # Tạo và kiểm tra thư mục cài đặt
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
            
        # Tải mã nguồn dưới dạng zip
        update_status("Đang tải mã nguồn Mindcraft...", 50)
        repo_url = "https://github.com/kolbytn/mindcraft/archive/refs/heads/main.zip"
        zip_path = os.path.join(tempfile.gettempdir(), "mindcraft.zip")
        download_file(repo_url, zip_path, update_status)
        
        # Giải nén file zip và di chuyển các file
        update_status("Đang giải nén...", 60)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
            
        # Di chuyển các file từ thư mục con ra ngoài
        temp_dir = os.path.join(install_dir, "mindcraft-main")
        if os.path.exists(temp_dir):
            # Lưu nội dung settings.js nếu đã tồn tại
            old_settings = None
            old_settings_path = os.path.join(install_dir, "settings.js")
            if os.path.exists(old_settings_path):
                with open(old_settings_path, "r", encoding="utf-8") as f:
                    old_settings = f.read()
            
            # Di chuyển các file
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join(install_dir, item)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                shutil.move(src, dst)
            
            # Khôi phục settings.js nếu có
            if old_settings:
                with open(old_settings_path, "w", encoding="utf-8") as f:
                    f.write(old_settings)
                    
            shutil.rmtree(temp_dir)
            
        # Cài đặt dependencies
        update_status("Đang cài đặt các dependencies...", 70)
        subprocess.run(['npm', 'install'], cwd=install_dir, shell=True, check=True)
        
        # Xóa file andy.json nếu tồn tại
        andy_path = os.path.join(install_dir, "andy.json")
        if os.path.exists(andy_path):
            os.remove(andy_path)
            
        # Tạo file tomisakae.json với nội dung từ profile
        tomisakae_content = get_tomisakae_profile()
        tomisakae_path = os.path.join(install_dir, "tomisakae.json")
        with open(tomisakae_path, "w", encoding="utf-8") as f:
            json.dump(tomisakae_content, f, indent=4, ensure_ascii=False)
            
        # Thêm phần tạo và lưu cấu hình mặc định
        default_settings = {
            "minecraft_version": "1.20.4",
            "host": "127.0.0.1",
            "port": 55916, 
            "auth": "offline",
            "profiles": ["./tomisakae.json"],
            "load_memory": False,
            "init_message": "xin chào thế giới và tên bạn",
            "language": "vi",
            "show_bot_views": False,
            "allow_insecure_coding": False,
            "code_timeout_mins": 10,
            "max_messages": 15,
            "max_commands": -1,
            "verbose_commands": True,
            "narrate_behavior": True
        }
        
        # Lưu settings.js nếu chưa tồn tại
        settings_path = os.path.join(install_dir, "settings.js")
        if not os.path.exists(settings_path):
            settings_content = "export default\n" + json.dumps(default_settings, indent=4)
            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(settings_content)
                
        # Tạo keys.json mặc định nếu chưa tồn tại
        keys_path = os.path.join(install_dir, "keys.json")
        if not os.path.exists(keys_path):
            default_keys = {
                "OPENAI_API_KEY": "",
                "GEMINI_API_KEY": "",
                "ANTHROPIC_API_KEY": "",
                "REPLICATE_API_KEY": "",
                "HUGGINGFACE_API_KEY": "",
                "GROQCLOUD_API_KEY": "",
                "XAI_API_KEY": ""
            }
            with open(keys_path, "w", encoding="utf-8") as f:
                json.dump(default_keys, f, indent=4)
                
        
        update_status("Cài đặt hoàn tất!", 100)
        return True
        
    except Exception as e:
        raise Exception(f"Không thể cài đặt Mindcraft: {str(e)}")

def uninstall_mindcraft(install_dir):
    try:
        # Xóa shortcut
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, "Mindcraft.lnk")
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            
        # Xóa thư mục cài đặt
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
            
        return True
    except Exception as e:
        raise Exception(f"Không thể gỡ cài đặt Mindcraft: {str(e)}")

def check_installation(install_dir):
    """Kiểm tra xem Mindcraft đã được cài đặt đúng cách chưa"""
    required_files = [
        "package.json",
        "node_modules",
        "main.js",
        "keys.json"
    ]
    
    for file in required_files:
        if not os.path.exists(os.path.join(install_dir, file)):
            return False
    return True

def repair_installation(install_dir, update_status):
    """Sửa chữa cài đặt bị lỗi"""
    try:
        update_status("Đang sửa chữa cài đặt...", 0)
        
        # Xóa node_modules và các file build
        paths_to_remove = ['node_modules', 'dist', '.next', 'build']
        for path in paths_to_remove:
            full_path = os.path.join(install_dir, path)
            if os.path.exists(full_path):
                shutil.rmtree(full_path)
                
        # Cài đặt lại dependencies
        update_status("Đang cài đặt lại dependencies...", 30)
        subprocess.run(['npm', 'install'], cwd=install_dir, check=True)
        
        # Build lại project
        update_status("Đang build lại project...", 60)
        subprocess.run(['npm', 'build'], cwd=install_dir, check=True)
        
        update_status("Sửa chữa hoàn tất!", 100)
        return True
        
    except Exception as e:
        raise Exception(f"Không thể sửa chữa cài đặt: {str(e)}")