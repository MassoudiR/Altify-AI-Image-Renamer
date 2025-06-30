import os
import sys
import ctypes
import shutil
import tempfile
import winreg
import psutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QGraphicsDropShadowEffect
)

from widgets.installerIntreface import Ui_SplashScreen
from PySide6.QtGui import QIcon
import sys
import os
from PySide6.QtGui import QIcon

APP_NAME = "Altify"
SENDTO_NAME = "Altify Ai Gen"
ALTIFY_INSTALL_FOLDER_NAME = "Altify"

def resource_path(relative):
    """ Get absolute path for PyInstaller or normal """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath("."), relative)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Relaunch as admin if needed
if sys.platform == "win32" and not is_admin():
    params = ' '.join([f'"{x}"' for x in sys.argv])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)
    except Exception as e:
        QMessageBox.critical(None, "Admin Required",
                             f"Failed to request administrator privileges.\n\nError: {e}")
        sys.exit(1)

# Registry deletion
def delete_registry(log):
    log("[*] Removing registry context menu entries...")
    command_key = r"Directory\Background\shell\Altify\command"
    main_key = r"Directory\Background\shell\Altify"
    for key in [command_key, main_key]:
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key)
            log(f"[-] Deleted registry key: {key}")
        except FileNotFoundError:
            log(f"[~] Registry key not found: {key}")
        except PermissionError:
            log(f"[!] Permission denied for key: {key}")
        except Exception as e:
            log(f"[!] Error deleting key '{key}': {e}")

# Shortcut deletion
def delete_shortcut(path, log):
    name = os.path.basename(path)
    log(f"[*] Deleting shortcut: {name}")
    if os.path.exists(path):
        try:
            os.remove(path)
            log(f"[-] Deleted: {name}")
        except Exception as e:
            log(f"[!] Error deleting {name}: {e}")
    else:
        log(f"[~] Shortcut not found: {name}")

def delete_sendto(log):
    sendto = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\SendTo', f"{SENDTO_NAME}.lnk")
    delete_shortcut(sendto, log)

def clear_settings(log):
    from PySide6.QtCore import QSettings
    log("[*] Clearing QSettings...")
    try:
        QSettings("Triweb", APP_NAME).clear()
        log("[-] Cleared settings.")
    except Exception as e:
        log(f"[!] Failed to clear settings: {e}")

def create_self_delete_batch(folder_name, uninstaller_path, log):
    target_folder = Path(os.environ["ProgramFiles"]) / folder_name
    temp = tempfile.gettempdir()
    bat = os.path.join(temp, "altify_folder_uninstaller.bat")
    vbs = os.path.join(temp, "altify_folder_uninstaller_launcher.vbs")
    log_file = os.path.join(temp, "altify_uninstall_log.txt")

    if not target_folder.exists() and not os.path.exists(uninstaller_path):
        log(f"[~] Nothing to delete.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    batch = f"""@echo off
timeout /t 5 /nobreak > nul
rmdir /s /q "{target_folder}" 2>nul
if exist "{target_folder}" (
    echo [{timestamp}] [!] Failed to delete: "{target_folder}" >> "{log_file}"
) else (
    echo [{timestamp}] [-] Deleted: "{target_folder}" >> "{log_file}"
)
del "{uninstaller_path}" 2>nul
if exist "{uninstaller_path}" (
    echo [{timestamp}] [!] Failed to delete uninstaller >> "{log_file}"
) else (
    echo [{timestamp}] [-] Uninstaller deleted >> "{log_file}"
)
del "{bat}" 2>nul
del "{vbs}" 2>nul
exit
"""
    with open(bat, 'w') as b: b.write(batch)
    with open(vbs, 'w') as v:
        v.write(f'Set WshShell = CreateObject("WScript.Shell")\n'
                f'WshShell.Run chr(34) & "{bat}" & chr(34), 0, False\n'
                f'Set WshShell = Nothing\n')
    os.system(f'start "" "{vbs}"')
    log("[*] Self-deletion scheduled.")

class UninstallSplash(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self.setWindowTitle("Altify Uninstaller")
        icon_path = resource_path("assets/Logo/logo-fill.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.ui.label_title.setText("<strong>ALTIFY</strong> UNINSTALLER")
        self.ui.label_description.setText("Ready to uninstall.")
        self.ui.label_loading.setText("Waiting for user action...")
        self.ui.start_button.setText("Uninstall Altify")
        self.ui.start_button.clicked.connect(self.uninstall)

        self.target_progress = 0
        self.ui.progressBar.setValue(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_progress)
        self.timer.start(15)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(shadow)

    def animate_progress(self):
        current = self.ui.progressBar.value()
        if current < self.target_progress:
            self.ui.progressBar.setValue(current + 1)
        elif current > self.target_progress:
            self.ui.progressBar.setValue(current - 1)

    def log_msg(self, msg):
        print(msg)

    def uninstall(self):
        # Check if Altify.exe is running
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == "altify.exe":
                    choice = QMessageBox.question(
                        self,
                        "Altify is running",
                        "Altify is currently running.\n\nDo you want to close it to continue uninstallation?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if choice == QMessageBox.Yes:
                        proc.terminate()
                        proc.wait(timeout=5)
                        self.log_msg("[-] Altify.exe terminated.")
                    else:
                        QMessageBox.information(self, "Cancelled", "Uninstallation cancelled.")
                        self.ui.start_button.setEnabled(True)
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        self.ui.start_button.setEnabled(False)
        self.ui.label_description.setText("<strong>REMOVING</strong> FILES")

        self.ui.label_loading.setText("Removing registry entries...")
        self.target_progress = 20
        delete_registry(self.log_msg)

        self.ui.label_loading.setText("Deleting SendTo shortcut...")
        self.target_progress = 40
        delete_sendto(self.log_msg)

        self.ui.label_loading.setText("Clearing settings...")
        self.target_progress = 60
        clear_settings(self.log_msg)

        self.ui.label_loading.setText("Deleting shortcuts...")
        desktop = os.path.expanduser("~/Desktop/Altify.lnk")
        delete_shortcut(desktop, self.log_msg)

        startmenu = os.path.join(os.getenv('APPDATA'), "Microsoft\\Windows\\Start Menu\\Programs", APP_NAME)
        delete_shortcut(os.path.join(startmenu, f"{APP_NAME}.lnk"), self.log_msg)
        delete_shortcut(os.path.join(startmenu, f"Uninstall {APP_NAME}.lnk"), self.log_msg)
        if os.path.exists(startmenu):
            try:
                shutil.rmtree(startmenu)
                self.log_msg(f"[-] Deleted Start Menu folder: {startmenu}")
            except Exception as e:
                self.log_msg(f"[!] Failed to delete Start Menu folder: {e}")

        self.ui.label_loading.setText("Scheduling cleanup...")
        self.target_progress = 90
        create_self_delete_batch(ALTIFY_INSTALL_FOLDER_NAME, sys.argv[0], self.log_msg)

        self.target_progress = 100
        self.ui.label_title.setText("<strong>ALTIFY</strong> UNINSTALLED")
        self.ui.label_description.setText("Altify has been successfully removed.")
        self.ui.label_loading.setText("Uninstaller will now close.")

        QMessageBox.information(self, "Altify Uninstalled",
                                "Altify has been uninstalled.\nThis uninstaller will now close.")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = UninstallSplash()
    window.show()
    sys.exit(app.exec())
