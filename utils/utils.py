import os
import random
from PySide6.QtCore import Qt, QTimer 
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QApplication, QCompleter 
)
from PySide6.QtGui import QFont

from qfluentwidgets import (PushButton, ToolButton, FluentIcon,
    TitleLabel, BodyLabel, InfoBar, InfoBarPosition, SwitchButton, CaptionLabel , SubtitleLabel , setFont , LineEdit , Slider , ComboBox
)
from typing import List

def copy_text_to_clipboard(self, index: int) -> None:
    if 0 <= index < len(self.result_items):
        text = self.result_items[index].text()
        app = QApplication.instance()
        if not app: 
            print("QApplication instance not found for clipboard.")
            return
        clipboard = app.clipboard()
        clipboard.setText(text)
        InfoBar.success(
            title="Copied!", content=f"'{text}' copied to clipboard.",
            orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=2000, parent=self
        ).show()
    else:
        InfoBar.warning(
            title="Copy Error", content="Invalid result item index selected.",
            orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=2000, parent=self
        ).show()




def create_crea_folders(base_path):
    main_folder = os.path.join(base_path, "crea")
    subfolders = ["psd", "images", "adobe stock", "redact", "visibility"]

    try:
        os.makedirs(main_folder, exist_ok=True)
        for folder in subfolders:
            os.makedirs(os.path.join(main_folder, folder), exist_ok=True)
        print(f"Created folders in {main_folder}")
    except Exception as e:
        print(f"Failed to create folders: {e}")
