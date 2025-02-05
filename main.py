# main.py
import os
import yt_dlp
import threading
import ssl
from tkinter import Tk, StringVar, ttk, messagebox, Label, Button, Entry  # Fixed imports
from flask import Flask, request, jsonify
from flask_cors import CORS

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
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('video_ext') != 'none':
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': f.get('resolution', 'Unknown'),
                        'ext': f['ext']
                    })
            return jsonify({"formats": formats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- Download Logic (Unchanged) ---
def download_video(url, format_id='best'):
    try:
        ydl_opts = {
            'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
            'format': format_id,
            'progress_hooks': [progress_hook],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
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