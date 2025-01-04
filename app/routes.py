from flask import Blueprint, render_template, request, jsonify, send_from_directory, Response
from app.search_yt import search_youtube, download_video, get_videos
import subprocess
import os
main = Blueprint("main", __name__)

VIDEOS_FOLDER = os.path.abspath('./videos')
print(os.listdir('./videos')) 

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/youtube")
def youtube():
    return render_template("index.html")  # Create a search.html if needed

@main.route("/files")
def list_files():
    return render_template("downloads.html")  # Create a files.html if needed

@main.route('/search', methods=['POST'])
def search():
    search_query = request.json.get('query')
    max_results = request.json.get('maxResults', 5)  # Default to 5 if not provided
    if not search_query:
        return jsonify({"error": "Query is required"}), 400

    # Call the search_youtube function
    results = search_youtube(search_query, int(max_results))
    return jsonify(results), 200

@main.route('/download/<video_id>', methods=['GET'])
def download(video_id):
    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400

    def generate():
        url = f"https://www.youtube.com/watch?v={video_id}"
        command = [
            "yt-dlp",
            f"--output=videos/%(title)s.%(ext)s",
            url,
            "--progress",
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"Server Output: {line.strip()}")  # Debugging log
                yield f"data: {line.strip()}\n\n"  # Send formatted data to client

        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            yield "data: Download complete!\n\n"
        else:
            yield "data: Error occurred during download.\n\n"

    return Response(generate(), content_type='text/event-stream')

@main.route('/videos', methods=['GET'])
def list_videos():
    # List all video files in the VIDEOS_FOLDER
    video_files = os.listdir(VIDEOS_FOLDER)
    print(f"Available videos: {video_files}") 
    return jsonify(video_files), 200


@main.route('/video/<path:filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(VIDEOS_FOLDER, filename)
    print(f"Attempting to send file from: {file_path}")  # Debug print
    if not os.path.isfile(file_path):
        print("File does not exist!")  # Debug print
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(VIDEOS_FOLDER, filename, as_attachment=True)

@main.route('/delete_video', methods=['POST'])
def delete_video():
    video_filename = request.json.get('filename')
    if not video_filename:
        return jsonify({"error": "Filename is required"}), 400

    file_path = os.path.join(VIDEOS_FOLDER, video_filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({"message": "Video deleted successfully"}), 200
    else:
        return jsonify({"error": "File not found"}), 404