import difm
import os

current_page = 1
stop_input = False
quit = False

def screen_clear():
    # for mac and linux(here, os.name is 'posix')
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')

def main_menu():
    global current_page
    global stop_input
    global quit
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
    print("N: Next Page - P: Previous Page - Q: Quit")
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
            stop_main_menu = True
            channel = difm.channels[max - 10:max][int(val)]
            id = channel["id"]
            print(f"Generating pls file for {channel['name']}...")
            index = 0
            pls_tracks = {}
            for n in range(1):
                tracks = difm.get_tracks_by_channel_id(id)
                for track in tracks:
                    pls_tracks[track["track"]] = f'https:{track["content"]["assets"][0]["url"]}'
            expiration = difm.get_url_expiration(list(pls_tracks.items())[0][1]).replace(":","-")
            if not  os.path.exists("playlists"):
                os.makedirs('playlists')
            with open(os.path.join("playlists",f"{channel['name']} - Expires {expiration}.pls"), 'a', encoding="utf-8") as f:
                f.write("[playlist]\n")
                f.write(f"NumberOfEntries={len(pls_tracks)}\n")
                for track in pls_tracks:
                    index += 1
                    f.write(f"File{index}={pls_tracks[track]}\n")
                    f.write(f"Title{index}={track} Expires: {difm.get_url_expiration(pls_tracks[track])}\n")
            print("Done. See playlists directory for file")
            quit = True
        else:
            stop_main_menu = True




while not quit:
    main_menu()