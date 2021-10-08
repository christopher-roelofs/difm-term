import datetime
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
config = {"playlist_directory":"playlists","track_directory":"tracks","vlc_log":False}
player = None
stop_input = False
last_channel = {}
logs = []

def log(message,type):
    global logs
    log = {}
    log["timestamp"] = datetime.datetime.now()
    log["message"] = message
    log["type"] = type
    logs.append(log)

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
    log(f"Saved last channel","info")

def load_last_channel():
    global last_channel
    if os.path.exists('last_channel.json'):
        with open('last_channel.json') as json_file:
            last_channel = json.load(json_file)
    log("Loaded last channel","info")

def update_last_channel():
    global last_channel
    last_channel = {}
    last_channel[current_channel] = current_channel_id
    log(f"Updated last channel to {current_channel}","info")
    save_last_channel()

def save_favorites():
    with open('favorites.json', 'w') as outjson:
        json.dump(favorite_channels, outjson)
    log("Saved favorites","info")

def load_favorites():
    global favorite_channels
    if os.path.exists('favorites.json'):
        with open('favorites.json') as json_file:
            favorite_channels = json.load(json_file)
    log("Loaded favorites","info")
    
def load_config():
    global config
    if os.path.exists('config.json'):
        with open('config.json') as json_file:
            config = json.load(json_file)
    log("Loaded config","info")

def save_config():
    with open('config.json', 'w') as outjson:
        json.dump(config, outjson)
    log("Saved config","info")

def update_favorites(channel,id):
    global favorite_channels
    if channel in favorite_channels:
        del favorite_channels[channel]
    else:
         favorite_channels[channel] = id
    log("Upated favorites","info")
    save_favorites()

def update_current_tracks():
    global current_track_index
    global current_tracklist
    current_tracklist = {}
    current_track_index = -1
    for n in range(1):
        for track in difm.get_tracks_by_channel_id(current_channel_id):
            current_tracklist[track["track"]] = "https:" + track['content']["assets"][0]["url"]
    log(f"Refreshed tracks for channel id {current_channel_id}","info")

def draw_player():
    screen_clear()
    print("--------------------------------------------------------------")
    print(f"Channel:  {current_channel}")
    print(f"Favorite: {current_channel in favorite_channels}")
    print(f"Track:    {current_track}")
    print(f"Status:   {player.get_status()}")
    print(f"Volume:   {player.get_volume()}")
    print("--------------------------------------------------------------")
    print("P: Play/Pause | S: Stop | N: Next | R: Previous | Q: Back")
    print("--------------------------------------------------------------")
    print("V: Volume | D: Download Track | F: Favorite/Unfavorite Channel")
    print("--------------------------------------------------------------")

def play_next_track(event=None):
    global player
    global current_track
    global current_track_index
    current_track_index += 1
    if current_track_index >= len(current_tracklist): 
        log("Last song in tracklist","info")
        update_current_tracks()
        current_track_index += 1   
    if difm.is_url_expired(list(current_tracklist.items())[current_track_index][1]):
        log("Track is expired","info")
        update_current_tracks()
        current_track_index += 1
    if player != None:
        if event == None:
            player.stop_audio()
    del player
    player = audio.Player(vlc_log=config["vlc_log"])
    player.set_event_callback(play_next_track)
    player.play_audio(list(current_tracklist.items())[current_track_index][1])
    current_track = list(current_tracklist.items())[current_track_index][0]
    log(f"Playing next track: {current_track}","info")
    draw_player()

def play_previous_track():
    global player
    global current_track
    global current_track_index
    current_track_index -= 1
    log("Playing previous track")
    if current_track_index > 0: 
        if difm.is_url_expired(list(current_tracklist.items())[current_track_index][1]):
            log("Track is expired","info")
            update_current_tracks()
            current_track_index += 1
        player.stop_audio()
        del player
        player = audio.Player(vlc_log=config["vlc_log"])
        player.set_event_callback(play_next_track)
        player.play_audio(list(current_tracklist.items())[current_track_index][1])
        current_track = list(current_tracklist.items())[current_track_index][0]
        draw_player()

def config_menu():
    quit_config = False
    global config
    while not quit_config:
        screen_clear()
        print("----------------------")
        print("Edit Config")
        print("----------------------")
        print("1: Track Directory")
        print("2: Playlist Directory")
        print("3: Enable VLC Log to File")
        print("Q: Back")
        print("----------------------")
        val = input().lower()
        if val == "q":
            quit_config = True
        if val == "1":
            screen_clear()
            print("Edit Track Directory. Q to Quit")
            print(f'Current Track Directory: {config["track_directory"]}')
            val = input("New Track Directory:     ")
            if val.lower() == "q":
                pass
            else:
                config["track_directory"] = val
                log(f"Updated track directory to {val}","info")
                save_config()
        if val == "2":
            screen_clear()
            print("Edit Playlist Directory. Q to Quit")
            print(f'Current Playlist Directory: {config["playlist_directory"]}')
            val = input("New Playlist Directory:     ")
            if val.lower() == "q":
                pass
            else:
                config["playlist_directory"] = val
                log(f"Updated playlist directory to {val}","info")
                save_config()
        if val == "3":
            print("Enable VLC logging to file")
            print(f"Current set to {config['vlc_log']}")
            val = input("New state True/False: ")
            if val.lower() == "q":
                pass
            elif val.lower() in ["true","t","false","f"]:
                if val.lower() in ["true","t"]:
                    config["vlc_log"] = True
                else:
                    config["vlc_log"] = False
                save_config()

