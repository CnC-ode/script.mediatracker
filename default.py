import xbmc
from resources.lib.monitor import Monitor
from resources.lib.player import Player

xbmc.log("###MediaTracker###: starting", xbmc.LOGINFO)

player = Player()

monitor = Monitor()
while not monitor.abortRequested():
    if monitor.waitForAbort(30):
        break

xbmc.log("###MediaTracker###: exiting", xbmc.LOGINFO)