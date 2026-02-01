import os
import sys
import ctypes

# 1. Enable Verbose Logging for CTranslate2
os.environ["CT2_VERBOSE"] = "1"

def check_dll(name):
    try:
        ctypes.CDLL(name)
        print(f"[OK] {name} loaded.")
    except Exception as e:
        print(f"[ERROR] Failed to load {name}: {e}")

def add_inv_path():
    # Attempt to find nvidia libs in site-packages and add to PATH
    import site
    packages_dirs = site.getsitepackages()
    
    added = False
    for p in packages_dirs:
        nvidia_dir = os.path.join(p, "nvidia")
        if os.path.exists(nvidia_dir):
            print(f"Found NVIDIA directory: {nvidia_dir}")
            for root, dirs, files in os.walk(nvidia_dir):
                if "bin" in dirs or "lib" in dirs:
                     if root not in os.environ["PATH"]:
                         os.environ["PATH"] += os.pathsep + root
                         print(f"Added to PATH: {root}")
                         added = True
    
    # Also generated 'bin' folders inside nvidia packages
    # e.g. site-packages/nvidia/cublas/bin
    return added

def test():
    print("--- ADVANCED DEBUG DIAGNOSTICS ---")
    print(f"Python: {sys.version}")
    
    print("\n[STEP 1] Checking DLL Paths...")
    add_inv_path()
    
    print("\n[STEP 2] Pre-loading dependencies...")
    # These are common dependencies for CTranslate2 / FasterWhisper with CUDA
    check_dll("cublas64_12.dll")
    check_dll("cudnn64_8.dll")
    # zlibwapi is often missing on Windows
    check_dll("zlibwapi.dll") 

    print("\n[STEP 3] Importing Modules...")
    try:
        import ctranslate2
        print(f"CTranslate2 version: {ctranslate2.__version__}")
        print(f"CUDA Devices: {ctranslate2.get_cuda_device_count()}")
    except Exception as e:
        print(f"CTranslate2 Import Fail: {e}")

    try:
        from faster_whisper import WhisperModel
        print("Faster-Whisper imported.")
    except Exception as e:
        print(f"Faster-Whisper Import Fail: {e}")

    print("\n[STEP 4] Loading Model (Simulating Crash)...")
    try:
        # Tring to load large model
        # Using device_index=0 explicitly
        model = WhisperModel("large-v3", device="cuda", compute_type="int8", device_index=0)
        print("SUCCESS: Model Loaded!")
    except Exception as e:
        print(f"FAIL: Model Load Error -> {e}")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"Script Crashed: {e}")
    input("\nPress Enter to exit...")
