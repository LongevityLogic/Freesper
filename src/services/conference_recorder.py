import threading
import soundfile as sf
import pyaudio
import wave
import os
import tempfile
import numpy as np

class ConferenceRecorder:
    def __init__(self):
        self.is_recording = False
        self.mic_frames = []
        self.sys_data = []
        
        self.mic_thread = None
        self.sys_thread = None
        
        self.mic_filename = os.path.join(tempfile.gettempdir(), "conf_mic.wav")
        self.sys_filename = os.path.join(tempfile.gettempdir(), "conf_sys.wav")
        
        self.p = pyaudio.PyAudio()

    def start_recording(self):
        if self.is_recording:
            return
        
        self.is_recording = True
        self.mic_frames = []
        self.sys_data = [] # List of numpy arrays
        
        self.mic_thread = threading.Thread(target=self._record_mic)
        self.sys_thread = threading.Thread(target=self._record_system)
        
        self.mic_thread.start()
        self.sys_thread.start()
        print("Conference Recording started...")

    def stop_recording(self):
        if not self.is_recording:
            return None, None
        
        self.is_recording = False
        if self.mic_thread:
            self.mic_thread.join()
        if self.sys_thread:
            self.sys_thread.join()
            
        print("Conference Recording stopped.")
        return self.mic_filename, self.sys_filename

    def _record_mic(self):
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100

        try:
            stream = self.p.open(format=format,
                                 channels=channels,
                                 rate=rate,
                                 input=True,
                                 frames_per_buffer=chunk)

            while self.is_recording:
                data = stream.read(chunk)
                self.mic_frames.append(data)

            stream.stop_stream()
            stream.close()

            with wave.open(self.mic_filename, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(self.p.get_sample_size(format))
                wf.setframerate(rate)
                wf.writeframes(b''.join(self.mic_frames))
        except Exception as e:
            print(f"Mic recording error: {e}")

    def _record_system(self):
        # Using soundcard for loopback
        # Default loopback mic
        try:
            import soundcard as sc
            # Get default speaker
            speaker = sc.default_speaker()
            # Get loopback microphone for that speaker
            # Note: sc.get_microphone(id=str(speaker.name), include_loopback=True) might be needed
            # But commonly sc.all_microphones(include_loopback=True) finds it.
            # However, simpler is just record from loopback mic directly if identifiable.
            # sc.default_microphone() is usually the physical mic.
            
            # Find the loopback matching default speaker
            mics = sc.all_microphones(include_loopback=True)
            loopback = None
            # Heuristic: often named after valid output device
            # For simplicity, let's grab the first loopback device we find
            for mic in mics:
                 if mic.isloopback:
                     loopback = mic
                     break
            
            if not loopback:
                # Fallback: try to just record from default mic (better than crash)
                # But user wants system audio.
                # On Windows, WASAPI loopback is reliable via soundcard.
                print("No loopback device found. System audio might be silent.")
                return

            sample_rate = 44100
            with loopback.recorder(samplerate=sample_rate) as recorder:
                while self.is_recording:
                    # Record small chunks
                    data = recorder.record(numframes=1024)
                    self.sys_data.append(data)
            
            # Save using soundfile
            full_data = np.concatenate(self.sys_data)
            sf.write(self.sys_filename, full_data, sample_rate)
            
        except Exception as e:
            print(f"System recording error: {e}")

    def __del__(self):
        self.p.terminate()
