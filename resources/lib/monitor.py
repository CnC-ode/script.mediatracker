import xbmc
from resources.lib.scrobbler import Scrobbler

class Monitor(xbmc.Monitor):
    def __init__(self):
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
