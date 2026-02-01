from src.services.transcriber import Transcriber
import os

class ConferenceTranscriber:
    def __init__(self):
        self.transcriber = Transcriber()

    def transcribe_session(self, mic_path, sys_path, language=None):
        segments = []

        # 1. Transcribe Mic
        if os.path.exists(mic_path) and os.path.getsize(mic_path) > 1000:
            mic_raw = self.transcriber.transcribe(mic_path, language, return_segments=True)
            mic_segs = self._normalize(mic_raw, "User")
            segments.extend(mic_segs)
            
        # 2. Transcribe System
        if os.path.exists(sys_path) and os.path.getsize(sys_path) > 1000:
            sys_raw = self.transcriber.transcribe(sys_path, language, return_segments=True)
            # Use 'System' or 'Attendee'
            sys_segs = self._normalize(sys_raw, "System")
            segments.extend(sys_segs)
            
        # 3. Sort by start time
        segments.sort(key=lambda x: x['start'])
        
        return segments

    def _normalize(self, raw_segments, label):
        normalized = []
        for s in raw_segments:
            # Local whisper returns dict, API returns object (or dict depending on client version)
             # Handle Object access
            if hasattr(s, 'start'):
                start = s.start
                end = s.end
                text = s.text
            else:
                # Dict access
                start = s.get('start', 0)
                end = s.get('end', 0)
                text = s.get('text', "")
            
            normalized.append({
                'start': start,
                'end': end,
                'text': text.strip(),
                'speaker': label
            })
        return normalized
