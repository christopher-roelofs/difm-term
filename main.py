from logging import exception
from time import sleep
import difm
import os
import audio

current_page = 1
current_channel = None
current_channel_id = None
volume = None
current_track = ""
current_track_index = -1
current_tracklist = {}
debug_message = ""
debug = False
quit = False
player = None
stop_input = False

def screen_clear():
    # for mac and linux(here, os.name is 'posix')
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')

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
    global stop_input
    global debug_message
    screen_clear()
    print("--------------------------------")
    print(f"Channel: {current_channel}")
    print(f"Status:  {player.get_status()}")
    print(f"Volume:  {player.get_volume()}")
    if debug:
        print(f"Msg:     {debug_message}")
    print("--------------------------------")
    print("P: Play/Pause | S: Stop | N: Next | R: Previous | Q: Back | V: Volume | D: Download Track")
    val = input().lower()
    if val == "q":
        player.stop_audio()
        stop_input = True
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
        difm.download_track(list(current_tracklist.items())[current_track_index][0],list(current_tracklist.items())[current_track_index][1])



def main_menu():
    global debug_message
    global current_page
    global current_channel
    global current_channel_id
    global current_tracklist
    global current_track
    global stop_input
    global player
    global quit
    global current_track_index
    stop_input = False
    stop_main_menu = False
    screen_clear()
    print("--------------------------------")
    print("Select Station")
    print("--------------------------------")
    index = 0
    max = current_page * 10
    for channel in difm.channels[max - 10:max]:
        print(f"{index}: {channel['name']}")
        index += 1
    print("--------------------------------")
    print("N: Next Page | P: Previous Page | Q: Quit")
    print("--------------------------------")
    while not stop_main_menu:
        val = input()
        if val.lower() == "n" or val == "":
            stop_main_menu = True
            if current_page <= (len(difm.channels) / 10):
                current_page += 1
        elif val.lower() == "p":
            stop_main_menu = True
            if current_page > 1:
                current_page -= 1
        elif val.lower() == "q":
                stop_main_menu = True
                quit = True
        elif val in "0123456789":
            try:
                stop_main_menu = True
                channel = difm.channels[max - 10:max][int(val)]
                id = channel["id"]
                current_channel = channel["name"]
                current_channel_id = id
                current_tracklist = {}
                for n in range(1):
                    for track in difm.get_tracks_by_channel_id(id):
                        current_tracklist[track["track"]] = "https:" + track['content']["assets"][0]["url"]
                current_track_index = -1
                play_next_track()
                while not stop_input:
                    player_menu()
                    sleep(1)
            except Exception as e:
                debug_message = e   
                
        else:
            stop_main_menu = True




while not quit:
    main_menu()
