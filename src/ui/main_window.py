import threading
import sys
import os
import subprocess
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                               QLabel, QHBoxLayout, QMessageBox, QApplication, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QIcon, QAction, QPixmap

from src.ui.settings_window import SettingsWindow
from src.ui.styles import Styles
from src.services.audio_recorder import AudioRecorder
from src.services.transcriber import Transcriber
from src.services.text_injector import TextInjector
from src.services.hotkey_manager import HotkeyManager
from src.utils.config import Config

# V3/V5 Imports
from src.services.conference_recorder import ConferenceRecorder
from src.services.conference_transcriber import ConferenceTranscriber
from src.services.report_generator import ReportGenerator
from src.services.system_recorder import SystemRecorder

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
            # Standard mode: don't auto-enter
            self.injector.inject(text, modes, append_enter=False)
            
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))

class InterviewProcessingThread(QThread):
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
            print(f"Interview Mode: Transcribing system audio...")
            
            text = self.transcriber.transcribe(self.audio_file, language=language)
            print(f"Transcribed System: {text}")
            
            modes = ["cursor"] # Interview mode forces typing
            # Auto-Enter is TRUE
            self.injector.inject(text, modes, append_enter=True)
            
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
        self.setFixedSize(300, 260) # Increased height for Mode dropdown
        
        icon_path = os.path.join("assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setStyleSheet(Styles.MAIN_WINDOW)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Recorders
        self.recorder = AudioRecorder()
        self.conf_recorder = ConferenceRecorder()
        self.sys_recorder = SystemRecorder()
        self.is_recording = False
        
        self.init_ui()
        self.apply_transparency()
        
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
        
        # Mode Selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Dictation (Mic)", "Interview (Sys)", "Conference (Dual)"])
        self.mode_combo.setCurrentIndex(0)
        mode_layout.addWidget(self.mode_combo)
        
        layout.addLayout(mode_layout)
        
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
        # Stealth Button
        self.stealth_btn = QPushButton("👻")
        self.stealth_btn.setFixedSize(30, 30)
        self.stealth_btn.setToolTip("Stealth Mode (Minimize to Tray)")
        self.stealth_btn.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #555555; 
                font-size: 16px; 
                border: none; 
            } 
            QPushButton:hover { color: #aaaaaa; }
        """)
        self.stealth_btn.clicked.connect(self.toggle_stealth)
        settings_layout.addWidget(self.stealth_btn)
        
        settings_layout.addWidget(self.settings_btn)
        
        layout.addLayout(settings_layout)
        
        # System Tray
        self.init_tray()
        
        # Stealth Hotkey
        self.stealth_hotkey_manager = None
        
    def init_tray(self):
        from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join("assets", "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Fallback icon if missing
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
            
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_stealth()

    def toggle_stealth(self):
        if self.isVisible():
            self.hide()
        else:
            self.show_window()

    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def setup_hotkey(self):
        # Record Hotkey
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        
        hotkey_str = Config.get_hotkey()
        if hotkey_str:
            self.hotkey_manager = HotkeyManager(hotkey_str, self.on_hotkey_triggered)
            self.hotkey_manager.start()
            
        # Stealth Hotkey
        if self.stealth_hotkey_manager:
            self.stealth_hotkey_manager.stop()
            
        stealth_key = Config.get_stealth_hotkey()
        if stealth_key:
            self.stealth_hotkey_manager = HotkeyManager(stealth_key, self.toggle_stealth)
            self.stealth_hotkey_manager.start()

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
        self.mode_combo.setEnabled(False) # Lock mode while recording
        
        mode = self.mode_combo.currentText()
        
        if "Dictation" in mode:
            self.recorder.start_recording()
        elif "Interview" in mode:
            self.sys_recorder.start_recording()
        elif "Conference" in mode:
            self.conf_recorder.start_recording()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.record_btn.setStyleSheet(Styles.RECORD_BUTTON_IDLE)
        self.status_label.setText("Processing...")
        self.record_btn.setEnabled(False) 
        self.mode_combo.setEnabled(True)
        
        mode = self.mode_combo.currentText()
        
        if "Dictation" in mode:
            audio_file = self.recorder.stop_recording()
            self.worker = AudioProcessingThread(audio_file)
            self.worker.finished.connect(self.on_process_finished)
            
        elif "Interview" in mode:
            # System Only -> Text -> Enter
            audio_file = self.sys_recorder.stop_recording()
            self.worker = InterviewProcessingThread(audio_file)
            self.worker.finished.connect(self.on_process_finished)
            
        elif "Conference" in mode:
            mic_path, sys_path = self.conf_recorder.stop_recording()
            self.worker = ConferenceProcessingThread(mic_path, sys_path)
            self.worker.finished.connect(self.on_conf_finished)
            
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
            if sys.platform == 'win32':
                os.startfile(report_path)
            else:
                subprocess.call(('xdg-open', report_path))

    def on_process_error(self, err_msg):
        self.status_label.setText("Error")
        self.record_btn.setEnabled(True)
        self.mode_combo.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Processing failed: {err_msg}")

    def open_settings(self):
        dlg = SettingsWindow(self)
        if dlg.exec():
            self.setup_hotkey()
            self.apply_transparency()

    def apply_transparency(self):
        opacity = Config.get_transparency()
        self.setWindowOpacity(opacity)

    def closeEvent(self, event):
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        if self.stealth_hotkey_manager:
            self.stealth_hotkey_manager.stop()
        super().closeEvent(event)
