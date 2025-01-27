import xbmc
from resources.lib.monitor import Monitor
from resources.lib.monitor import Player
from resources.lib.scrobbler import Scrobbler

xbmc.log("###MediaTracker###: starting", xbmc.LOGINFO)

scrobbler = Scrobbler()
monitor = Monitor(scrobbler)
player = Player(scrobbler)

while not monitor.abortRequested():
    if monitor.waitForAbort(30):
        xbmc.log("###MediaTracker###: monitor aborted", xbmc.LOGINFO)
        break

    # else:
        # if xbmc.Player().isPlaying():
            # scrobbler.scrobble(xbmc.Player())

xbmc.log("###MediaTracker###: exiting", xbmc.LOGINFO)