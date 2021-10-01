from logging import exception
from time import sleep
import difm
import os
import audio
import json

current_page = 1
current_channel = None
current_channel_id = None
volume = None
current_track = ""
current_track_index = -1
current_tracklist = {}
favorite_channels = {}
debug_message = ""
debug = False
player = None
stop_input = False
last_channel = {}

def screen_clear():
    # for mac and linux(here, os.name is 'posix')
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')

def save_last_channel():
    with open('last_channel.json', 'w') as outjson:
        json.dump(last_channel, outjson)

def load_last_channel():
    global last_channel
    if os.path.exists('last_channel.json'):
        with open('last_channel.json') as json_file:
            last_channel = json.load(json_file)

def update_last_channel():
    global last_channel
    last_channel = {}
    last_channel[current_channel] = current_channel_id
    save_last_channel()

def save_favorites():
    with open('favorites.json', 'w') as outjson:
        json.dump(favorite_channels, outjson)

def load_favorites():
    global favorite_channels
    if os.path.exists('favorites.json'):
        with open('favorites.json') as json_file:
            favorite_channels = json.load(json_file)

def update_favorites(channel,id):
    global favorite_channels
    if channel in favorite_channels:
        del favorite_channels[channel]
    else:
         favorite_channels[channel] = id
    save_favorites()

def update_current_tracks():
    global current_track_index
    global current_tracklist
    current_tracklist = {}
    current_track_index = -1
    for n in range(1):
        for track in difm.get_tracks_by_channel_id(current_channel_id):
            current_tracklist[track["track"]] = "https:" + track['content']["assets"][0]["url"]

def play_next_track(event=None):
    global debug_message
    global player
    global current_track
    global current_track_index
    current_track_index += 1
    if current_track_index >= len(current_tracklist): 
        global debug_message 
        update_current_tracks()
        current_track_index += 1   
    if difm.is_url_expired(list(current_tracklist.items())[current_track_index][1]):
        update_current_tracks()
        current_track_index += 1
    if player != None:
        if event == None:
            player.stop_audio()
    del player
    player = audio.Player()
    player.set_event_callback(play_next_track)
    player.play_audio(list(current_tracklist.items())[current_track_index][1])
    current_track = list(current_tracklist.items())[current_track_index][0]

def play_previous_track():
    global player
    global current_track
    global current_track_index
    current_track_index -= 1
    if current_track_index > 0: 
        if difm.is_url_expired(list(current_tracklist.items())[current_track_index][1]):
            update_current_tracks()
            current_track_index += 1
        player.stop_audio()
        del player
        player = audio.Player()
        player.set_event_callback(play_next_track)
        player.play_audio(list(current_tracklist.items())[current_track_index][1])
        current_track = list(current_tracklist.items())[current_track_index][0]

def player_menu():
    quit_player = False
    while not quit_player:
        global debug_message
        screen_clear()
        print("-----------------------------------------------------------------------------------------")
        print(f"Channel:  {current_channel}")
        print(f"Favorite: {current_channel in favorite_channels}")
        print(f"Status:   {player.get_status()}")
        print(f"Volume:   {player.get_volume()}")
        if debug:
            print(f"Msg:      {debug_message}")
        print("-----------------------------------------------------------------------------------------")
        print("P: Play/Pause | S: Stop | N: Next | R: Previous | Q: Back | V: Volume | D: Download Track | F: Favorite/Unfavorite Channel")
        val = input().lower()
        if val == "q":
            player.stop_audio()
            quit_player = True
        if val == "p":
            player.pause_audio()
        if val == "r":
            play_previous_track()
        if val == "s":
            player.stop_audio()
        if val == "n":
            play_next_track()
        if val == "b":
            player.stop_audio()
        if val == "v":
            volume = input("Volume: ")
            try:
                player.set_volume(int(volume))
            except:
                pass
        if val == "d":
            difm.download_track(list(current_tracklist.items())[current_track_index][0],current_channel,list(current_tracklist.items())[current_track_index][1])
        if val =="f":
            update_favorites(current_channel,current_channel_id)
        sleep(1)

