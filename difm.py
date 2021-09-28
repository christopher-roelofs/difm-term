import requests
import json
import re
import time
import base64
from urllib.parse import urlparse
from urllib.parse import parse_qs
import threading
import datetime



audio_token = None
channels = []




s = requests.Session()
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
   # make request and see if  "URL expired" is returned
   #Invalid signature if token is invalid
   #response = requests.options(url)
   #if response.text == "URL expired":
   #   return True
   #else:
   #   return False

   # return true if expiration date is less than current date
   current_time = (datetime.datetime.now())
   expiration_time = datetime.datetime.strptime(get_url_expiration(url)[:-1], '%Y-%m-%dT%H:%M:%S')
   return expiration_time < current_time
   
   
def get_channels():
   return channels

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
   for track in tracks:
      print(is_url_expired(track["content"]["assets"][0]["url"]))
      

   

