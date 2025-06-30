from qfluentwidgets import Theme, setTheme
from utils.config import Config

config = Config()

def apply_theme(dark: bool = True):
    setTheme(Theme.DARK if dark else Theme.LIGHT)
    config.set_theme_dark(dark)

def load_saved_theme():
    apply_theme(config.is_theme_dark())