def favorites_menu():
    global current_channel
    global current_channel_id
    global current_track_index
    global stop_input
    global current_tracklist
    quit_favorites = False
    favorite_page = 1
    while not quit_favorites:
        favorites = list(favorite_channels.items())
        favorite_index = 0
        screen_clear()
        print("------------------------------------------")
        print("            Favorite Channels             ")
        print("------------------------------------------")
        max = favorite_page * 10
        if len(favorites[max - 10:max]) < 1:
            max = (favorite_page - 1) * 10
            favorite_page -= 1
        for channel in favorites[max - 10:max]:
            print(f"{favorite_index}: {channel[0]}")
            favorite_index += 1
        print("------------------------------------------")
        print("N: Next Page | P: Previous Page | Q: Back ")
        print("------------------------------------------")
        val = input().lower()
        if val == "n" or val == "":
            if favorite_page <= (len(favorites) / 10):
                favorite_page += 1
        elif val == "p":
            if favorite_page > 1:
                favorite_page -= 1
        elif val == "q":
            quit_favorites = True
        elif val in "0123456789":
            try:
                channel = favorites[max - 10:max][int(val)]
                id = channel[1]
                current_channel = channel[0]
                current_channel_id = id
                current_tracklist = {}
                for n in range(1):
                    for track in difm.get_tracks_by_channel_id(id):
                        current_tracklist[track["track"]] = "https:" + track['content']["assets"][0]["url"]
                current_track_index = -1
                update_last_channel()
                play_next_track()
                player_menu()
            except Exception as e:
                debug_message = e  

def all_channels_menu():
    quit = False
    while not quit:
        global current_page
        global current_channel
        global current_channel_id
        global current_tracklist
        global current_track
        global stop_input
        global current_track_index
        screen_clear()
        print("------------------------------------------")
        print("              All Channels                ")
        print("------------------------------------------")
        index = 0
        max = current_page * 10
        for channel in difm.channels[max - 10:max]:
            print(f"{index}: {channel['name']}")
            index += 1
        print("------------------------------------------")
        print("N: Next Page | P: Previous Page | Q: Quit ")
        print("------------------------------------------")
        val = input()
        if val.lower() == "n" or val == "":
            if current_page <= (len(difm.channels) / 10):
                current_page += 1
        if val.lower() == "p":
            if current_page > 1:
                current_page -= 1
        if val.lower() == "q":
                quit = True
        if val in "0123456789":
            try:
                channel = difm.channels[max - 10:max][int(val)]
                id = channel["id"]
                current_channel = channel["name"]
                current_channel_id = id
                current_tracklist = {}
                for n in range(1):
                    for track in difm.get_tracks_by_channel_id(id):
                        current_tracklist[track["track"]] = "https:" + track['content']["assets"][0]["url"]
                current_track_index = -1
                update_last_channel()
                play_next_track()
                player_menu()
            except Exception as e:
                debug_message = e   
                    

def menu():
    global current_channel
    global current_channel_id
    global current_tracklist
    global current_track_index
    global last_channel
    quit_menu = False
    while not quit_menu:
        screen_clear()
        print("-------------------")
        print("     DI.FM Term    ")
        print("-------------------")
        print("1: All Channels")
        print("2: Favorite Channels")
        print("3: Last Channel (default)")
        print("Q: Quit")
        print("-------------------")
        val = input().lower() or "3"
        if val == "1":
            all_channels_menu()
        if val == "2":
            favorites_menu()
        if val == "3":
            if len(last_channel) > 0:
                id = list(last_channel.items())[0][1]
                current_channel = list(last_channel.items())[0][0]
                current_channel_id = id
                current_tracklist = {}
                for n in range(1):
                    for track in difm.get_tracks_by_channel_id(id):
                        current_tracklist[track["track"]] = "https:" + track['content']["assets"][0]["url"]
                current_track_index = -1
                play_next_track()
                player_menu()
        if val == "q":
            quit_menu = True


load_favorites()
load_last_channel()
menu()
