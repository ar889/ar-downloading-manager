# main.py
import os
import yt_dlp
import threading
import ssl
from tkinter import Tk, StringVar, ttk, messagebox, Label, Button, Entry  # Fixed imports
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app)

# --- SSL Configuration (Updated) ---
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain('localhost.crt', 'localhost.key')  # Ensure these files exist!

# --- Flask Server ---
@app.route('/add_download', methods=['POST'])
def handle_download():
    data = request.json
    url = data.get('url')
    format_id = data.get('format', 'best')  # Default to 'best' if no format specified
    if url:
        threading.Thread(target=download_video, args=(url, format_id)).start()
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

# --- GUI Class ---
class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("Video Download Manager")
        self.setup_gui()
        
        # Start Flask server in a non-daemon thread
        self.flask_thread = threading.Thread(target=run_flask)
        self.flask_thread.start()
        
        self.root.mainloop()

    def setup_gui(self):
        Label(self.root, text="Enter Video URL:").pack(pady=10)
        self.url_entry = Entry(self.root, width=50)
        self.url_entry.pack()
        Button(self.root, text="Download", command=self.start_download).pack(pady=10)

    def start_download(self):
        url = self.url_entry.get()
        if url:
            threading.Thread(target=download_video, args=(url,)).start()

# --- Flask Server Setup ---
def run_flask():
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=context,
        threaded=True,
        use_reloader=False
    )

# main.py
@app.route('/get_formats', methods=['POST'])
def get_formats():
    data = request.json
    url = data.get('url')
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('video_ext') != 'none':
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': f.get('resolution') or f.get('format_note'),
                        'ext': f['ext'],
                        'has_audio': f.get('acodec') not in ['none', None]
                    })
            return jsonify({"formats": formats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- Download Logic (Unchanged) ---

def sanitize_filename(filename):
    """Ensure filename is safe for filesystem."""
    return re.sub(r'[\/:*?"<>|]', '_', filename)

def download_video(url, format_id='best'):
    try:
        # Get video info
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)

        original_title = sanitize_filename(info['title'])  # Get clean title
        video_format = None
        audio_format = None

        for f in info.get('formats', []):
            if f['format_id'] == format_id:
                video_format = f
            if f.get('acodec') != 'none':  # Find best available audio format
                audio_format = f

        if not video_format:
            print("Error: Video format not found.")
            return

        # Define file paths using original title
        video_output = os.path.join("downloads", f"{original_title}_video.mp4")
        final_output = os.path.join("downloads", f"{original_title}.mp4")

        # Download video-only format
        ydl_opts_video = {
            'format': video_format['format_id'],
            'outtmpl': video_output,
            'progress_hooks': [progress_hook],
        }
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([url])

        if video_format.get('acodec') == 'none' and audio_format:
            # Download audio format
            audio_output = os.path.join("downloads", f"{original_title}_audio.m4a")
            ydl_opts_audio = {
                'format': audio_format['format_id'],
                'outtmpl': audio_output,
            }
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([url])

            # Merge video and audio using FFmpeg
            merge_command = [
                "ffmpeg", "-y",
                "-i", video_output,
                "-i", audio_output,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                final_output
            ]
            subprocess.run(merge_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Remove temp files
            os.remove(video_output)
            os.remove(audio_output)
            print(f"Merged video saved as: {final_output}")
        else:
            print(f"Downloaded video saved as: {video_output}")

    except Exception as e:
        print(f"Error: {e}")



def start_selected_download(ydl, url, selected_format, root):
    ydl_opts = {'format': selected_format.get().split(':')[0]}
    root.destroy()
    ydl.download([url])

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Progress: {d['_percent_str']} | Speed: {d['_speed_str']}")
    elif d['status'] == 'finished':
        print("Download completed!")

if __name__ == "__main__":
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    App()