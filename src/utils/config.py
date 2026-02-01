import os
from dotenv import load_dotenv, set_key
from pathlib import Path

# Load env variables from the .env file in the root directory
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

class Config:
    @staticmethod
    def get_openai_api_key():
        return os.getenv("OPENAI_API_KEY")

    @staticmethod
    def set_openai_api_key(key):
        os.environ["OPENAI_API_KEY"] = key
        set_key(ENV_PATH, "OPENAI_API_KEY", key)

    @staticmethod
    def get_output_modes():
        mode_str = os.getenv("OUTPUT_MODE", "cursor")
        return mode_str.split(",") if mode_str else []

    @staticmethod
    def set_output_modes(modes):
        # modes is a list of strings, e.g. ['cursor', 'clipboard']
        mode_str = ",".join(modes)
        os.environ["OUTPUT_MODE"] = mode_str
        set_key(ENV_PATH, "OUTPUT_MODE", mode_str)

    @staticmethod
    def get_language():
        return os.getenv("WHISPER_LANGUAGE", "Auto")

    @staticmethod
    def set_language(lang):
        os.environ["WHISPER_LANGUAGE"] = lang
        set_key(ENV_PATH, "WHISPER_LANGUAGE", lang)

    @staticmethod
    def get_hotkey():
        return os.getenv("GLOBAL_HOTKEY", "<ctrl>+<alt>+s")

    @staticmethod
    def set_hotkey(hotkey):
        os.environ["GLOBAL_HOTKEY"] = hotkey
        set_key(ENV_PATH, "GLOBAL_HOTKEY", hotkey)

    @staticmethod
    def get_transcriber_backend():
        # 'openai_api' or 'local'
        return os.getenv("TRANSCRIBER_BACKEND", "openai_api")

    @staticmethod
    def set_transcriber_backend(backend):
        os.environ["TRANSCRIBER_BACKEND"] = backend
        set_key(ENV_PATH, "TRANSCRIBER_BACKEND", backend)

    @staticmethod
    def get_local_model_size():
        # 'tiny', 'base', 'small', 'medium', 'large'
        return os.getenv("LOCAL_MODEL_SIZE", "base")

    @staticmethod
    def set_local_model_size(size):
        os.environ["LOCAL_MODEL_SIZE"] = size
        set_key(ENV_PATH, "LOCAL_MODEL_SIZE", size)
