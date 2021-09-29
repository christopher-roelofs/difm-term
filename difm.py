import requests
import json
import time
from urllib.parse import urlparse
from urllib.parse import parse_qs
import datetime
from datetime import timezone
import os



s = requests.Session()
# There is probbaly a better way to get this that also allows for using credentials.
response = s.post("https://www.di.fm/login")
result = json.loads(response.text.split("di.app.start(")[1].split(");")[0])

user = result["user"]
channels = result["channels"]
audio_token = user["audio_token"]

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

def download_track(track,url):
   if not  os.path.exists("tracks"):
      os.makedirs('tracks')
   r = requests.get(url, allow_redirects=True)
   open(os.path.join("tracks",f"{track}.mp4"), 'wb').write(r.content)


def get_channel_by_id(id):
   epoch = time.time()
   channel_url = f'https://www.di.fm/_papi/v1/di/routines/channel/{id}?tune_in=false&audio_token={audio_token}&_={epoch}'
   channel_repsonse = s.get(channel_url)
   channel_details = json.loads(channel_repsonse.text)
   return channel_details

def get_tracks_by_channel_id(id):
   tracks = []
   epoch = time.time()
   channel_url = f'https://www.di.fm/_papi/v1/di/routines/channel/{id}?tune_in=false&audio_token={audio_token}&_={epoch}'
   for n in range(4):
      channel_repsonse = s.get(channel_url)
      for track in json.loads(channel_repsonse.text)["tracks"]:
         tracks.append(track)
   return tracks


if __name__ == "__main__":
   tracks = get_tracks_by_channel_id(1)
   url = "https:" + tracks[0]["content"]["assets"][0]["url"]
   name = tracks[0]["track"] + ".mp4"
   download_track(name,url)
