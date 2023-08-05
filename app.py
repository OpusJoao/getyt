from pytube import YouTube
from youtubesearchpython import VideosSearch
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import time
import os
import shutil
import zipfile

VIDEO_DOWNLOAD_DIR = "/video"
AUDIO_DOWNLOAD_DIR = "/audio"


app = Flask(__name__)
CORS(app)

def search_and_get_first_result_url(song_list):
    youtube_urls = []

    for song in song_list:
        result = VideosSearch(song, limit=1).result()

        if result and 'result' in result and result['result']:
            first_video = result['result'][0]
            url = first_video['link']
            youtube_urls.append(url)

    return youtube_urls

def youtube_audio_download(video_url, current_name):
    video = YouTube(video_url)
    audio = video.streams.filter(only_audio=True).first()

    try:
        saved_path = current_name + '/' + AUDIO_DOWNLOAD_DIR
        file_name = audio.default_filename
        audio.download(saved_path)
        print("Audio was downloaded successfully")
        return saved_path + '/'+ file_name
    except Exception as e:
        print("Failed to download audio:", e)
        return None

def youtube_video_download(video_url, current_name):
    video = YouTube(video_url)
    video_stream = video.streams.get_highest_resolution()

    try:
        saved_path = current_name + '/' + VIDEO_DOWNLOAD_DIR
        file_name = video_stream.default_filename
        video_stream.download(saved_path)
        print("Video was downloaded successfully")
        return saved_path + '/'+ file_name
    except Exception as e:
        print("Failed to download video:", e)
        return None 

def zip_folder(folder_path, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

def download_zip(current_name):
    folder_path = './temp/' + current_name  # Substitua pelo caminho da pasta que você deseja zipar
    zip_file = f"./temp/{current_name}.zip"   # Substitua pelo caminho e nome do arquivo zip que você deseja gerar

    zip_folder(folder_path, zip_file)
    return zip_file
def format_path(path_string):
    # Remove "./" do início da string (se existir)
    if path_string.startswith("./"):
        path_string = path_string[2:]

    # Substitui todas as ocorrências de "//" por "/"
    path_string = path_string.replace("//", "/")

    return path_string

def delete_directory(directory_path):
    try:
        shutil.rmtree(directory_path)
        print(f"The directory '{directory_path}' has been deleted successfully.")
    except OSError as e:
        print(f"Error: Unable to delete the directory '{directory_path}'. {e}")

@app.route('/', methods=['GET'])
def render_index():
    return render_template('index.html')
    
@app.route('/', methods=['POST'])
def index():
    current_name = str(time.time())
    songs = []
    count_files_downloaded = 0
    to_download = False
    single_file_path = ''

    if request.method == 'POST':
        data = request.get_json()  # Extrai os dados JSON do corpo da requisição
        # Ou use request.form para obter os dados de um formulário HTML (application/x-www-form-urlencoded)

        # Verifica se o corpo da requisição contém a chave 'nome'
        if 'songs' in data:
            songs = data['songs']
        if 'toDownload' in data:
            to_download = data['toDownload']

        urls = search_and_get_first_result_url(songs)

        for i, url in enumerate(urls, start=1):
            print(f"Música \"{songs[i-1]}\": {url}")
            if 'type' in data and data["type"] == "audio":
                single_file_path = youtube_audio_download(url, './temp/' + current_name)
            else:
                single_file_path = youtube_video_download(url, './temp/' + current_name)
            count_files_downloaded += 1
        if to_download is True:
            if len(songs) == 1: 
                return send_file(format_path(single_file_path), as_attachment=True)
            else:
                file = download_zip(current_name)
                delete_directory('./temp/' + current_name)
                return send_file(file, as_attachment=True)
        else:
            return {
                "filesDownloaded": count_files_downloaded
            }

if __name__ == '__main__':
    app.run()