import threading
import sys
import os
import subprocess
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                               QLabel, QHBoxLayout, QMessageBox, QApplication, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QIcon, QAction, QPixmap

from src.ui.settings_window import SettingsWindow
from src.ui.styles import Styles
from src.services.audio_recorder import AudioRecorder
from src.services.transcriber import Transcriber
from src.services.text_injector import TextInjector
from src.services.hotkey_manager import HotkeyManager
from src.utils.config import Config

# V3 Imports
from src.services.conference_recorder import ConferenceRecorder
from src.services.conference_transcriber import ConferenceTranscriber
from src.services.report_generator import ReportGenerator

class AudioProcessingThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file
        self.transcriber = Transcriber()
        self.injector = TextInjector()

    def run(self):
        try:
            language = Config.get_language()
            print(f"Transcribing with language: {language}")
            
            text = self.transcriber.transcribe(self.audio_file, language=language)
            print(f"Transcribed: {text}")
            
            modes = Config.get_output_modes()
            self.injector.inject(text, modes)
            
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))

class ConferenceProcessingThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, mic_path, sys_path):
        super().__init__()
        self.mic_path = mic_path
        self.sys_path = sys_path
        self.transcriber = ConferenceTranscriber()

    def run(self):
        try:
            language = Config.get_language()
            print("Processing Conference Session...")
            segments = self.transcriber.transcribe_session(self.mic_path, self.sys_path, language)
            
            report_path = ReportGenerator.generate_markdown(segments)
            self.finished.emit(report_path)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    request_start = pyqtSignal()
    request_stop = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WhisperTyping")
        self.setFixedSize(300, 220)
        
        icon_path = os.path.join("assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setStyleSheet(Styles.MAIN_WINDOW)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Recorders
        self.recorder = AudioRecorder()
        self.conf_recorder = ConferenceRecorder()
        self.is_recording = False
        
        self.init_ui()
        
        self.hotkey_manager = None
        self.setup_hotkey()

        self.request_start.connect(self.start_recording)
        self.request_stop.connect(self.stop_recording)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Main Record Button
        self.record_btn = QPushButton("🎙️")
        self.record_btn.setFixedSize(80, 80)
        self.record_btn.setStyleSheet(Styles.RECORD_BUTTON_IDLE)
        self.record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_btn.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_btn)
        
        # Conference Toggle
        self.conf_mode_check = QCheckBox("Conference Mode")
        self.conf_mode_check.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        layout.addWidget(self.conf_mode_check, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Settings Button
        settings_layout = QHBoxLayout()
        settings_layout.addStretch()
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #555555; 
                font-size: 16px; 
                border: none; 
            } 
            QPushButton:hover { color: #aaaaaa; }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        settings_layout.addWidget(self.settings_btn)
        
        layout.addLayout(settings_layout)

    def setup_hotkey(self):
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        
        hotkey_str = Config.get_hotkey()
        if hotkey_str:
            self.hotkey_manager = HotkeyManager(hotkey_str, self.on_hotkey_triggered)
            self.hotkey_manager.start()

    def on_hotkey_triggered(self):
        if self.is_recording:
            self.request_stop.emit()
        else:
            self.request_start.emit()

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        if self.is_recording:
            return
        self.is_recording = True
        self.record_btn.setStyleSheet(Styles.RECORD_BUTTON_ACTIVE)
        self.status_label.setText("Recording...")
        
        if self.conf_mode_check.isChecked():
            self.conf_recorder.start_recording()
        else:
            self.recorder.start_recording()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.record_btn.setStyleSheet(Styles.RECORD_BUTTON_IDLE)
        self.status_label.setText("Processing...")
        self.record_btn.setEnabled(False) 
        
        if self.conf_mode_check.isChecked():
            mic_path, sys_path = self.conf_recorder.stop_recording()
            self.worker = ConferenceProcessingThread(mic_path, sys_path)
            self.worker.finished.connect(self.on_conf_finished)
        else:
            audio_file = self.recorder.stop_recording()
            self.worker = AudioProcessingThread(audio_file)
            self.worker.finished.connect(self.on_process_finished)
            
        self.worker.error.connect(self.on_process_error)
        self.worker.start()

    def on_process_finished(self, text):
        self.status_label.setText("Done!")
        self.record_btn.setEnabled(True)

    def on_conf_finished(self, report_path):
        self.status_label.setText("Report Ready!")
        self.record_btn.setEnabled(True)
        
        msg = QMessageBox()
        msg.setWindowTitle("Conference Report")
        msg.setText(f"Report generated successfully:\n{report_path}")
        open_btn = msg.addButton("Open File", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        if msg.clickedButton() == open_btn:
            # Open file with default app
            if sys.platform == 'win32':
                os.startfile(report_path)
            else:
                subprocess.call(('xdg-open', report_path))

    def on_process_error(self, err_msg):
        self.status_label.setText("Error")
        self.record_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Processing failed: {err_msg}")

    def open_settings(self):
        dlg = SettingsWindow(self)
        if dlg.exec():
            self.setup_hotkey()

    def closeEvent(self, event):
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        super().closeEvent(event)
