import xbmc
from resources.lib.scrobbler import Scrobbler

class Player(xbmc.Player):
    def __init__(self):
        self.scrobbler = Scrobbler()
        xbmc.log('#cnc# Player initialized', xbmc.LOGINFO)

    def onAVStarted(self):
        xbmc.log("###MediaTracker###: Player => starting scrobbler", xbmc.LOGINFO)
        self.scrobbler.start()

    def onPlayBackPaused(self):
        xbmc.log("###MediaTracker###: Player => pausing scrobbler", xbmc.LOGINFO)
        self.scrobbler.pause()

    def onPlayBackResumed(self):
        xbmc.log("###MediaTracker###: Player => resuming scrobbler", xbmc.LOGINFO)
        self.scrobbler.resume()

    def onPlayBackSeek(self, time, offset):
        xbmc.log("###MediaTracker###: Player => seeking", xbmc.LOGINFO)
        self.scrobbler.seek()

    def onPlayBackSeekChapter(self, chapter):
        xbmc.log("###MediaTracker###: Player => seeking chapter", xbmc.LOGINFO)
        self.scrobbler.seek()

    def onPlayBackStopped(self):
        xbmc.log("###MediaTracker###: Player => stopping scrobbler", xbmc.LOGINFO)
        self.scrobbler.stop()

    def onPlayBackEnded(self):
        xbmc.log("###MediaTracker###: Player => ending scrobbler", xbmc.LOGINFO)
        self.scrobbler.end()