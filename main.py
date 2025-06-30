import sys
import os
import ctypes
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout
from qfluentwidgets import (
    SplitFluentWindow, SubtitleLabel, setFont, FluentIcon,
    NavigationItemPosition, isDarkTheme, SwitchButton 
)
from qframelesswindow import FramelessWindow
from utils.theme_utils import apply_theme, load_saved_theme
from widgets.altTextAiInterface import AltTextAiInterface
from widgets.SettingsInterface import SettingsInterface
from widgets.mini_alt import MiniAltInterface
from PySide6.QtGui import QIcon
from utils.utils import create_crea_folders
from utils.context_menu import register_crea_context_menu , create_sendto_shortcut
from utils.config import Config

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join(f'"{arg}"' for arg in sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)


class HomeWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homeInterface")

        self.altTextInterface = AltTextAiInterface(self)

        self.themeSwitch = SwitchButton("Dark Mode", self)
        self.themeSwitch.setChecked(isDarkTheme())
        self.themeSwitch.checkedChanged.connect(self.toggleTheme)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 48, 0, 0)
        layout.addWidget(self.altTextInterface)
        layout.addWidget(self.themeSwitch, alignment=Qt.AlignCenter)

    def toggleTheme(self, checked: bool):
        apply_theme(checked)


class SettingsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsInterface")

        self.settingsInterface = SettingsInterface(self)
        self.settingsInterface.setObjectName("settingsInterface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 48, 0, 0)
        layout.addWidget(self.settingsInterface)


class Window(SplitFluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Altify App')
        icon_path = resource_path("assets/Logo/logo.png")
        self.setWindowIcon(QIcon(icon_path))

        self.resize(900, 700)

        self.homeInterface = HomeWidget(self)
        self.settingsInterface = SettingsWidget(self)
        self.addSubInterface(self.homeInterface, FluentIcon.HOME, "Home")
        self.addSubInterface(self.settingsInterface, FluentIcon.SETTING, "Settings", NavigationItemPosition.BOTTOM)


class MiniWindow(FramelessWindow):
    def __init__(self, image_paths=None):
        super().__init__()
        self.setWindowTitle('Altify App')
        icon_path = resource_path("assets/Logo/logo.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(700, 250)
        self.titleBar.maxBtn.hide()
        self.titleBar.minBtn.hide()
        self.titleBar.closeBtn.raise_()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        self.homeInterface = MiniAltInterface(self, image_paths)
        layout.addWidget(self.homeInterface)


if __name__ == '__main__':
    config = Config()

    if not config.is_configured() and not is_admin():
        run_as_admin()
        sys.exit(0)

    app = QApplication(sys.argv)

    if not config.is_configured():
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        icon_path = resource_path(os.path.join("assets", "Logo", "logo-rounded.ico"))
        register_crea_context_menu(base_path)
        create_sendto_shortcut(os.path.abspath(os.path.join(base_path, "mini_app.exe")), 'Altify Ai Gen', icon_path)
        config.save_app_path(os.path.abspath(sys.argv[0]))
        config.set_configured()


    load_saved_theme()

    args = sys.argv[1:]
    mini_mode = False
    image_paths = None


    if '--create_now_crea' in args:
        idx = args.index('--create_now_crea')
        args.pop(idx)
        if len(args) > idx and not args[idx].startswith('--'):
            base_path = args.pop(idx)
            create_crea_folders(base_path)
        sys.exit(0)

    if '--mini' in args:
        mini_mode = True
        args.remove('--mini')
        image_paths = args  

    if mini_mode:
        w = MiniWindow(image_paths=image_paths)
    else:
        w = Window()
        w.setMicaEffectEnabled(True)

    w.show()
    sys.exit(app.exec())
