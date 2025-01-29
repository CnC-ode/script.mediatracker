import xbmc
import xbmcgui
import json

from resources.lib.mediatracker import MediaTracker
from resources.lib import utils

class Scrobbler:
    def __init__(self) -> None:
        self.player = xbmc.Player()
        self.instanceName = utils.getInfoLabel('System.FriendlyName')
        
        self.reset()

    def reset(self):
        self.isMediaTrackerClientConnected = False
        self.onProgress = False
        self.onProgressError = False
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

    def start(self):
        self.reset()

        mediatrackerUrl = utils.getSetting('mediatrackerUrl')
        apiToken = utils.getSetting('apiToken')
        self.mediaTrackerClient = MediaTracker(mediatrackerUrl, apiToken)

        if self.mediaTrackerClient is None:
            utils.logAndNotify("client not initialized", True)
            return

        self.isMediaTrackerClientConnected = self.mediaTrackerClient.validateConnection()

        if not self.isMediaTrackerClientConnected:
            utils.logAndNotify("client connection failed", True)
            return

        self.onProgress = True
        self.isScrollable = self.getPlayingItemData()

        utils.logAndNotify(f"onProgress {self.onProgress}", False)
        utils.logAndNotify(f"isScrollable {self.isScrollable}", False)
        utils.logAndNotify(f"mediaType {self.mediaType}", False)
        utils.logAndNotify(f"id {self.id}", False)
        utils.logAndNotify(f"tmdbId {self.tmdbId}", False)
        utils.logAndNotify(f"imdbId {self.imdbId}", False)
        utils.logAndNotify(f"title {self.title}", False)
        utils.logAndNotify(f"tvShowTitle {self.tvShowTitle}", False)
        utils.logAndNotify(f"seasonNumber {self.seasonNumber}", False)
        utils.logAndNotify(f"episodeNumber {self.episodeNumber}", False)
        utils.logAndNotify(f"progress {self.progress}", False)
        utils.logAndNotify(f"currentTime {self.currentTime}", False)
        utils.logAndNotify(f"duration {self.duration}", False)

        if not self.isScrollable:
            utils.logAndNotify("item is not scrollable", True)
            return

        self.scrobble()

    def pause(self):
        if not self.isScrollable:
            return

        self.onProgress = False
        self.scrobbleProgress()

    def resume(self):
        if not self.isScrollable:
            return

        self.onProgress = True
        self.scrobble()
        # self.sendProgress()

    def seek(self):
        if not self.isScrollable:
            return

        self.scrobbleProgress()

    def stop(self):
        if not self.isScrollable:
            return


        if self.progress > 0.85:
            self.progress = 1
        self.onProgress = False
        self.sendProgress()

    def end(self):
        if not self.isScrollable:
            return

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
            if not self.tmdbId and not self.imdbId:
                res = utils.kodiJsonRequest('VideoLibrary.GetEpisodeDetails', {
                    'episodeid': self.id,
                    'properties': ['tvshowid']
                })

                tvShowId = res.get("episodedetails", {}).get("tvshowid")

                if not tvShowId:
                    utils.logAndNotify("missing tvShowId for episode " + self.title, False)
                    return False

                res = utils.kodiJsonRequest('VideoLibrary.GetTVShowDetails', {
                    'tvshowid': tvShowId,
                    'properties': ['uniqueid']
                })

                self.tmdbId = res.get("tvshowdetails", {}).get("uniqueid", {}).get("tmdb")
                self.imdbId = res.get("tvshowdetails", {}).get("uniqueid", {}).get("imdb")
            
            # gave up
            if not self.tmdbId and not self.imdbId:
                utils.logAndNotify(f"missing tmdbId and imdbId for episode of \"{self.title}\"", False)
                return False

            self.seasonNumber = videoInfoTag.getSeason()
            self.episodeNumber = videoInfoTag.getEpisode()

        elif self.mediaType == "movie":
            if not self.tmdbId and not self.imdbId:
                utils.logAndNotify(f"missing tmdbId and imdbId for \"{self.title}\"", False)
                return False
        else:
            utils.logAndNotify(f"media type is not scrollable \"{self.title}\"", False)
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
            utils.logAndNotify(f"updating progress for tv show \"{self.tvShowTitle}\" {self.seasonNumber}x{self.episodeNumber} - {self.progress * 100:.2f}%", False)
        elif self.mediaType == "movie":
            utils.logAndNotify(f"updating progress for movie \"{self.title}\" - {self.progress * 100:.2f}%", False)

        try:
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
                "action": "playing" if self.onProgress else "paused",
                "device": self.instanceName
            })
            if self.onProgressError:
                utils.logAndNotify(f"scrobbler restablished", True)
            self.onProgressError = False
        except Exception as e:
            utils.logAndNotify(f"error sending progress {e=}, {type(e)=}", not self.onProgressError)
            self.onProgressError = True
