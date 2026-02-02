from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QMessageBox, QHBoxLayout, QCheckBox, QStackedWidget, QWidget, QSlider)
from PyQt6.QtCore import Qt
from src.utils.config import Config
from src.ui.styles import Styles
from src.utils.autostart import AutostartManager

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 500)
        self.setStyleSheet(Styles.SETTINGS_WINDOW)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Backend Selection
        self.layout.addWidget(QLabel("Transcriber Backend:"))
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["OpenAI API", "Local Whisper"])
        current_backend = Config.get_transcriber_backend()
        self.backend_combo.setCurrentText("Local Whisper" if current_backend == "local" else "OpenAI API")
        self.backend_combo.currentIndexChanged.connect(self.toggle_backend_ui)
        self.layout.addWidget(self.backend_combo)
        
        # Stacked Widget for Backend Specifics
        self.backend_stack = QStackedWidget()
        self.layout.addWidget(self.backend_stack)
        
        # Page 1: OpenAI API
        self.page_api = QWidget()
        page_api_layout = QVBoxLayout()
        page_api_layout.setContentsMargins(0,0,0,0)
        page_api_layout.addWidget(QLabel("OpenAI API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(Config.get_openai_api_key() or "")
        self.api_key_input.setPlaceholderText("sk-...")
        page_api_layout.addWidget(self.api_key_input)
        self.page_api.setLayout(page_api_layout)
        self.backend_stack.addWidget(self.page_api)
        
        # Page 2: Local Whisper
        self.page_local = QWidget()
        page_local_layout = QVBoxLayout()
        page_local_layout.setContentsMargins(0,0,0,0)
        page_local_layout.addWidget(QLabel("Model Size:"))
        self.model_size_combo = QComboBox()
        self.model_size_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_size_combo.setCurrentText(Config.get_local_model_size())
        page_local_layout.addWidget(self.model_size_combo)
        
        warning_label = QLabel("Note: First run will download the model.\n'Large' requires significant RAM/VRAM.")
        warning_label.setStyleSheet("color: #888; font-size: 11px;")
        warning_label.setWordWrap(True)
        page_local_layout.addWidget(warning_label)
        
        self.page_local.setLayout(page_local_layout)
        self.backend_stack.addWidget(self.page_local)

        # Trigger initial UI state
        self.toggle_backend_ui()

        # Common Settings
        # Language Section
        self.layout.addWidget(QLabel("Default Language:"))
        self.lang_combo = QComboBox()
        languages = ["Auto", "en", "ru", "uk", "de", "fr", "es", "it", "jp", "zh"]
        self.lang_combo.addItems(languages)
        current_lang = Config.get_language()
        if current_lang in languages:
            self.lang_combo.setCurrentText(current_lang)
        self.layout.addWidget(self.lang_combo)

        # Output Mode Section
        self.layout.addWidget(QLabel("Output Mode:"))
        self.cursor_check = QCheckBox("Type at Cursor")
        self.clipboard_check = QCheckBox("Copy to Clipboard")
        
        current_modes = Config.get_output_modes()
        self.cursor_check.setChecked("cursor" in current_modes)
        self.clipboard_check.setChecked("clipboard" in current_modes)
        
        self.layout.addWidget(self.cursor_check)
        self.layout.addWidget(self.clipboard_check)

        # Hotkey Section
        self.layout.addWidget(QLabel("Global Hotkey:"))
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(Config.get_hotkey())
        self.hotkey_input.setPlaceholderText("<ctrl>+<alt>+s")
        self.layout.addWidget(self.hotkey_input)
        
        self.layout.addWidget(QLabel("Stealth Hotkey:"))
        self.stealth_hotkey_input = QLineEdit()
        self.stealth_hotkey_input.setText(Config.get_stealth_hotkey())
        self.stealth_hotkey_input.setPlaceholderText("<ctrl>+<alt>+h")
        self.layout.addWidget(self.stealth_hotkey_input)
        
        # Autostart Section
        self.autostart_check = QCheckBox("Start with Windows")
        if AutostartManager.is_autostart_enabled():
            self.autostart_check.setChecked(True)
        self.layout.addWidget(self.autostart_check)

        # Transparency Section
        self.layout.addWidget(QLabel("Window Transparency:"))
        self.transparency_layout = QHBoxLayout()
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setRange(10, 100) # 10% to 100%
        current_transparency = int(Config.get_transparency() * 100)
        self.transparency_slider.setValue(current_transparency)
        
        self.transparency_label = QLabel(f"{current_transparency}%")
        self.transparency_label.setFixedWidth(40)
        
        self.transparency_slider.valueChanged.connect(lambda v: self.transparency_label.setText(f"{v}%"))
        
        self.transparency_layout.addWidget(self.transparency_slider)
        self.transparency_layout.addWidget(self.transparency_label)
        self.layout.addLayout(self.transparency_layout)

        # Spacer
        self.layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save & Close")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        self.layout.addLayout(btn_layout)

    def toggle_backend_ui(self):
        if self.backend_combo.currentText() == "Local Whisper":
            self.backend_stack.setCurrentWidget(self.page_local)
        else:
            self.backend_stack.setCurrentWidget(self.page_api)

    def save_settings(self):
        # Backend
        backend = "local" if self.backend_combo.currentText() == "Local Whisper" else "openai_api"
        Config.set_transcriber_backend(backend)
        
        if backend == "openai_api":
            api_key = self.api_key_input.text().strip()
            if not api_key:
                QMessageBox.warning(self, "Invalid Input", "API Key cannot be empty for OpenAI backend.")
                return
            Config.set_openai_api_key(api_key)
        else:
            Config.set_local_model_size(self.model_size_combo.currentText())

        # Common
        Config.set_language(self.lang_combo.currentText())
        Config.set_hotkey(self.hotkey_input.text().strip())
        Config.set_stealth_hotkey(self.stealth_hotkey_input.text().strip())
        
        output_modes = []
        if self.cursor_check.isChecked():
            output_modes.append("cursor")
        if self.clipboard_check.isChecked():
            output_modes.append("clipboard")
        Config.set_output_modes(output_modes)

        # Autostart
        AutostartManager.set_autostart(self.autostart_check.isChecked())
        
        # Transparency
        Config.set_transparency(self.transparency_slider.value())
        
        self.accept()
