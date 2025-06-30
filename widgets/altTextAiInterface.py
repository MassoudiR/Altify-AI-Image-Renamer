import os
import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QApplication, QCompleter
)
from PySide6.QtGui import QFont

from qfluentwidgets import (PushButton, ToolButton, FluentIcon,
    TitleLabel, BodyLabel, InfoBar, InfoBarPosition, SwitchButton, CaptionLabel , SubtitleLabel , setFont , LineEdit , Slider , ComboBox , SearchLineEdit
)
from typing import List
from utils.utils import copy_text_to_clipboard
from utils.constants import Constants
from .custom_widgets import DragDropLabel
from services.fetch_dp_services import DPClient



class AltTextAiInterface(QWidget):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.result_items: List[BodyLabel] = []
        self.loading_infobar = None
        self._setup_ui() # self.drag_drop_area will be initialized here

    def _setup_ui(self) -> None:
        """Initializes the main user interface components and layout."""
        self._create_layouts()
        self._add_widgets_to_layouts()
        self._connect_signals() # Currently empty, can be expanded or removed if not used

    def _create_layouts(self) -> None:
        """Creates and configures the main layouts for the window."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 25, 40, 25)
        self.main_layout.setSpacing(20)
        self.main_layout.setAlignment(Qt.AlignTop)

        self.top_input_layout = QHBoxLayout()
        self.bottom_layout = QVBoxLayout()
        self.settings_layout = QVBoxLayout()
        self.results_layout = QVBoxLayout()

    def _add_widgets_to_layouts(self) -> None:
        """Adds widgets to their respective layouts."""
        self._add_header_widgets()
        self._add_top_input_line_widgets()
        # self.drag_drop_area is initialized in _add_top_input_line_widgets()
        # and then added to the main_layout here.
        self.main_layout.addWidget(self.drag_drop_area)
        self._add_settings_bar_widgets()

        self._add_results_section_widgets()
        self._add_regenerate_button()

        self.main_layout.addLayout(self.bottom_layout)

    def _add_header_widgets(self) -> None:
        """Adds title and description labels to the header."""


        title_label = TitleLabel('Altify App')
        setFont(title_label, 24, QFont.Bold)

        description_label = SubtitleLabel("Generate alt text for images using AI")
        setFont(description_label, 14)

        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(description_label)

    def _add_top_input_line_widgets(self) -> None:
        """Adds the multiple LineEdits, ToolButton, and DragDropLabel."""
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

        self.upload_cdc_button = ToolButton(FluentIcon.FOLDER)
        self.upload_cdc_button.setToolTip("Upload CDC")
        self.upload_cdc_button.clicked.connect(self._upload_cdc_file)
        self.top_input_layout.addWidget(self.upload_cdc_button)

        self.main_layout.addLayout(self.top_input_layout)

        self.drag_drop_area = DragDropLabel(self)


    def _add_settings_bar_widgets(self) -> None:
        """Adds the settings bar with sliders, switch, and combobox."""

        alt_length_layout = QHBoxLayout()
        self.alt_length_label = CaptionLabel(f"Max Alt Length: {Constants.ALT_MAX_LENGTH_DEFAULT} Characters")
        self.alt_length_slider = Slider(Qt.Horizontal)
        self.alt_length_slider.setRange(Constants.ALT_MAX_LENGTH_MIN, Constants.ALT_MAX_LENGTH_MAX)
        self.alt_length_slider.setValue(Constants.ALT_MAX_LENGTH_DEFAULT)
        self.alt_length_slider.setSingleStep(1)
        self.alt_length_slider.valueChanged.connect(self._update_alt_length_label)
        alt_length_layout.addWidget(self.alt_length_label)
        alt_length_layout.addWidget(self.alt_length_slider)
        self.settings_layout.addLayout(alt_length_layout)

        consolidated_settings_line = QHBoxLayout()

        self.result_number_label = CaptionLabel(f"Results: {Constants.RESULT_NUMBER_DEFAULT}")
        self.result_number_slider = Slider(Qt.Horizontal)
        self.result_number_slider.setRange(Constants.RESULT_NUMBER_MIN, Constants.RESULT_NUMBER_MAX)
        self.result_number_slider.setValue(Constants.RESULT_NUMBER_DEFAULT)
        self.result_number_slider.setSingleStep(1)
        self.result_number_slider.setTickInterval(1)
        self.result_number_slider.setTickPosition(Slider.TicksBelow) # type: ignore
        self.result_number_slider.valueChanged.connect(self._update_result_number_label)
        consolidated_settings_line.addWidget(self.result_number_label)
        consolidated_settings_line.addWidget(self.result_number_slider)
        consolidated_settings_line.addStretch(1)

        self.include_address_switch = SwitchButton(self)
        self.include_address_switch.setChecked(True)
        self.include_address_switch.setText("Include Address")
        consolidated_settings_line.addWidget(self.include_address_switch)
        consolidated_settings_line.addStretch(1)

        ai_model_label = CaptionLabel("AI Model:")
        self.ai_model_combo = ComboBox()
        self.ai_model_combo.addItems(Constants.AI_MODELS_DICT.keys())
        self.ai_model_combo.setFixedHeight(30)
        consolidated_settings_line.addWidget(ai_model_label)
        consolidated_settings_line.addWidget(self.ai_model_combo)
        consolidated_settings_line.addStretch(1)

        self.settings_layout.addLayout(consolidated_settings_line)
        self.main_layout.addLayout(self.settings_layout)


    def _update_alt_length_label(self, value: int) -> None:
        """Updates the label text for the alt text max length slider."""
        self.alt_length_label.setText(f"Max Alt Length: {value} Characters")

    def _update_result_number_label(self, value: int) -> None:
        """Updates the label text for the number of results slider and adjusts result items."""
        self.result_number_label.setText(f"Results: {value}")
        self._adjust_result_items_count(value)


    def _adjust_result_items_count(self, count: int) -> None:
        """Dynamically adds or removes result item layouts based on the slider value."""
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        self.result_items.clear()

        for i in range(count):
            item_layout = QHBoxLayout()
            text_label = BodyLabel(f"Suggested alt text {i+1}") # Placeholder text
            text_label.setWordWrap(True)
            text_label.setMinimumWidth(300)

            copy_btn = ToolButton(FluentIcon.COPY)
            copy_btn.setToolTip("Copy to clipboard")
            copy_btn.clicked.connect(lambda checked=False, idx=i: copy_text_to_clipboard(self,idx))

            auto_rename_btn = ToolButton(FluentIcon.SAVE_AS)
            auto_rename_btn.setToolTip("Auto Rename Image File")
            auto_rename_btn.clicked.connect(
                lambda checked=False, idx=i: self._auto_rename_image_file(self.result_items[idx].text())
            )

            item_layout.addWidget(text_label)

            item_layout.addStretch()
            item_layout.addWidget(copy_btn)
            item_layout.addWidget(auto_rename_btn)
            self.results_layout.addLayout(item_layout)
            self.result_items.append(text_label)

    def _clear_layout(self, layout) -> None:
        """Helper to clear widgets from a layout recursively."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())


    def _add_results_section_widgets(self) -> None:
        """Adds the 'Results' label and the dynamic result items."""
        self.bottom_layout.addWidget(TitleLabel("Results:"))
        self._adjust_result_items_count(Constants.RESULT_NUMBER_DEFAULT) # Create initial result items
        self.bottom_layout.addLayout(self.results_layout)

    def _add_regenerate_button(self) -> None:
        """Adds the regenerate button."""
        self.regenerate_btn = PushButton("Regenerate")
        self.regenerate_btn.setFixedHeight(36)
        self.regenerate_btn.clicked.connect(self.regenerate_results_with_loading)
        self.bottom_layout.addWidget(self.regenerate_btn)

    def _connect_signals(self) -> None:
        """Connects signals to their respective slots if not connected directly at creation."""
        self.sage_code_input.searchButton.clicked.connect(self._search_sage_code)
        self.sage_code_input.returnPressed.connect(self._search_sage_code)


    def _set_ui_enabled_state(self, enable: bool) -> None:
        """Enables or disables key UI elements during operations."""
        self.regenerate_btn.setEnabled(enable)
        self.activity_input.setEnabled(enable)
        self.address_input.setEnabled(enable)
        self.keywords_input.setEnabled(enable)
        self.sage_code_input.setEnabled(enable)
        self.upload_cdc_button.setEnabled(enable)
        self.alt_length_slider.setEnabled(enable)
        self.result_number_slider.setEnabled(enable)
        self.include_address_switch.setEnabled(enable)
        self.ai_model_combo.setEnabled(enable)
        if hasattr(self, 'drag_drop_area'):
            self.drag_drop_area.setEnabled(enable)

    def _show_loading_infobar(self, title: str, content: str) -> None:
        """Displays a persistent loading InfoBar and disables UI."""
        self._set_ui_enabled_state(False)
        if self.loading_infobar:
            self.loading_infobar.close()
            self.loading_infobar = None

        self.loading_infobar = InfoBar.info(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=False, # Non-closable by user during loading
            position=InfoBarPosition.TOP,
            duration=-1, # Persistent until dismissed programmatically
            parent=self
        )
        self.loading_infobar.show()

    def _dismiss_loading_infobar(self) -> None:
        """Dismisses the active loading InfoBar and re-enables UI."""
        if self.loading_infobar:
            self.loading_infobar.close()
            self.loading_infobar = None
        self._set_ui_enabled_state(True)

    def _upload_cdc_file(self) -> None:
        """Opens a file dialog to upload a CDC file (simulated processing)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Upload CDC File", "", "All Files (*.*)"
        )
        if file_path:
            self._show_loading_infobar("Uploading File...", "Please wait while the file is being processed.")
            QTimer.singleShot(1500, lambda: self._process_uploaded_file(file_path))
        else:
            InfoBar.info(
                title="Upload Cancelled", content="CDC file upload cancelled.",
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=1500, parent=self
            ).show()

    def _process_uploaded_file(self, file_path: str) -> None:
        """Simulates processing the uploaded file and dismisses loading bar."""
        self._dismiss_loading_infobar()
        InfoBar.success(
            title="File Uploaded", content=f"'{os.path.basename(file_path)}' uploaded successfully.",
            orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=2000, parent=self
        ).show()
        print(f"CDC file selected: {file_path}")

    def _auto_rename_image_file(self, alt_text: str) -> None:
        """Attempts to rename the currently loaded image file using the provided alt_text."""
        if not hasattr(self, 'drag_drop_area') or not self.drag_drop_area.current_original_image_path:
            InfoBar.warning(
                title="No Image Loaded", content="Please load an image first to use auto-rename.",
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=2000, parent=self
            ).show()
            return

        image_path = self.drag_drop_area.current_original_image_path
        directory = os.path.dirname(image_path)
        original_filename, file_extension = os.path.splitext(os.path.basename(image_path))

        sanitized_alt_text = "".join(c for c in alt_text if c.isalnum() or c in (' ', '_')).strip()
        sanitized_alt_text = " ".join(sanitized_alt_text.split())
        if not sanitized_alt_text:
            sanitized_alt_text = "untitled_image"

        new_filename = f"{sanitized_alt_text}{file_extension}"
        new_path = os.path.join(directory, new_filename)

        if image_path == new_path:
            InfoBar.info(
                title="Already Renamed", content="File name is already the same as the alt text.",
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=2000, parent=self
            ).show()
            return

        self._show_loading_infobar("Renaming File...", "Please wait while the image is being renamed.")
        QTimer.singleShot(1000, lambda: self._perform_rename_operation(image_path, new_path, new_filename))

    def _perform_rename_operation(self, old_path: str, new_path: str, new_filename: str) -> None:
        """Performs the actual rename operation after a delay."""
        self._dismiss_loading_infobar()
        try:
            # Loop to replace ' ' with '  ' repeatedly until no file conflict
            while os.path.exists(new_path):
                new_filename = new_filename.replace(" ", "  ")
                new_path = os.path.join(os.path.dirname(old_path), new_filename)
                # Prevent infinite loop if no spaces left to replace:
                if " " not in new_filename:
                    break

            os.rename(old_path, new_path)

            if hasattr(self, 'drag_drop_area'):
                self.drag_drop_area.current_original_image_path = new_path
                # Optionally clear processed base64 if needed
                # self.drag_drop_area.current_processed_image_base64 = ""

            InfoBar.success(
                title="File Renamed!",
                content=f"Image renamed to: '{new_filename}'",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            ).show()
            print(f"Renamed '{old_path}' to '{new_path}'")

        except OSError as e:
            InfoBar.error(
                title="Rename Failed",
                content=f"Could not rename file: {e}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            ).show()
            print(f"Error renaming file: {e}")



    def regenerate_results_with_loading(self) -> None:
        """Initiates the alt text generation process with a loading indicator."""
        self._show_loading_infobar("Generating Alt Text...", "Please wait while the AI generates suggestions.")
        # Simulate AI processing delay
        QTimer.singleShot(100, self._run_generation_logic)# Reduced delay for quicker testing

    def _construct_prompt(self) -> str:
        """Constructs a prompt from the user input."""
        parts = []

        activity = self.activity_input.text().strip()
        if activity:
            parts.append(f"Activity: {activity}")

        if self.include_address_switch.isChecked():
            address = self.address_input.text().strip()
            if address:
                parts.append(f"Address: {address}")

        keywords = self.keywords_input.text().strip()
        if keywords:
            parts.append(f"Keywords: {keywords}")
        num_results = self.result_number_slider.value()
        if num_results > 0:
            parts.append(f"number_of_suggestions: {num_results}")
        max_length = self.alt_length_slider.value()
        if max_length > 0:
            parts.append(f"max_length: {max_length}")

        return " | ".join(parts) if parts else "Describe the image."

    def _run_generation_logic(self) -> None:
        """Runs the alt text generation and updates the UI."""
        try:
            prompt = self._construct_prompt()

            if not hasattr(self, 'drag_drop_area') or not self.drag_drop_area.current_processed_image_base64:
                raise ValueError("No image uploaded or processed. Please upload an image first.")

            # Get the selected AI model
            selected_model = self.ai_model_combo.currentText()
            model = Constants.AI_MODELS_DICT.get(selected_model, "gemini-1.5-pro")

            results = model(input_json=prompt, base64_image_str=self.drag_drop_area.current_processed_image_base64)

            for i, (key, value) in enumerate(results.items()):
                if i < len(self.result_items):
                    self.result_items[i].setText(value)
                else:
                    # If there are more results than labels, we can either ignore or create new labels
                    new_label = BodyLabel(value)
                    new_label.setWordWrap(True)
                    self.results_layout.addWidget(new_label)
                    self.result_items.append(new_label)

            InfoBar.success(
                title="Done",
                content="Alt text successfully generated!",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title="Error",
                content=str(e),
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        finally:
            self._set_ui_enabled_state(True)
            if self.loading_infobar:
                self.loading_infobar.close()
                self.loading_infobar = None

    def _search_sage_code(self) -> None:
        """
        Handles the search functionality for the Sage Code input.
        This is where you'd implement your logic to query a database
        or perform a lookup based on the entered Sage Code.
        """
        sage_code = self.sage_code_input.text().strip()
        if not sage_code:
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

        self._show_loading_infobar("Searching...", f"Searching for Sage Code: '{sage_code}'")

        QTimer.singleShot(100, lambda: self._handle_sage_code_search_result(sage_code))

    def _handle_sage_code_search_result(self, sage_code: str) -> None:
      
        client = DPClient()
        success, result = client.get_info(sage_code)
        self._dismiss_loading_infobar()
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
            
            name = result["name"]
            main_locality = result["mainLocality"]
            billingCity = result["billingCity"]
            industry = result["industry"]
            code_ape = result["Libell_code_APE__c"]
            seo_keywords = result["seoKeywords"]
            

            self.activity_input.setText(industry + " - " + code_ape)
            self.address_input.setText(main_locality if main_locality  else billingCity)
            self.keywords_input.setText(seo_keywords)

            InfoBar.success(
                title="Sage Code Found!",
                content=f"{name}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            ).show()
        

      