import os
import base64
import io
import re
from PIL import Image
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QApplication, QCompleter
)
from PySide6.QtGui import QFont

from qfluentwidgets import (
    PushButton, TitleLabel,
    SubtitleLabel, setFont, LineEdit, SearchLineEdit
)
from services.fetch_dp_services import DPClient
from utils.constants import Constants
from utils.config import Config
import sys
from win10toast import ToastNotifier

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def safe_filename(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text[:100]



class WorkerThread(QThread):
    successSignal = Signal(int) 
    errorSignal = Signal(str)
    finishedSignal = Signal()

    def __init__(self, processed_images, default_model, prompt):
        super().__init__()
        self.processed_images = processed_images
        self.default_model = default_model
        self.prompt = prompt

    def run(self):
        try:
            for original_path, base64image in self.processed_images:
                alt_response = self.default_model(base64_image_str=base64image, input_json=self.prompt)
                if isinstance(alt_response, dict):
                    alt_text = next(iter(alt_response.values()))
                else:
                    alt_text = alt_response

                dir_name = os.path.dirname(original_path)
                ext = os.path.splitext(original_path)[1]
                safe_name = safe_filename(alt_text)
                new_filename = f"{safe_name}{ext}"
                new_file_path = os.path.join(dir_name, new_filename)


                while os.path.exists(new_file_path):
                    new_filename = new_filename.replace(" ", "  ")
                    new_file_path = os.path.join(dir_name, new_filename)
                    if " " not in new_filename:
                        break

                try:
                    os.rename(original_path, new_file_path)
                    print(f"Renamed '{original_path}' to '{new_file_path}'")
                except Exception as e:
                    print(f"Failed to rename '{original_path}' to '{new_file_path}': {e}")


            self.successSignal.emit(len(self.processed_images))
        except Exception as e:
            self.errorSignal.emit(str(e))
        finally:
            self.finishedSignal.emit()


class MiniAltInterface(QWidget):
    def __init__(self, parent: QWidget = None, image_paths=None) -> None:
        super().__init__(parent)
        self.image_paths = image_paths or []
        self.filter_image_paths()
        self.processed_images = []  
        self.config = Config()
        self.default_model = Constants.AI_MODELS_DICT.get(self.config.get_default_model() )
        self.notifier = ToastNotifier()
        self.worker = None
        self.icon_path = resource_path(os.path.join("assets", "Logo", "logo-fill.ico"))
    

        self.setup_ui()
        if self.image_paths:
            self.compress_and_store_images()

    def filter_image_paths(self):
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif' , '.webp')
        filtered_paths = []
        for path in self.image_paths:
            if not os.path.exists(path):
                print(f"File not found and removed: {path}")
                continue
            if not path.lower().endswith(supported_formats):
                print(f"Unsupported format removed: {path}")
                continue
            filtered_paths.append(path)
        self.image_paths = filtered_paths

    def setup_ui(self) -> None:
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle("Altify")
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.connect_signals()

    def create_layouts(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 25, 40, 25)
        self.main_layout.setSpacing(20)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.top_input_layout = QHBoxLayout()

    def add_widgets_to_layouts(self) -> None:
        self.add_header_widgets()
        self.add_top_input_line_widgets()
        self.add_regenerate_button()

    def add_header_widgets(self) -> None:
        title_label = TitleLabel('Altify App')
        setFont(title_label, 24, QFont.Bold)
        description_label = SubtitleLabel(f"{len(self.image_paths)} Selected")
        setFont(description_label, 14)
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(description_label)

    def add_top_input_line_widgets(self) -> None:
        self.activity_input = LineEdit()
        self.activity_input.setPlaceholderText("Activity")
        self.activity_input.setFixedHeight(30)
        activity_completer = QCompleter(Constants.ACTIVITY_TYPES, self.activity_input)
        activity_completer.setCaseSensitivity(Qt.CaseInsensitive)
        activity_completer.setMaxVisibleItems(10)
        self.activity_input.setCompleter(activity_completer)
        self.top_input_layout.addWidget(self.activity_input)

        self.address_input = LineEdit()
        self.address_input.setPlaceholderText("Address")
        self.address_input.setFixedHeight(30)
        self.top_input_layout.addWidget(self.address_input)

        self.keywords_input = LineEdit()
        self.keywords_input.setPlaceholderText("Keywords")
        self.keywords_input.setFixedHeight(30)
        self.top_input_layout.addWidget(self.keywords_input)

        self.sage_code_input = SearchLineEdit()
        self.sage_code_input.setPlaceholderText("Sage Code")
        self.sage_code_input.setFixedHeight(30)
        self.top_input_layout.addWidget(self.sage_code_input)

        self.main_layout.addLayout(self.top_input_layout)

    def add_regenerate_button(self) -> None:
        self.regenerate_btn = PushButton("Generate Data")
        self.regenerate_btn.setFixedHeight(36)
        self.regenerate_btn.clicked.connect(self.generate_data_with_loading)
        self.main_layout.addWidget(self.regenerate_btn)

    def connect_signals(self) -> None:
        self.sage_code_input.searchButton.clicked.connect(self.search_sage_code)
        self.sage_code_input.returnPressed.connect(self.search_sage_code)

    def set_ui_enabled_state(self, enable: bool) -> None:
        self.regenerate_btn.setEnabled(enable)
        self.activity_input.setEnabled(enable)
        self.address_input.setEnabled(enable)
        self.keywords_input.setEnabled(enable)
        self.sage_code_input.setEnabled(enable)

    def compress_and_store_images(self) -> None:
        self.processed_images.clear()
        for img_path in self.image_paths:
            try:
                img = Image.open(img_path)
                if img.mode in ("RGBA", "P", "LA"):
                    img = img.convert("RGB")
                max_dim = 1024
                w, h = img.size
                if w > max_dim or h > max_dim:
                    scale = min(max_dim / w, max_dim / h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", optimize=True, quality=85)
                img_bytes = buffer.getvalue()
                b64_str = base64.b64encode(img_bytes).decode("utf-8")
                self.processed_images.append((img_path, b64_str))
            except Exception as e:
                print(f"Error processing {img_path}: {e}")

    def generate_data_with_loading(self) -> None:
        self.window().hide()
        QApplication.processEvents() 

        self.notifier.show_toast(
            "Altify",
            "Generating data in background...",
            duration=2,
            threaded=True,
            icon_path=self.icon_path
        )

        prompt = self.construct_prompt()
        self.worker = WorkerThread(self.processed_images, self.default_model, prompt)
        self.worker.successSignal.connect(lambda count: self.on_generation_success(count))
        self.worker.errorSignal.connect(lambda msg: self.on_generation_error(msg))
        self.worker.finishedSignal.connect(self.on_generation_finished)
        self.worker.start()

    def on_generation_success(self, count):
        self.notifier.show_toast(
            "Altify",
            f"Generated data for {count} images.",
            duration=5,
            threaded=True,
            icon_path=self.icon_path
        )

    def on_generation_error(self, message):
        self.notifier.show_toast(
            "Altify - Error",
            message,
            duration=5,
            threaded=True,
            icon_path=self.icon_path
        )

    def on_generation_finished(self):
        QApplication.instance().quit()

    def construct_prompt(self) -> str:
        parts = []
        activity = self.activity_input.text().strip()
        if activity:
            parts.append(f"Activity: {activity}")
        address = self.address_input.text().strip()
        if address:
            parts.append(f"Address: {address}")
        keywords = self.keywords_input.text().strip()
        if keywords:
            parts.append(f"Keywords: {keywords}")
        parts.append(f"number_of_suggestions: 1")
        parts.append(f"max_length: {Constants.ALT_MAX_LENGTH_DEFAULT}")
        return " | ".join(parts) if parts else "Generate data."

    def search_sage_code(self) -> None:
        sage_code = self.sage_code_input.text().strip()
        if not sage_code:
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.warning(
                title="Empty Search",
                content="Please enter a Sage Code to search.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            ).show()
            return
        self.set_ui_enabled_state(False)
        QTimer.singleShot(100, lambda: self.handle_sage_code_search_result(sage_code))

    def handle_sage_code_search_result(self, sage_code: str) -> None:
        client = DPClient()
        success, result = client.get_info(sage_code)
        self.set_ui_enabled_state(True)
        from qfluentwidgets import InfoBar, InfoBarPosition
        if not success:
            InfoBar.error(
                title="Search Failed",
                content=f"Error: {result}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            ).show()
        else:
            name = result.get("name", "")
            main_locality = result.get("mainLocality", "")
            billingCity = result.get("billingCity", "")
            industry = result.get("industry", "")
            code_ape = result.get("Libell_code_APE__c", "")
            seo_keywords = result.get("seoKeywords", "")
            self.activity_input.setText(f"{industry} - {code_ape}")
            self.address_input.setText(main_locality if main_locality else billingCity)
            self.keywords_input.setText(seo_keywords)
            InfoBar.success(
                title="Sage Code Found!",
                content=name,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            ).show()
