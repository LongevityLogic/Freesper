import os
import sys
import ctypes
import platform
import shutil

# Enable CTranslate2 verbose logging immediately
os.environ["CT2_VERBOSE"] = "1"

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def find_in_path(filename):
    print(f"Searching for {filename}...")
    found = False
    
    # Check current directory
    if os.path.exists(filename):
        print(f"  [FOUND] ./ {filename}")
        found = True
        
    # Check PATH
    paths = os.environ["PATH"].split(os.pathsep)
    for p in paths:
        if not p: continue
        try:
            full_path = os.path.join(p, filename)
            if os.path.exists(full_path):
                print(f"  [FOUND] {full_path}")
                found = True
        except:
            continue
            
    if not found:
        print(f"  [MISSING] Could not find {filename} in PATH.")
    return found

def check_dll_load(name):
    print(f"Attempting to load {name}...")
    try:
        lib = ctypes.CDLL(name)
        print(f"  [OK] Loaded successfully. Handle: {lib._handle}")
    except OSError as e:
        print(f"  [FAIL] Error loading {name}: {e}")
        # decode winerror if present
        if hasattr(e, 'winerror'):
             print(f"  WinError Code: {e.winerror}")
             if e.winerror == 193:
                 print("  -> ERROR 193 means '%1 is not a valid Win32 application'.")
                 print("  -> You likely have a 32-bit DLL but need 64-bit (or vice versa).")
             elif e.winerror == 126:
                 print("  -> ERROR 126 means 'The specified module could not be found'.")
                 print("  -> The DLL file is missing or one of ITS dependencies is missing.")

def main():
    print_header("SYSTEM INFO")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")
    
    is_64bits = sys.maxsize > 2**32
    print(f"Is 64-bit Python? {is_64bits}")
    
    if not is_64bits:
        print("CRITICAL: You are running 32-bit Python. Faster-Whisper/CUDA requires 64-bit Python!")
        return

    print_header("DLL CHECK")
    # Critical DLLs for NVIDIA/Faster-Whisper
    dlls = ["zlibwapi.dll", "cudnn64_8.dll", "cublas64_12.dll"]
    
    for dll in dlls:
        found = find_in_path(dll)
        if found:
            check_dll_load(dll)
        else:
            print(f"  [WARNING] {dll} not found. This might cause a crash.")

    print_header("LIBRARY IMPORT TEST")
    try:
        import ctranslate2
        print(f"CTranslate2 Version: {ctranslate2.__version__}")
        print(f"CUDA Device Count: {ctranslate2.get_cuda_device_count()}")
    except Exception as e:
        print(f"Failed to import ctranslate2: {e}")

    print_header("MODEL LOAD TEST")
    try:
        from faster_whisper import WhisperModel
        print("Initializing WhisperModel (tiny, CUDA, float16)...")
        # Use tiny for quick testing
        model = WhisperModel("tiny", device="cuda", compute_type="float16")
        print("SUCCESS! Model loaded on GPU.")
    except Exception as e:
        print(f"CRASH/ERROR during model load: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("\nPress Enter to exit...")
