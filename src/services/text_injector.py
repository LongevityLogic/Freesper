from pynput.keyboard import Controller, Key
import pyperclip
import time
import platform

class TextInjector:
    def __init__(self):
        self.keyboard = Controller()

    def inject(self, text, modes):
        # modes is a list, e.g. ['cursor', 'clipboard']
        if not text:
            return

        print(f"Injecting text via {modes}: {text}")

        # Always do clipboard if requested, or if it's the step for cursor
        # If 'cursor' is present, we copy to clipboard then paste. 
        # So if 'clipboard' is present AND 'cursor' is present, we just do the cursor logic (which copies)
        # BUT if we want to leave it in clipboard, we should ensure we don't clear it.
        # Logic:
        # 1. Update clipboard content (Required for both usually, unless typing manually)
        # 2. If cursor mode, trigger paste.
        
        # In this simple implementation:
        # 'clipboard' -> calls pyperclip.copy()
        # 'cursor' -> calls pyperclip.copy() AND Ctrl+V.
        
        # So we just need to ensure we copy.
        
        pyperclip.copy(text)
        
        if 'cursor' in modes:
            # Small delay to ensure clipboard is ready
            time.sleep(0.1)
            
            modifier = Key.ctrl
            if platform.system() == 'Darwin':
                modifier = Key.cmd
            
            with self.keyboard.pressed(modifier):
                self.keyboard.press('v')
                self.keyboard.release('v')
        
        # If 'clipboard' in modes, we are done because we already copied.
