from pynput.keyboard import Controller, Key
import pyperclip
import time
import platform

class TextInjector:
    def __init__(self):
        self.keyboard = Controller()

    def inject(self, text, modes, append_enter=False):
        # modes is a list, e.g. ['cursor', 'clipboard']
        if not text:
            return

        print(f"Injecting text via {modes}: {text}")

        # Always do clipboard if requested, or if it's the step for cursor
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
        
            if append_enter:
                 time.sleep(0.1)
                 self.keyboard.press(Key.enter)
                 self.keyboard.release(Key.enter)
