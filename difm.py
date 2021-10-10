import requests
import json
import time
from urllib.parse import urlparse
from urllib.parse import parse_qs
import datetime
from datetime import timezone
import os

from requests.models import Response

networks = []
channels = []
user = []
audio_token = None
session_key = None

network_url = "https://www.di.fm"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}

def update_audio_token():
   global audio_token
   global channels
   global session_key
   global user
   global networks
   # There is probbaly a better way to get this that also allows for using credentials.
   response = requests.post(f"{network_url}/login",headers=headers)
   #print(response.text.encode('utf8'))
   result = json.loads(response.text.split("di.app.start(")[1].split(");")[0])
   user = result["user"]
   networks = []
   for network in result["networks"]:
      # figure out what's wrong with parsing ClassicalRadio.com thml
      if network["name"] != "ClassicalRadio.com":
         networks.append(network)
   
   audio_token = result["user"]["audio_token"]
   session_key = result["user"]["session_key"]
   channels = result["channels"]

def get_all_channels():
   channel_list = []
   response = requests.post(f"{network_url}/login",headers=headers)
   result = json.loads(response.text.split("di.app.start(")[1].split(");")[0])
   for network in result["networks"]:
      if network["name"] != "ClassicalRadio.com":
         response = requests.post(f"{network['url']}/login",headers=headers)
         result = json.loads(response.text.split("di.app.start(")[1].split(");")[0])
         for channel in result["channels"]:
            if channel not in channel_list:
               channel_list.append(channel)
   return channel_list

def get_url_expiration(url):
    parsed_url = urlparse(url)
    exp = parse_qs(parsed_url.query)['exp'][0]
    return exp

def is_url_expired(url):
   # This puts the burden on difm endpoint to validate
   # make request and see if  "URL expired" is returned
   # Invalid signature if token is invalid
   #response = requests.options(url)
   # if response.text == "URL expired":
   #   return True
   # else:
   #   return False

   # This is less overhead since we are doing it before playing each track.
   # Expired track is reall only an issue if the user keeps the app open for 24+ hrs.
   # return true if expiration date is less than current date
   current_time = datetime.datetime.now(timezone.utc).replace(tzinfo=timezone.utc)
   expiration_time = datetime.datetime.strptime(
      get_url_expiration(url), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=timezone.utc)
   return expiration_time < current_time

def get_channels():
   return channels

def get_networks():
   return networks

def set_network_url(url):
   global network_url
   network_url = url
   update_audio_token()

def download_track(track,channel,url,directory="tracks"):
   path = os.path.join(directory,channel)
   if not os.path.exists(path):
      os.makedirs(path)
   r = requests.get(url, allow_redirects=True,headers=headers)
   open(os.path.join(path,f"{track}.mp4"), 'wb').write(r.content)

def get_tracks_by_channel_id(id):
   tracks = []
   epoch = time.time()
   channel_url = f'{network_url}/_papi/v1/di/routines/channel/{id}?tune_in=false&audio_token={audio_token}&_={epoch}'
   channel_repsonse = requests.get(channel_url,headers=headers)
   for track in json.loads(channel_repsonse.text)["tracks"]:
      tracks.append(track)
   return tracks

def generate_playlist(channel_id,channel_name,playlist_directory="playlists"):
   print(f"Generating pls file for {channel_name} in {playlist_directory} ...")
   index = 0
   pls_tracks = {}
   for n in range(4):
         tracks = get_tracks_by_channel_id(channel_id)
         for track in tracks:
            pls_tracks[track["track"]] = f'https:{track["content"]["assets"][0]["url"]}'
   expiration = get_url_expiration(list(pls_tracks.items())[0][1]).replace(":","-")
   if not  os.path.exists(playlist_directory):
         os.makedirs(playlist_directory)
   with open(os.path.join(playlist_directory,f"{channel_name} - Expires {expiration}.pls"), 'a', encoding="utf-8") as f:
         f.write("[playlist]\n")
         f.write(f"NumberOfEntries={len(pls_tracks)}\n")
         for track in pls_tracks:
            index += 1
            f.write(f"File{index}={pls_tracks[track]}\n")
            f.write(f"Title{index}={track} Expires: {get_url_expiration(pls_tracks[track])}\n")
   print("Done. See playlists directory for file")

update_audio_token()

if __name__ == "__main__":
   print(get_all_channels())
