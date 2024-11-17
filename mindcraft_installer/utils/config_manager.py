import json
import os
from .api_manager import APIManager

def load_config(install_dir):
    try:
        keys_path = os.path.join(install_dir, "keys.json")
        with open(keys_path, "r") as f:
            return json.load(f)
    except:
        return None

def save_config(install_dir, api_type, api_key):
    try:
        keys_path = os.path.join(install_dir, "keys.json")
        
        # Tạo config với tất cả key rỗng
        default_config = {config["key"]: "" for api, config in APIManager.API_TYPES.items()}
        
        # Chỉ cập nhật key cho API được chọn
        if api_type in APIManager.API_TYPES:
            key_name = APIManager.API_TYPES[api_type]["key"]
            default_config[key_name] = api_key
            
        with open(keys_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
            
        return True
    except Exception as e:
        raise Exception(f"Không thể lưu cấu hình: {str(e)}")

def save_last_install_dir(install_dir):
    try:
        # Lưu vào thư mục %APPDATA% hoặc ~/.config
        config_dir = os.path.join(os.path.expanduser('~'), '.mindcraft')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'config.json')
        config = {}
        
        # Load config cũ nếu có
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
        config['last_install_dir'] = install_dir
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu cấu hình: {str(e)}")
        return False

def load_last_install_dir():
    try:
        config_path = os.path.join(os.path.expanduser('~'), '.mindcraft', 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('last_install_dir')
    except Exception as e:
        print(f"Lỗi khi đọc cấu hình: {str(e)}")
    return None