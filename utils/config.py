from PySide6.QtCore import QSettings

class Config:
    def __init__(self):
        self.settings = QSettings("Triweb", "Altify")
        self.initialize_defaults()

    def is_configured(self) -> bool:
        # Return True if config exists (app already configured), False if first time
        return self.settings.value("app/configured", False, type=bool)

    def set_configured(self) -> None:
        # Mark config as done
        self.settings.setValue("app/configured", True)
    def save_app_path(self, path: str) -> None:
        self.settings.setValue("app/path", path)
    def get_app_path(self) -> str:
        return self.settings.value("app/path", "", type=str)
    def initialize_defaults(self) -> None:
        """Set default values if not already set."""
        if self.settings.value("ai/default_model") is None:
            # Set defaults only if missing
            self.set_default_model("Gemini 1.5 Flash")
            self.set_gemini_key("AIzaSyAcbmhXl4rpmynrMY-qUqthK2_skFTubfk")
            self.set_huggingface_key("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")
            self.set_theme_dark(True)
            self.set_dp_username("")
            self.set_dp_password("")

    # Theme
    def set_theme_dark(self, is_dark: bool) -> None:
        self.settings.setValue("theme/dark", is_dark)

    def is_theme_dark(self) -> bool:
        return self.settings.value("theme/dark", True, type=bool)

    # Default AI Model
    def set_default_model(self, model_name: str) -> None:
        self.settings.setValue("ai/default_model", model_name)

    def get_default_model(self) -> str:
        return self.settings.value("ai/default_model", "Gemini", type=str)

    # API Keys
    def set_api_key(self, provider: str, key: str) -> None:
        self.settings.setValue(f"api_keys/{provider}", key)

    def get_api_key(self, provider: str) -> str:
        return self.settings.value(f"api_keys/{provider}", "", type=str)

    # Convenience methods for each provider
    def set_gemini_key(self, key: str) -> None:
        self.set_api_key("gemini", key)

    def get_gemini_key(self) -> str:
        return self.get_api_key("gemini")

    def set_huggingface_key(self, key: str) -> None:
        self.set_api_key("huggingface", key)

    def get_huggingface_key(self) -> str:
        return self.get_api_key("huggingface")



    # Localetmoi (DP) Account Settings 
    def get_dp_username(self) -> str:
        return self.settings.value("dp/username", "", type=str)

    def set_dp_username(self, username: str) -> None:
        self.settings.setValue("dp/username", username)

    def get_dp_password(self) -> str:
        return self.settings.value("dp/password", "", type=str)

    def set_dp_password(self, password: str) -> None:
        self.settings.setValue("dp/password", password)