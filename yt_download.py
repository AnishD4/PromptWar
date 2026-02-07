from yt_dlp import YoutubeDL

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s', # Output filename template
        'noplaylist': True, # Only download the single video, not the whole playlist
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Example Usage:
video_url = "https://www.youtube.com/watch?v=wj6jIn2FoME" # Replace with your YouTube URL
download_audio(video_url)
