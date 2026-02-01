import sys
import os
import platform

class AutostartManager:
    APP_NAME = "WhisperTyping"
    
    @staticmethod
    def get_app_path():
        # Handle if running as script or frozen exe (future proof)
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            # Assuming running via bat file or python main.py
            # Best to link to the run_windows.bat if possible, or pythonw + main.py
            # For simplicity, let's point to the run_windows.bat in the current dir
            current_dir = os.getcwd()
            bat_path = os.path.join(current_dir, "run_windows.bat")
            return f'"{bat_path}"'

    @staticmethod
    def is_autostart_enabled():
        if platform.system() != "Windows":
            return False
        
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                 r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                 0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, AutostartManager.APP_NAME)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
        except Exception as e:
            print(f"Autostart check error: {e}")
            return False

    @staticmethod
    def set_autostart(enable: bool):
        if platform.system() != "Windows":
            print("Autostart is only supported on Windows.")
            return

        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                 r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                 0, winreg.KEY_WRITE)
            if enable:
                winreg.SetValueEx(key, AutostartManager.APP_NAME, 0, 
                                  winreg.REG_SZ, AutostartManager.get_app_path())
            else:
                try:
                    winreg.DeleteValue(key, AutostartManager.APP_NAME)
                except FileNotFoundError:
                    pass # Already deleted
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Autostart set error: {e}")
