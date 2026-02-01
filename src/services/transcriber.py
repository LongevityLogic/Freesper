from openai import OpenAI
from src.utils.config import Config
import os
import threading

class Transcriber:
    _local_model = None
    _local_model_name = None
    _model_lock = threading.Lock()

    def __init__(self):
        pass

    def transcribe(self, audio_path, language=None, return_segments=False):
        backend = Config.get_transcriber_backend()
        
        if backend == "local":
            return self._transcribe_local(audio_path, language, return_segments)
        else:
            return self._transcribe_api(audio_path, language, return_segments)

    def _transcribe_api(self, audio_path, language=None, return_segments=False):
        api_key = Config.get_openai_api_key()
        if not api_key:
            raise ValueError("OpenAI API Key is missing. Please set it in Settings.")

        client = OpenAI(api_key=api_key)
        
        if not os.path.exists(audio_path):
             raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if language == "Auto":
            language = None
            
        args = {
            "model": "whisper-1",
            "file": open(audio_path, "rb") 
        }
        
        if return_segments:
            args["response_format"] = "verbose_json"
            
        try:
            with open(audio_path, "rb") as audio_file:
                args["file"] = audio_file
                if language:
                    args["language"] = language
                
                transcript = client.audio.transcriptions.create(**args)
            
            if return_segments:
                return getattr(transcript, 'segments', [])
            else:
                return transcript.text
        except Exception as e:
            print(f"API Transcription error: {e}")
            raise e

    def _transcribe_local(self, audio_path, language=None, return_segments=False):
        from faster_whisper import WhisperModel
        import ctranslate2

        model_size = Config.get_local_model_size()
        
        if language == "Auto":
            language = None

        # Windows DLL Fix: Add nvidia libs to PATH
        if os.name == 'nt':
            import site
            try:
                # Add site-packages/nvidia/*/bin to PATH
                for p in site.getsitepackages():
                    nvidia_dir = os.path.join(p, "nvidia")
                    if os.path.exists(nvidia_dir):
                         for root, dirs, files in os.walk(nvidia_dir):
                             if 'bin' in dirs:
                                 bin_path = os.path.join(root, 'bin')
                                 if bin_path not in os.environ["PATH"]:
                                     os.environ["PATH"] += os.pathsep + bin_path
                                     print(f"Added DLL path: {bin_path}", flush=True)
            except Exception as e:
                print(f"Warning: Failed to patch DLL paths: {e}", flush=True)

        with self._model_lock:
            if Transcriber._local_model is None or Transcriber._local_model_name != model_size:
                print(f"Loading local faster-whisper model: {model_size}...", flush=True)
                
                try:
                    import ctypes
                    
                    print("Checking for CUDA device...", flush=True)
                    cuda_count = ctranslate2.get_cuda_device_count()
                    print(f"CUDA count: {cuda_count}", flush=True)
                    
                    device = "cuda" if cuda_count > 0 else "cpu"
                    
                    # Windows specific check for zlibwapi (Removed to avoid false negatives)
                    # if device == "cuda" and os.name == 'nt': ... (User confirmed DLL exists)

                
                    # RTX 5090 (CC 12.0) detection issue with INT8 in CTranslate2 4.x
                    if device == "cuda":
                        compute_type = "float16"
                    else:
                        compute_type = "int8"
                    
                    print(f"Using device: {device}, compute_type: {compute_type}", flush=True)
                    
                    print("Initializing WhisperModel...", flush=True)
                    try:
                        Transcriber._local_model = WhisperModel(model_size, device=device, compute_type=compute_type)
                    except Exception as e:
                         print(f"Initial load failed with {compute_type}, retrying with 'default'...", flush=True)
                         Transcriber._local_model = WhisperModel(model_size, device=device, compute_type="default")

                         
                    Transcriber._local_model_name = model_size
                    print("Model loaded successfully.", flush=True)
                except Exception as e:
                    print(f"FAILED to load model: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
                    raise e
        
        print("Starting local transcription...")
        
        segments_generator, info = Transcriber._local_model.transcribe(
            audio_path, 
            beam_size=5, 
            language=language
        )
        
        # faster-whisper returns a generator, so we must consume it here
        segments = list(segments_generator)
        
        if return_segments:
            # Normalize to match API/prev structure (dicts mostly)
            # faster-whisper Segment(start, end, text, ...)
            normalized = []
            for s in segments:
                normalized.append({
                    'start': s.start,
                    'end': s.end,
                    'text': s.text.strip()
                })
            return normalized
        else:
            # Join text
            text = " ".join([s.text for s in segments])
            return text.strip()
