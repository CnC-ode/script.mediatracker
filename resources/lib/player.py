import xbmc

from resources.lib.scrobbler import Scrobbler
from resources.lib import utils

class Player(xbmc.Player):
    def __init__(self):
        self.scrobbler = Scrobbler(self)
        utils.logAndNotify("Player initialized", xbmc.LOGINFO, False)

    def onAVStarted(self):
        utils.logAndNotify("Starting scrobbler", xbmc.LOGINFO, False)
        self.scrobbler.start()

    def onPlayBackPaused(self):
        utils.logAndNotify("Pausing scrobbler", xbmc.LOGINFO, False)
        self.scrobbler.pause()

    def onPlayBackResumed(self):
        utils.logAndNotify("Resuming scrobbler", xbmc.LOGINFO, False)
        self.scrobbler.resume()

    def onPlayBackSeek(self, time, offset):
        utils.logAndNotify("Seeking", xbmc.LOGINFO, False)
        self.scrobbler.seek()

    def onPlayBackSeekChapter(self, chapter):
        utils.logAndNotify("Seeking chapter", xbmc.LOGINFO, False)
        self.scrobbler.seek()

    def onPlayBackStopped(self):
        utils.logAndNotify("Stopping scrobbler", xbmc.LOGINFO, False)
        self.scrobbler.stop()

    def onPlayBackEnded(self):
        utils.logAndNotify("Ending scrobbler", xbmc.LOGINFO, False)
        self.scrobbler.end()