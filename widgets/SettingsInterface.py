from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
)
from qfluentwidgets import (
    ComboBox, PasswordLineEdit, CaptionLabel, TitleLabel,
    SubtitleLabel, setFont, PushButton, InfoBar, InfoBarPosition
)
from PySide6.QtGui import QFont
from utils.config import Config
from utils.constants import Constants


class SettingsInterface(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.config = Config()
        self._setup_ui()
        self.load_settings()

    def _setup_ui(self) -> None:
        self._create_main_layout()
        self._add_header_widgets()
        self._add_model_selection_widgets()
        self._add_api_key_widgets()
        self._add_dp_user_pass_widgets()
        self._add_save_button()
        self._connect_signals()

    def _create_main_layout(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 25, 40, 25)
        self.main_layout.setSpacing(20)
        self.main_layout.setAlignment(Qt.AlignTop)

    def _add_header_widgets(self) -> None:
        title_label = TitleLabel("Settings")
        setFont(title_label, 24, QFont.Bold)
        self.main_layout.addWidget(title_label)

        description_label = SubtitleLabel(
            "Configure your default AI model and set the API keys for Gemini and Huggingface."
        )
        setFont(description_label, 14)
        self.main_layout.addWidget(description_label)

    def _add_model_selection_widgets(self) -> None:
        model_layout = QHBoxLayout()
        model_label = CaptionLabel("Select Default Model:")
        self.model_combo = ComboBox()
        self.model_combo.setObjectName("model_combo")
        self.model_combo.addItems(Constants.AI_MODELS_DICT.keys())
        self.model_combo.setFixedHeight(30)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        self.main_layout.addLayout(model_layout)

    def _add_api_key_widgets(self) -> None:
        def create_key_layout(label_text, object_name, placeholder):
            layout = QHBoxLayout()
            label = CaptionLabel(label_text)
            label.setMinimumWidth(500)
            line_edit = PasswordLineEdit()
            line_edit.setObjectName(object_name)
            line_edit.setPlaceholderText(placeholder)
            line_edit.setFixedHeight(30)
            layout.addWidget(label)
            layout.addWidget(line_edit)
            self.main_layout.addLayout(layout)
            return line_edit

        self.gemini_key_edit = create_key_layout("Gemini Key:", "gemini_key", "Enter Gemini key")
        self.huggingface_key_edit = create_key_layout("Huggingface Key:", "huggingface_key", "Enter Huggingface key")

    def _add_dp_user_pass_widgets(self) -> None:
        self.main_layout.addSpacing(20)

        dp_section_label = SubtitleLabel("Localetmoi (DP) Account Settings")
        setFont(dp_section_label, 14)
        self.main_layout.addWidget(dp_section_label)

        dp_user_layout = QHBoxLayout()
        dp_user_label = CaptionLabel("DP Username:")
        dp_user_label.setMinimumWidth(500)
        self.dp_username_edit = QLineEdit()
        self.dp_username_edit.setObjectName("dp_username")
        self.dp_username_edit.setPlaceholderText("Enter DP username")
        self.dp_username_edit.setFixedHeight(30)
        dp_user_layout.addWidget(dp_user_label)
        dp_user_layout.addWidget(self.dp_username_edit)
        self.main_layout.addLayout(dp_user_layout)

        dp_pass_layout = QHBoxLayout()
        dp_pass_label = CaptionLabel("DP Password:")
        dp_pass_label.setMinimumWidth(500)
        self.dp_password_edit = PasswordLineEdit()
        self.dp_password_edit.setObjectName("dp_password")
        self.dp_password_edit.setPlaceholderText("Enter DP password")
        self.dp_password_edit.setFixedHeight(30)
        dp_pass_layout.addWidget(dp_pass_label)
        dp_pass_layout.addWidget(self.dp_password_edit)
        self.main_layout.addLayout(dp_pass_layout)

    def _add_save_button(self) -> None:
        self.save_button = PushButton("Save")
        self.save_button.setObjectName("save_button")
        self.save_button.setFixedHeight(36)
        self.main_layout.addWidget(self.save_button)

    def _connect_signals(self) -> None:
        self.save_button.clicked.connect(self._on_save)

    def load_settings(self) -> None:
        self.model_combo.setCurrentText(self.config.get_default_model())
        self.gemini_key_edit.setText(self.config.get_gemini_key())
        self.huggingface_key_edit.setText(self.config.get_huggingface_key())
        self.dp_username_edit.setText(self.config.get_dp_username())
        self.dp_password_edit.setText(self.config.get_dp_password())

    def _on_save(self) -> None:
        self.config.set_default_model(self.model_combo.currentText())
        self.config.set_gemini_key(self.gemini_key_edit.text())
        self.config.set_huggingface_key(self.huggingface_key_edit.text())
        self.config.set_dp_username(self.dp_username_edit.text())
        self.config.set_dp_password(self.dp_password_edit.text())

        InfoBar.success(
            title="Settings Saved",
            content="Your settings have been saved successfully.",
            orient=Qt.Horizontal,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        ).show()
