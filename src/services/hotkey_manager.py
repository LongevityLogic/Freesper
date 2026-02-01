from pynput import keyboard
import threading
import time

class HotkeyManager:
    def __init__(self, hotkey_str, callback):
        self.hotkey_str = hotkey_str
        self.callback = callback
        self.listener = None
        self.running = False

    def start(self):
        if self.running:
            return
        
        self.running = True
        # Parse hotkey string (e.g. "<ctrl>+<alt>+s")
        # pynput expects strings like '<ctrl>+<alt>+h'
        try:
            self.listener = keyboard.GlobalHotKeys({
                self.hotkey_str: self.on_activate
            })
            self.listener.start()
        except Exception as e:
            print(f"Failed to start hotkey listener: {e}")

    def on_activate(self):
        if self.callback:
            self.callback()

    def stop(self):
        if self.listener:
            self.listener.stop()
        self.running = False

    def update_hotkey(self, new_hotkey):
        self.stop()
        self.hotkey_str = new_hotkey
        self.start()
