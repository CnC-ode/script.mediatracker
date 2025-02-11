import xbmc
import xbmcgui
import json

from resources.lib.mediatracker import MediaTracker
from resources.lib import utils

class Scrobbler:
    def __init__(self, player) -> None:
        self.player = player
        self.scrobbleMonitor = xbmc.Monitor()
        self.instanceName = utils.getInfoLabel('System.FriendlyName')
        utils.logAndNotify("Scrobbler initialized", xbmc.LOGINFO, False)

    def reset(self):
        self.isMediaTrackerClientConnected = False
        self.onProgress = False
        self.onProgressError = False
        self.isScrollable = False
        self.scrobbleInterval = utils.getSettingAsInt('scrobbleInterval')
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
            utils.logAndNotify("Client initialization failed", xbmc.LOGERROR, True)
            return

        self.isMediaTrackerClientConnected = self.mediaTrackerClient.validateConnection()

        if not self.isMediaTrackerClientConnected:
            utils.logAndNotify("Client connection failed", xbmc.LOGERROR, True)
            return

        self.onProgress = True
        self.isScrollable = self.getPlayingItemData()

        # utils.logAndNotify(f"onProgress {self.onProgress}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"isScrollable {self.isScrollable}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"mediaType {self.mediaType}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"id {self.id}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"tmdbId {self.tmdbId}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"imdbId {self.imdbId}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"title {self.title}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"tvShowTitle {self.tvShowTitle}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"seasonNumber {self.seasonNumber}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"episodeNumber {self.episodeNumber}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"progress {self.progress}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"currentTime {self.currentTime}", xbmc.LOGINFO, False)
        # utils.logAndNotify(f"duration {self.duration}", xbmc.LOGINFO, False)

        if not self.isScrollable:
            utils.logAndNotify("Item is not scrollable", xbmc.LOGINFO, False)
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
        self.sendProgress()

    def seek(self):
        if not self.isScrollable:
            return

        xbmc.sleep(500)
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
                    utils.logAndNotify("Missing tvShowId for episode " + self.title, xbmc.LOGINFO, False)
                    return False

                res = utils.kodiJsonRequest('VideoLibrary.GetTVShowDetails', {
                    'tvshowid': tvShowId,
                    'properties': ['uniqueid']
                })

                self.tmdbId = res.get("tvshowdetails", {}).get("uniqueid", {}).get("tmdb")
                self.imdbId = res.get("tvshowdetails", {}).get("uniqueid", {}).get("imdb")
            
            # gave up
            if not self.tmdbId and not self.imdbId:
                utils.logAndNotify(f"Missing tmdbId and imdbId for episode of \"{self.title}\"", xbmc.LOGINFO, False)
                return False

            self.seasonNumber = videoInfoTag.getSeason()
            self.episodeNumber = videoInfoTag.getEpisode()

        elif self.mediaType == "movie":
            if not self.tmdbId and not self.imdbId:
                utils.logAndNotify(f"missing tmdbId and imdbId for \"{self.title}\"", xbmc.LOGINFO, False)
                return False
        else:
            utils.logAndNotify(f"Media type is not scrollable \"{self.title}\"", xbmc.LOGINFO, False)
            return False

        return True

    def scrobble(self):
        while self.player.isPlaying():
            if self.onProgress:
                self.scrobbleProgress()

            if self.scrobbleMonitor.waitForAbort(self.scrobbleInterval):
                self.onProgress = False
                self.sendProgress()
                break;

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
        # if self.mediaType == "episode":
        #     utils.logAndNotify(f"Updating progress for tv show \"{self.tvShowTitle}\" {self.seasonNumber}x{self.episodeNumber} - {self.progress * 100:.2f}%", xbmc.LOGINFO, False)
        # elif self.mediaType == "movie":
        #     utils.logAndNotify(f"Updating progress for movie \"{self.title}\" - {self.progress * 100:.2f}%", xbmc.LOGINFO, False)

        try:
            progressBody = {
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
            }
            
            self.mediaTrackerClient.setProgress(progressBody)
            
            if self.onProgressError:
                utils.logAndNotify(f"Scrobbler restablished", xbmc.LOGINFO, True)
                self.onProgressError = False

        except Exception as e:
            utils.logAndNotify(f"Error sending progress {e=}, {type(e)=}", xbmc.LOGERROR, not self.onProgressError)
            self.onProgressError = True
