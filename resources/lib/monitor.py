import xbmc
from resources.lib.scrobbler import Scrobbler

class Monitor(xbmc.Monitor):
    def __init__(self, scrobbler: Scrobbler):
        self.scrobbler = scrobbler
        xbmc.Monitor.__init__(self)

    # def onNotification(self, sender, method, dataJson):
        # xbmc.log("###MediaTracker###: onNotification => %s" % method, xbmc.LOGINFO);
        
        # if not method in [
        #     'Player.OnPlay',
        #     'Player.OnPause',
        #     'Player.OnStop',
        #     'Player.OnSeek',
        #     'Player.OnResume',
        # ]:
        #     return

        # self.scrobbler.scrobble(xbmc.Player())


class Player(xbmc.Player):
    def __init__(self, scrobbler: Scrobbler):
        self.scrobbler = scrobbler
        xbmc.log('#cnc# Player initialized', xbmc.LOGINFO)

    def onAVStarted(self):
        xbmc.log("###MediaTracker###: Player => starting scrobbler", xbmc.LOGINFO)
        self.scrobbler.startScrobbler()

    def onPlayBackPaused(self):
        xbmc.log("###MediaTracker###: Player => pausing scrobbler", xbmc.LOGINFO)
        self.scrobbler.pauseScrobbler()

    def onPlayBackResumed(self):
        xbmc.log("###MediaTracker###: Player => resuming scrobbler", xbmc.LOGINFO)
        self.scrobbler.resumeScrobbler()

    def onPlayBackSeek(self, time, offset):
        xbmc.log("###MediaTracker###: Player => seeking", xbmc.LOGINFO)
        self.scrobbler.seekScrobbler()

    def onPlayBackSeekChapter(self, chapter):
        xbmc.log("###MediaTracker###: Player => seeking chapter", xbmc.LOGINFO)
        self.scrobbler.seekScrobbler()

    def onPlayBackStopped(self):
        xbmc.log("###MediaTracker###: Player => stopping scrobbler", xbmc.LOGINFO)
        self.scrobbler.stopScrobbler()

    def onPlayBackEnded(self):
        xbmc.log("###MediaTracker###: Player => ending scrobbler", xbmc.LOGINFO)
        self.scrobbler.endScrobbler()