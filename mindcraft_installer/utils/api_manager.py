class APIManager:
    DEFAULT_API = "Gemini"
    
    API_TYPES = {
        "Gemini": {
            "enabled": True,
            "key": "GEMINI_API_KEY"
        },
        "OpenAI": {
            "enabled": False,
            "key": "OPENAI_API_KEY"
        },
        "Anthropic": {
            "enabled": False,
            "key": "ANTHROPIC_API_KEY"
        },
        "Replicate": {
            "enabled": False,
            "key": "REPLICATE_API_KEY"
        },
        "Hugging Face": {
            "enabled": False,
            "key": "HUGGINGFACE_API_KEY"
        },
        "Groq": {
            "enabled": False,
            "key": "GROQCLOUD_API_KEY"
        },
        "Ollama": {
            "enabled": False,
            "key": "XAI_API_KEY"
        }
    }
    
    @classmethod
    def get_enabled_apis(cls):
        return [api for api, config in cls.API_TYPES.items() if config["enabled"]]