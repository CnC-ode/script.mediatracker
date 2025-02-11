import xbmc

from resources.lib.monitor import Monitor
from resources.lib.player import Player
from resources.lib import utils

utils.logAndNotify("Starting", xbmc.LOGINFO, False)

player = Player()
monitor = Monitor()

monitor.waitForAbort()

utils.logAndNotify("Exiting", xbmc.LOGINFO, False)
