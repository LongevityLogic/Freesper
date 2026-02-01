import datetime

class ReportGenerator:
    @staticmethod
    def generate_markdown(segments, output_path=None):
        if output_path is None:
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = f"Conference_Report_{now}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Conference Report\n")
            f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("---\n\n")
            
            for seg in segments:
                time_str = ReportGenerator._format_time(seg['start'])
                speaker = seg['speaker']
                text = seg['text']
                
                # Format: > **[00:15] User**: Hello
                f.write(f"> **[{time_str}] {speaker}**: {text}\n>\n")
        
        return output_path

    @staticmethod
    def _format_time(seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"
