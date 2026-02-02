import threading
import soundfile as sf
import os
import tempfile
import numpy as np

class SystemRecorder:
    def __init__(self):
        self.is_recording = False
        self.sys_data = [] # List of numpy arrays
        self.sys_thread = None
        self.sys_filename = os.path.join(tempfile.gettempdir(), "system_only.wav")

    def start_recording(self):
        if self.is_recording:
            return
        
        self.is_recording = True
        self.sys_data = []
        
        self.sys_thread = threading.Thread(target=self._record_system)
        self.sys_thread.start()
        print("System Recording started...")

    def stop_recording(self):
        if not self.is_recording:
            return None
        
        self.is_recording = False
        if self.sys_thread:
            self.sys_thread.join()
            
        print("System Recording stopped.")
        return self.sys_filename

    def _record_system(self):
        try:
            import soundcard as sc
            
            # Find the loopback matching default speaker
            mics = sc.all_microphones(include_loopback=True)
            loopback = None
            for mic in mics:
                 if mic.isloopback:
                     loopback = mic
                     break
            
            if not loopback:
                print("No loopback device found. System audio might be silent.")
                return

            sample_rate = 44100
            
            with loopback.recorder(samplerate=sample_rate) as recorder:
                while self.is_recording:
                    # Record small chunks
                    data = recorder.record(numframes=1024)
                    self.sys_data.append(data)
            
            if self.sys_data:
                full_data = np.concatenate(self.sys_data)
                sf.write(self.sys_filename, full_data, sample_rate)
            
        except Exception as e:
            print(f"System recording error: {e}")