def play_last_channel(generate_playlist=False):
    global current_channel
    global current_channel_id
    global current_tracklist
    global current_track_index
    if len(last_channel) > 0:
        id = list(last_channel.items())[0][1]
        channel= list(last_channel.items())[0][0]
        current_channel = channel
        current_channel_id = id
        try:
            if generate_playlist:
                difm.generate_playlist(id,channel,config["playlist_directory"])
                val = input("Press enter to continue")
            else:
                current_tracklist = {}
                for n in range(1):
                    for track in difm.get_tracks_by_channel_id(id):
                        current_tracklist[track["track"]] = "https:" + track['content']["assets"][0]["url"]
                current_track_index = -1
                play_next_track()
                player_menu()
        except Exception as e:
            log(f"Error: {e}","error")

def player_menu():
    quit_player = False
    while not quit_player:
        draw_player()
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
                log(f"Updated volume to {volume}","info")
            except Exception as e:
                log(f"Failed to set volume: {e}","error")
        if val == "d":
            track = list(current_tracklist.items())[current_track_index][0]
            url = list(current_tracklist.items())[current_track_index][1]
            difm.download_track(track,current_channel,url,config["track_directory"])
            log(f"Downloaded track: {track}","info")
        if val =="f":
            update_favorites(current_channel,current_channel_id)
            log(f"Updated favorites: {current_channel}:{current_channel_id}","info")
        sleep(1)

def favorites_menu(generate_playlist=False):
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
                if generate_playlist:
                    difm.generate_playlist(id,channel[0],config["playlist_directory"])
                    val = input("Press enter to continue")
                else:
                    current_tracklist = {}
                    for n in range(1):
                        for track in difm.get_tracks_by_channel_id(id):
                            current_tracklist[track["track"]] = "https:" + track['content']["assets"][0]["url"]
                    current_track_index = -1
                    update_last_channel()
                    play_next_track()
                    player_menu()
            except Exception as e:
                log(f"Error: {e}","error")

def all_channels_menu(generate_playlist=False):
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
                if generate_playlist:
                    difm.generate_playlist(id,channel["name"],config["playlist_directory"])
                    val = input("Press enter to continue")
                else:
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
                log(f"Error: {e}","error") 

def log_menu():
    quit = False
    log_page = 1
    sorted_logs = sorted(logs, key=lambda k: k['timestamp'], reverse=True)
    while not quit:
        screen_clear()
        print("------------------------------------------")
        print("                  Logs                    ")
        print("------------------------------------------")
        index = 0
        max = log_page * 10
        for log in sorted_logs[max - 10:max]:
            print(f"{log['timestamp']} - {log['type']} - {log['message']}")
            index += 1
        print("------------------------------------------")
        print("N: Next Page | P: Previous Page | Q: Quit ")
        print("------------------------------------------")
        val = input()
        if val.lower() == "n" or val == "":
            if log_page <= (len(sorted_logs) / 10):
                log_page += 1
        if val.lower() == "p":
            if log_page > 1:
                log_page -= 1
        if val.lower() == "q":
                quit = True

def playlist_menu():
    global current_channel
    global current_channel_id
    global current_tracklist
    global current_track_index
    global last_channel
    quit_playlist = False
    while not quit_playlist:
        screen_clear()
        print("--------------------------------------------")
        print("    Generate Playlist(.pls) from Channel    ")
        print("--------------------------------------------")
        print("1: All Channels")
        print("2: Favorite Channels")
        print("3: Last Channel (default)")
        print("Q: Quit")
        print("--------------------------------------------")
        val = input().lower() or "3"
        if val == "1":
            all_channels_menu(generate_playlist=True)
        if val == "2":
            favorites_menu(generate_playlist=True)
        if val == "3":
            play_last_channel(generate_playlist=True)
        if val == "q":
            quit_playlist = True                    

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
        print("4: Generate Playlist")
        print("5: Edit Config")
        print("6: Show logs")
        print("Q: Quit")
        print("-------------------")
        val = input().lower() or "3"
        if val == "1":
            all_channels_menu()
        if val == "2":
            favorites_menu()
        if val == "3":
            play_last_channel()
        if val == "4":
            playlist_menu()
        if val == "5":
            config_menu()
        if val == "6":
            log_menu()
        if val == "q":
            quit_menu = True

load_config()
load_favorites()
load_last_channel()
menu()
