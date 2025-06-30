
import os
import base64 
import io 

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import QWidget, QFileDialog, QLabel 
from qfluentwidgets import BodyLabel, InfoBar, InfoBarPosition, isDarkTheme 
from typing import List
from PIL import Image


from utils.constants import Constants 

class DragDropLabel(BodyLabel):
    """
    A QLabel subclass that accepts drag & drop of image files and allows clicking
    to open a file dialog for image selection.
    Processed image is stored as base64.
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._set_default_style()
        self.pixmap: QPixmap = None
        self.current_original_image_path: str = ""
        self.current_processed_image_base64: str = "" # To store the processed image as base64

    def _setup_ui(self) -> None:
        """Sets up the initial UI properties of the label."""
        self.setText("Drag & Drop Image Here\n(or click to select)")
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setFixedHeight(200)

    def _set_default_style(self) -> None:
        """Applies the default dashed border style."""
        border_color = "#BBB" if isDarkTheme() else "#888"
        bg_color = "#333" if isDarkTheme() else "#F0F0F0"
        text_color = "#EEE" if isDarkTheme() else "#444"
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {border_color};
                background-color: {bg_color};
                font-size: 16px;
                color: {text_color};
                cursor: pointer;
            }}
        """)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles mouse press events to open a file dialog."""
        if event.button() == Qt.LeftButton:
            self._open_file_dialog()

    def _open_file_dialog(self) -> None:
        """Opens a QFileDialog for image selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.load_image(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handles drag enter events to check for image data."""
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handles drop events to load images from mime data."""
        if event.mimeData().hasImage():
            InfoBar.warning(
                title="Unsupported Drop",
                content="Direct image data drop not supported for processing. Please drop a file or use file dialog.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.window()
            ).show()
            event.ignore()
        elif event.mimeData().hasUrls():
            urls: List[QUrl] = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                local_path = urls[0].toLocalFile()
                self.load_image(local_path)
                event.acceptProposedAction()
            else:
                InfoBar.warning(
                    title="Unsupported Drop",
                    content="Only local image files can be processed via drag & drop.",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.window()
                ).show()
                event.ignore()
        else:
            event.ignore()

    def _set_pixmap_from_image(self, pixmap: QPixmap) -> None:
        """Scales and sets the pixmap, clearing default styles and text."""
        self.pixmap = pixmap
        self.setPixmap(pixmap.scaled(
            self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        self.setStyleSheet("")
        self.setText("")

    def load_image(self, path: str) -> None:
        """
        Loads an image from the given path, scales it, and updates the label.
        Attempts to process/compress the image and stores it as base64.
        If processing fails, stores the original image as base64.
        """
        if not os.path.exists(path):
            InfoBar.warning(
                title="File Not Found", content=f"The file '{os.path.basename(path)}' does not exist.",
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.window()
            ).show()
            return

        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self._set_pixmap_from_image(pixmap)
            self.current_original_image_path = path
            self.current_processed_image_base64 = "" # Reset

            processed_base64_data = self._process_and_compress_image(path)

            if processed_base64_data:
                self.current_processed_image_base64 = processed_base64_data
                # Success InfoBars for resize/compress are shown within _process_and_compress_image
                # For debugging: print(f"Successfully processed image stored as base64 (first 100 chars): {self.current_processed_image_base64[:100]}")
            else:
                # Processing failed, attempt to load original image as base64
                print(f"Image processing failed for '{os.path.basename(path)}'. Attempting to load and encode original image as a fallback.")
                try:
                    with open(path, "rb") as image_file:
                        original_image_bytes = image_file.read()
                    self.current_processed_image_base64 = base64.b64encode(original_image_bytes).decode('utf-8')
                    InfoBar.warning(
                        title="Processing Fallback",
                        content="Image processing steps failed. Original image has been loaded as base64.",
                        orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3500, parent=self.window()
                    ).show()
                    # For debugging: print(f"Fallback: Original image stored as base64 (first 100 chars): {self.current_processed_image_base64[:100]}")
                except Exception as e_fallback:
                    self.current_processed_image_base64 = "" # Ensure it's cleared if fallback also fails
                    InfoBar.error(
                        title="Image Load Failed",
                        content=f"Could not load or process the image. Error: {e_fallback}",
                        orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self.window()
                    ).show()
                    print(f"Error during fallback to load original image '{os.path.basename(path)}': {e_fallback}")
        else:
            InfoBar.warning(
                title="Invalid Image", content=f"The file '{os.path.basename(path)}' is not a valid image.",
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.window()
            ).show()
            self.current_processed_image_base64 = "" # Ensure cleared if not a valid pixmap

    def _process_and_compress_image(self, original_path: str) -> str | None:
        """
        Attempts to process an image (resize, compress) and returns it as a base64 string.
        Shows InfoBars for successful resize/compression steps.
        Returns the base64 string of the processed image, or None on any processing failure.
        """
        try:
            img = Image.open(original_path)
            original_format = img.format 
            
            if original_format == 'JPEG':
                if img.mode == 'RGBA' or img.mode == 'P':
                    img = img.convert('RGB')
            elif img.mode == 'P' and original_format != 'GIF':
                 img = img.convert('RGBA' if original_format == 'PNG' else 'RGB')
            elif img.mode == 'LA': 
                img = img.convert('RGBA')

            original_size_kb = os.path.getsize(original_path) / 1024
            original_width, original_height = img.size

            needs_resize = original_width > Constants.MAX_DIMENSION or \
                           original_height > Constants.MAX_DIMENSION
            
            temp_buffer_for_size_check = io.BytesIO()
            img_for_size_check = img.copy()

            if needs_resize:
                scaling_factor = min(Constants.MAX_DIMENSION / original_width,
                                     Constants.MAX_DIMENSION / original_height)
                new_width = int(original_width * scaling_factor)
                new_height = int(original_height * scaling_factor)
                img_for_size_check = img_for_size_check.resize((new_width, new_height), Image.LANCZOS)
            
            try:
                save_format_check = original_format if original_format in ['PNG', 'JPEG', 'GIF', 'BMP'] else 'PNG'
                if save_format_check == 'JPEG' and img_for_size_check.mode == 'RGBA':
                     img_for_size_check_converted = img_for_size_check.convert('RGB')
                     img_for_size_check_converted.save(temp_buffer_for_size_check, format='JPEG')
                else:
                    img_for_size_check.save(temp_buffer_for_size_check, format=save_format_check)
                current_size_kb = len(temp_buffer_for_size_check.getvalue()) / 1024
            except Exception as e_save_check:
                print(f"Size check save failed for format {original_format}: {e_save_check}. Falling back to PNG for size check.")
                temp_buffer_for_size_check = io.BytesIO() 
                img_for_size_check.save(temp_buffer_for_size_check, format='PNG') 
                current_size_kb = len(temp_buffer_for_size_check.getvalue()) / 1024
                original_format = 'PNG' 
            
            needs_compress = current_size_kb > Constants.MAX_FILE_SIZE_KB
            
            if needs_resize:
                scaling_factor = min(Constants.MAX_DIMENSION / original_width,
                                     Constants.MAX_DIMENSION / original_height)
                new_width = int(original_width * scaling_factor)
                new_height = int(original_height * scaling_factor)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                InfoBar.info(
                    title="Image Resized",
                    content=f"Dimensions reduced to {new_width}x{new_height}.",
                    orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.window()
                ).show()

            image_buffer = io.BytesIO()
            final_format = original_format if original_format in ['PNG', 'JPEG', 'GIF', 'BMP'] else 'PNG'
            
            if final_format == 'JPEG' and img.mode in ['RGBA', 'P', 'LA']:
                img = img.convert('RGB')

            if needs_compress:
                quality = 90 
                if final_format == 'JPEG':
                    while True:
                        image_buffer.seek(0) 
                        image_buffer.truncate() 
                        try:
                            img.save(image_buffer, format='JPEG', optimize=True, quality=quality)
                            compressed_size_kb = len(image_buffer.getvalue()) / 1024
                            if compressed_size_kb <= Constants.MAX_FILE_SIZE_KB or quality <= 10:
                                break
                            quality -= 10
                        except Exception as e_jpeg_save:
                            print(f"Error saving image at quality {quality} for JPEG: {e_jpeg_save}")
                            image_buffer.seek(0)
                            image_buffer.truncate()
                            # Attempt to re-convert to RGB just in case mode was an issue for this specific save attempt
                            img_rgb_fallback = img.convert('RGB') if img.mode != 'RGB' else img
                            img_rgb_fallback.save(image_buffer, format='PNG') 
                            final_format = 'PNG' 
                            compressed_size_kb = len(image_buffer.getvalue()) / 1024
                            print(f"JPEG save loop failed, fell back to PNG. Size: {compressed_size_kb:.2f}KB")
                            break 
                    
                    InfoBar.info(
                        title=f"Image Compressed ({final_format})",
                        content=f"Size reduced from {original_size_kb:.2f}KB to {compressed_size_kb:.2f}KB (before base64).",
                        orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.window()
                    ).show()
                else: 
                    img.save(image_buffer, format=final_format, optimize=True) 
                    compressed_size_kb = len(image_buffer.getvalue()) / 1024
                    InfoBar.info(
                        title=f"Image Processed ({final_format})",
                        content=f"Original: {original_size_kb:.2f}KB, New: {compressed_size_kb:.2f}KB (before base64).",
                        orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.window()
                    ).show()
            else: 
                img.save(image_buffer, format=final_format)
            
            image_bytes = image_buffer.getvalue()
            base64_encoded_string = base64.b64encode(image_bytes).decode('utf-8')
            return base64_encoded_string

        except Exception as e:
            print(f"Error during image processing steps for '{os.path.basename(original_path)}': {e}")
            return None