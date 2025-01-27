import xbmc
import xbmcaddon
import xbmcgui
import json
from resources.lib.mediatracker import MediaTracker

class Scrobbler:
    def __init__(self) -> None:
        self.__addon__ = xbmcaddon.Addon()
        self.player = xbmc.Player()
        self.mediaTrackerClient = self.initMediaTrackerClient()

    def initMediaTrackerClient(self):
        apiToken = self.__addon__.getSettingString('apiToken')
        mediatrackerUrl = self.__addon__.getSettingString('mediatrackerUrl')

        if len(apiToken) == 0:
            xbmc.log("###MediaTracker###: missing api token", xbmc.LOGINFO)
            return

        if len(mediatrackerUrl) == 0:
            xbmc.log("###MediaTracker###: missing MediaTracker url", xbmc.LOGINFO)
            return

        return MediaTracker(mediatrackerUrl, apiToken)

    def resetScrobbler(self):
        self.onProgress = False
        self.isScrollable = False
        self.mediaType = None
        self.id = None
        self.tmdbId = None
        self.imdbId = None
        self.title = None
        self.tvShowTitle = None
        self.seasonNumber = None
        self.episodeNumber = None
        self.progress = None
        self.currentTime = None
        self.duration = None

    def startScrobbler(self):
        if self.mediaTrackerClient == None:
            xbmc.log("###MediaTracker###: cannot scrobble => mediaTrackerClient not initialized", xbmc.LOGINFO)
            return

        self.resetScrobbler()

        self.onProgress = True
        self.isScrollable = self.getPlayingItemData()

        if not self.isScrollable:
            xbmc.log("###MediaTracker###: cannot scrobble => item is not scrollable", xbmc.LOGINFO)
            return

        self.scrobble()

    def pauseScrobbler(self):
        self.onProgress = False
        self.scrobbleProgress()

    def resumeScrobbler(self):
        self.onProgress = True
        self.scrobble()
        self.sendProgress()

    def seekScrobbler(self):
        self.scrobbleProgress()

    def stopScrobbler(self):
        self.onProgress = False

        if self.progress > 0.85:
            self.progress = 1
            self.sendProgress()

    def endScrobbler(self):
        self.onProgress = False

        self.progress = 1
        self.sendProgress()

    def getPlayingItemData(self):
        playingItem = self.player.getPlayingItem()

        if not isinstance(playingItem, xbmcgui.ListItem):
            return False

        videoInfoTag = playingItem.getVideoInfoTag()

        if not isinstance(videoInfoTag, xbmc.InfoTagVideo):
            return False

        self.mediaType = videoInfoTag.getMediaType()
        self.id = videoInfoTag.getDbId()
        self.tmdbId = videoInfoTag.getUniqueID("tmdb")
        self.imdbId = videoInfoTag.getUniqueID("imdb")
        self.title = videoInfoTag.getTitle()
        self.tvShowTitle = videoInfoTag.getTVShowTitle()

        if self.mediaType == "episode":
            # second try
            if self.tmdbId == None and self.imdbId == None:
                res = kodiJsonRequest('VideoLibrary.GetEpisodeDetails', {
                    'episodeid': self.id,
                    'properties': ['tvshowid']
                })

                tvShowId = res.get("episodedetails", {}).get("tvshowid")

                if tvShowId == None:
                    xbmc.log("###MediaTracker###: missing tvShowId for episode " + self.title, xbmc.LOGINFO)
                    return False

                res = kodiJsonRequest('VideoLibrary.GetTVShowDetails', {
                    'tvshowid': tvShowId,
                    'properties': ['uniqueid']
                })

                self.tmdbId = res.get("tvshowdetails", {}).get("uniqueid", {}).get("tmdb")
                self.imdbId = res.get("tvshowdetails", {}).get("uniqueid", {}).get("imdb")
            
            # gave up
            if self.tmdbId == None and self.imdbId == None:
                xbmc.log(f"###MediaTracker###: missing tmdbId and imdbId for episode of \"{self.title}\"", xbmc.LOGINFO)
                return False

            self.seasonNumber = videoInfoTag.getSeason()
            self.episodeNumber = videoInfoTag.getEpisode()

        elif self.mediaType == "movie":
            if self.tmdbId == None and self.imdbId == None:
                xbmc.log(f"###MediaTracker###: missing tmdbId and imdbId for \"{self.title}\"", xbmc.LOGINFO)
                return False

        return True

    def scrobble(self):
        while self.player.isPlaying() and self.onProgress and self.isScrollable:
            self.scrobbleProgress()
            xbmc.sleep(5000)

    def scrobbleProgress(self):
        if self.player.isPlaying():
            self.progress = 0

            self.currentTime = self.player.getTime()

            if not self.duration or self.duration == 0:
                self.duration = self.player.getTotalTime()
            
            if self.duration and self.duration > 0:
                self.progress = self.currentTime / self.duration

            if self.progress < 0:
                self.progress = 0

            self.sendProgress()

    def sendProgress(self):
        if self.mediaType == "episode":
            xbmc.log(f"###MediaTracker###: updating progress for tv show \"{self.tvShowTitle}\" {self.seasonNumber}x{self.episodeNumber} - {self.progress * 100:.2f}%", xbmc.LOGINFO)
        elif self.mediaType == "movie":
            xbmc.log(f"###MediaTracker###: updating progress for movie \"{self.title}\" - {self.progress * 100:.2f}%", xbmc.LOGINFO)

        self.mediaTrackerClient.setProgress({
            "mediaType": self.mediaType if self.mediaType == "movie" else "tv",
            "id": {
                "imdbId": self.imdbId,
                "tmdbId": self.tmdbId
            },
            "seasonNumber": self.seasonNumber,
            "episodeNumber": self.episodeNumber,
            "progress": self.progress,
            "duration": self.duration * 1000,
            "action": "playing" if self.onProgress else "paused"
        })

def kodiJsonRequest(method: str, params: dict):
    args = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': 1
    }
    request = xbmc.executeJSONRPC(json.dumps(args))
    response = json.loads(request)

    if not isinstance(response, dict):
        return {}

    return response.get('result', {})
