import vlc
import datetime

class Player:
    def __init__(self,vlc_log=False):
        params = "--quiet"
        if vlc_log:
            params = f'--verbose=2 --file-logging --logfile=vlc-log_{datetime.datetime.now().strftime("%m%d%Y")}.txt'
        self.instance = vlc.Instance(params) # --verbose 2 --quiet
        self.player = self.instance.media_player_new()
        self.listPlayer = self.instance.media_list_player_new()
        self.status = "Not Playing"

    def get_status(self):
        return self.status

    def get_volume(self):
        volume = self.player.audio_get_volume()
        if int(volume) < 0:
            return "0"
        else:
            return volume
    
    def set_volume(self,volume):
        return self.player.audio_set_volume(volume)

    def set_event_callback(self, callback):
        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, callback)
        events.event_attach(vlc.EventType.MediaPlayerEncounteredError, callback)

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