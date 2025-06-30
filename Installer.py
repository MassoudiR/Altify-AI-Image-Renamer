# -*- coding: utf-8 -*-
################################################################################
# Altify Installer 
################################################################################

import sys
import os
import zipfile
import shutil
from pathlib import Path
import ctypes
import pythoncom
from win32com.shell import shell

from PySide6 import QtCore
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QGraphicsDropShadowEffect
)
from widgets.installerIntreface import Ui_SplashScreen

APP_NAME = "Altify"

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def create_shortcut(target, shortcut_path, icon=None, description=None):
    pythoncom.CoInitialize()
    shell_link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
    )
    shell_link.SetPath(target)
    if icon and os.path.exists(icon):
        shell_link.SetIconLocation(icon, 0)
    if description:
        shell_link.SetDescription(description)
    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(shortcut_path, 0)

def is_running_as_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class SplashInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        self.ui.start_button.clicked.connect(self.start_install)

        self.zip_filelist = []
        self.current_index = 0
        self.target_progress = 0

        self.smooth_timer = QTimer()
        self.smooth_timer.timeout.connect(self.update_progress_bar)
        self.smooth_timer.start(15)

    def update_progress_bar(self):
        current = self.ui.progressBar.value()
        if current < self.target_progress:
            self.ui.progressBar.setValue(current + 1)
        elif current > self.target_progress:
            self.ui.progressBar.setValue(current - 1)

    def start_install(self):
        self.ui.start_button.setEnabled(False)
        self.ui.label_description.setText("<strong>EXTRACTING</strong> FILES")
        self.prepare_extraction()

    def prepare_extraction(self):
        try:
            zip_path = resource_path(f"{APP_NAME}.zip")
            self.ui.label_loading.setText("Reading archive...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                self.zip_filelist = zip_ref.namelist()
            self.total_files = len(self.zip_filelist)
            self.ui.label_loading.setText(f"Extracting {self.total_files} files...")

            self.target_dir = Path(os.environ["ProgramFiles"]) / APP_NAME
            if self.target_dir.exists():
                shutil.rmtree(self.target_dir)
            self.target_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for idx, filename in enumerate(self.zip_filelist):
                    zip_ref.extract(filename, self.target_dir)
                    if "/" not in filename.strip("/\\") or filename.count("/") <= 1:
                        percent = int(((idx + 1) / self.total_files) * 85)  
                        self.target_progress = percent
                        self.ui.label_loading.setText(f"Extracting: {filename}")
                        QApplication.processEvents()

            self.create_shortcuts()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extraction failed: {e}")
            self.close()

    def create_shortcuts(self):
        try:
            altify_exe = self.target_dir / "Altify.exe"
            if altify_exe.exists():
                self.ui.label_description.setText("<strong>CREATING</strong> SHORTCUTS")

                desktop = Path.home() / "Desktop"
                self.ui.label_loading.setText("Creating desktop shortcut...")
                create_shortcut(str(altify_exe), str(desktop / f"{APP_NAME}.lnk"),
                                icon=str(altify_exe), description=f"{APP_NAME} Application")
                self.target_progress = 90

                start_menu = Path(os.environ['APPDATA']) / r'Microsoft\Windows\Start Menu\Programs' / APP_NAME
                start_menu.mkdir(parents=True, exist_ok=True)

                self.ui.label_loading.setText("Creating Start Menu shortcut...")
                create_shortcut(str(altify_exe), str(start_menu / f"{APP_NAME}.lnk"),
                                icon=str(altify_exe), description=f"{APP_NAME} Application")
                self.target_progress = 95

                uninstaller_exe = self.target_dir / "altify_uninstaller.exe"
                if uninstaller_exe.exists():
                    self.ui.label_loading.setText("Creating Start Menu Uninstaller shortcut...")
                    create_shortcut(str(uninstaller_exe), str(start_menu / f"Uninstall {APP_NAME}.lnk"),
                                    description=f"Uninstall {APP_NAME}")

                self.target_progress = 100
                self.ui.label_description.setText("<strong>LAUNCHING</strong> APPLICATION")
                self.ui.label_loading.setText(f"Launching {APP_NAME}...")
                os.startfile(str(altify_exe))

                self.ui.label_title.setText("<strong>ALTIFY</strong> INSTALLED SUCCESSFULLY")

                self.ui.start_button.setText("Close")
                self.ui.start_button.setEnabled(True)
                self.ui.start_button.clicked.disconnect()
                self.ui.start_button.clicked.connect(self.close)

            else:
                QMessageBox.critical(self, "Error", f"{APP_NAME}.exe not found after extraction!")


        except Exception as e:
            QMessageBox.critical(self, "Error", f"Installation failed:\n{e}")
            self.close()


if __name__ == "__main__":
    if not is_running_as_admin():
        params = ' '.join([f'"{x}"' for x in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)

    app = QApplication(sys.argv)
    splash = SplashInstaller()
    splash.show()
    sys.exit(app.exec())
