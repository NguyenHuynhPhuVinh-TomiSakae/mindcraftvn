import os
import json

class BotConfig:
    def __init__(self, name="TomiSakae", modes=None):
        self.name = name
        self.modes = modes or {
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

def load_bot_config(install_dir):
    try:
        tomisakae_path = os.path.join(install_dir, "tomisakae.json")
        if os.path.exists(tomisakae_path):
            with open(tomisakae_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config
        return None
    except:
        return None

def save_bot_config(install_dir, name, modes):
    try:
        tomisakae_path = os.path.join(install_dir, "tomisakae.json")
        if os.path.exists(tomisakae_path):
            # Đọc cấu hình hiện tại
            with open(tomisakae_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Chỉ cập nhật name và modes
            config["name"] = name
            config["modes"] = modes
            
            # Lưu lại file
            with open(tomisakae_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
    except Exception as e:
        raise Exception(f"Không thể lưu cấu hình bot: {str(e)}")
