# URL downloading (Youtube, Facebook)

# utils/video_utils.py

import yt_dlp
import os

def download_video_from_url(url, output_dir="data/downloads"):
    """
    Downloads a video from a URL using yt-dlp and returns the saved path.
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
        except Exception as e:
            print(f"[ERROR] Failed to download video: {e}")
            return None
