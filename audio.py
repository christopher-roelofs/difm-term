import vlc
import time
import threading
import os
from vlc import EventType, Media, MediaPlayer, MediaParseFlag, Meta


class Player:
    def __init__(self):
        self.instance = vlc.Instance("--quiet")
        self.player = self.instance.media_player_new()
        self.listPlayer = self.instance.media_list_player_new()
        self.status = "Not Playing"

    def get_status(self):
        return self.status

    def set_event_callback(self, callback):
        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, callback)

    def play_audio(self, url):
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.player.play()
        self.status = "Playing"

    def stop_audio(self):
        self.player.stop()
        self.status = "Stopped"

    def pause_audio(self):
        if self.status == "Playing":
            self.player.pause()
            self.status = "Paused"
        elif self.status == "Paused":
            self.player.play()
            self.status = "Playing"
        elif self.status == "Stopped":
            self.player.play()
            self.status = "Playing"



if __name__ == "__main__":
    pass
