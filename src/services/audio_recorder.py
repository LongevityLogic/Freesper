import pyaudio
import wave
import threading
import os
import tempfile

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.frames = []
        self.thread = None
        self.p = pyaudio.PyAudio()
        self.temp_filename = os.path.join(tempfile.gettempdir(), "whisper_temp.wav")

    def start_recording(self):
        if self.is_recording:
            return
        
        self.is_recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record)
        self.thread.start()
        print("Recording started...")

    def _record(self):
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100

        stream = self.p.open(format=format,
                             channels=channels,
                             rate=rate,
                             input=True,
                             frames_per_buffer=chunk)

        while self.is_recording:
            data = stream.read(chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        # Note: We don't terminate self.p here to allow restart

        self._save_to_file(channels, self.p.get_sample_size(format), rate)

    def stop_recording(self):
        if not self.is_recording:
            return
        
        self.is_recording = False
        if self.thread:
            self.thread.join()
        print(f"Recording stopped. Saved to {self.temp_filename}")
        return self.temp_filename

    def _save_to_file(self, channels, sample_width, rate):
        with wave.open(self.temp_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(b''.join(self.frames))

    def __del__(self):
        self.p.terminate()
