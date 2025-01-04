# path/to/your/api_file.py
from youtube_search import YoutubeSearch
import json
import subprocess



def search_youtube(query, max_results=5):
    results = YoutubeSearch(query, max_results).to_json()
    obj = json.loads(results)
    return obj["videos"]

def download_video(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    destination = "-P ./videos"
    command = ["yt-dlp",destination, url]
    subprocess.run(command)


def get_videos():
    import os
    videos_folder = "./videos"
    files = os.listdir(videos_folder)
    videos = [{"filename": file} for file in files]
    return videos


