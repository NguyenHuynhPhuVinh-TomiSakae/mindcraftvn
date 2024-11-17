import json
import os

def load_settings(install_dir):
    try:
        settings_path = os.path.join(install_dir, "settings.js")
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Giữ lại comments bằng cách chỉ lấy phần JSON
                json_str = content.split("export default")[1].strip()
                # Loại bỏ comments trong JSON
                lines = json_str.split('\n')
                clean_lines = [line.split('//')[0].strip() for line in lines]
                clean_json = '\n'.join(clean_lines)
                return json.loads(clean_json)
        return None
    except:
        return None

def save_settings(install_dir, settings):
    try:
        settings_path = os.path.join(install_dir, "settings.js")
        
        # Tạo nội dung JavaScript với comments
        settings_content = """export default
    {
        "minecraft_version": "%s", // supports up to 1.21.1
        "host": "%s", // or "localhost", "your.ip.address.here" 
        "port": %s,
        "auth": "%s", // or "microsoft"
        "profiles": ["%s"],
        "load_memory": %s, // load memory from previous session
        "init_message": "%s", // sends to all on spawn
        "language": "%s", // translate to/from this language
        "show_bot_views": %s, // show bot's view in browser
        "allow_insecure_coding": %s, // allows model to write/run code. enable at own risk
        "code_timeout_mins": 10, // minutes code is allowed to run. -1 for no timeout
        "max_messages": 15, // max number of messages to keep in context
        "max_commands": -1, // max number of commands to use in a response. -1 for no limit
        "verbose_commands": true, // show full command syntax
        "narrate_behavior": true // chat simple automatic actions
    }""" % (
            settings.get("minecraft_version", "1.20.4"),
            settings.get("host", "127.0.0.1"),
            settings.get("port", "55916"),
            settings.get("auth", "offline"),
            settings.get("profile", "./tomisakae.json"),
            str(settings.get("load_memory", False)).lower(),
            settings.get("init_message", "xin chào thế giới và tên bạn"),
            settings.get("language", "vi"),
            str(settings.get("show_bot_views", False)).lower(),
            str(settings.get("allow_insecure_coding", False)).lower()
        )
        
        # Ghi file với encoding utf-8
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(settings_content)
            
        return True
    except Exception as e:
        print(f"Lỗi khi lưu settings.js: {str(e)}")
        return False