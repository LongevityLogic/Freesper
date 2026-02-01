import sys
import traceback
import os
import faulthandler

# Enable fault handler to dump traceback on native crash (Segfault)
faulthandler.enable()

# Fix common MKL conflict crash on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# CRITICAL: Import CTranslate2/Faster-Whisper BEFORE PyQt6
# This prevents DLL conflicts (Access Violation) caused by Qt loading incompatible libraries first.
try:
    import ctranslate2
    from faster_whisper import WhisperModel
    print("Pre-loaded CTranslate2/Faster-Whisper successfully.")
except ImportError:
    pass

from PyQt6.QtWidgets import QApplication

def main():
    try:
        from src.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # Optional: Set global font or style tweaks here if needed
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
    except Exception:
        print("CRITICAL ERROR CAUGHT IN MAIN:")
        traceback.print_exc()
        input("Press Enter to close...")

if __name__ == "__main__":
    main()
