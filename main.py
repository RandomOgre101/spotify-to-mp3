from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import requests
import base64
import json
from yt_dlp import YoutubeDL

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
YOUTUBE_API = os.getenv("YOUTUBE_API")


def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    URL = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization": 'Basic '+auth_base64,
        "Content-Type": 'application/x-www-form-urlencoded'
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(URL, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


token = get_token()

playlist_id = str(input("Enter the playlist link: ").split('/')[-1].strip())

if len(playlist_id) > 22:
    playlist_id = playlist_id.split("?")[0]

headers = {
    "Authorization": "Bearer "+token
}

response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',headers=headers)
response_for_title = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}',headers=headers)
data = response.json()
data_title = response_for_title.json()

playlist_title = data_title['name']

song_list = []
artist_list = []
total_songs = int(data["total"])

for num in range(total_songs):
    song_list.append(data["items"][num]["track"]["name"])
    artist_list.append(data["items"][num]["track"]["artists"][0]["name"])

songs = list(zip(song_list, artist_list))


youtube = build('youtube', 'v3', developerKey=YOUTUBE_API)
links = []
for song in songs:
    req = youtube.search().list(
        part = "id",
        q = f'{song[0]} - {song[1]}',
        maxResults = 1
    )
    yt = req.execute()
    etag = str(yt["items"][0]["id"]["videoId"])
    youtube_link = 'https://www.youtube.com/watch?v='+etag
    links.append(youtube_link)


path = f"D:/Spotify Playlists/{playlist_title}"
try:
    os.mkdir(path=path)
except FileExistsError:
    print("File with this name already exists.")

os.chdir(path)
with YoutubeDL({'format': 'bestaudio'}) as ydl:
    ydl.download(links)



