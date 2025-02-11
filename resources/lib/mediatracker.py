import xbmc
import urllib.request
import urllib.parse
import json
from typing import TypedDict, Literal

from resources.lib import utils

class ExternalId(TypedDict):
    imdbId: str
    tmdbId: int

class ProgressPayload(TypedDict):
    mediaType: Literal["movie", "tv"]
    id: ExternalId
    seasonNumber: int
    episodeNumber: int
    action: Literal["playing", "paused"]
    progress: float
    duration: float
    device: str

class MarkAsSeenPayload(TypedDict):
    mediaType: Literal["movie", "tv"]
    id: ExternalId
    seasonNumber: int
    episodeNumber: int
    duration: float

class MediaTracker:
    def __init__(self, url: str, apiToken: str) -> None:
        if len(url) == 0:
            utils.logAndNotify("Missing MediaTracker url", xbmc.LOGERROR, True);
            return

        if len(apiToken) == 0:
            utils.logAndNotify("Missing MediaTracker api token", xbmc.LOGERROR, True);
            return

        self.url = url
        self.apiToken = apiToken

    def validateConnection(self):
        try:
            res = self.getUser()
            if res and res.status == 200:
                resContent = res.read()
                resContentCharset = res.headers.get_content_charset()
                if resContent and resContentCharset:
                    user = json.loads(resContent.decode(resContentCharset))
                    # utils.logAndNotify(f"User \"{user['name']}\" authorized", xbmc.LOGINFO, False)
                    return True
                else:
                    raise Exception("Unauthorized")
        except Exception as e:
            utils.logAndNotify(f"Error connecting client {e=}, {type(e)=}", xbmc.LOGERROR, True)
            return False


    def getUser(self):
        url = urllib.parse.urljoin(
            self.url, '/api/user?token=' + self.apiToken)

        return sendGetRequest(url)

    def setProgress(self, payload: ProgressPayload):
        url = urllib.parse.urljoin(
            self.url, '/api/progress/by-external-id?token=' + self.apiToken)

        sendPutRequest(url, payload)

    def markAsSeen(self, payload: MarkAsSeenPayload):
        url = urllib.parse.urljoin(
            self.url, '/api/seen/by-external-id?token=' + self.apiToken)

        sendPutRequest(url, payload)


def sendPutRequest(url: str, data: dict):
    postdata = json.dumps(data).encode()

    headers = {"Content-Type": "application/json; charset=UTF-8"}

    httprequest = urllib.request.Request(
        url,
        data=postdata,
        headers=headers,
        method="PUT")

    # utils.logAndNotify(f"sendPutRequest => \"{json.dumps(data)}\"", xbmc.LOGINFO, False)

    response = urllib.request.urlopen(httprequest)

def sendGetRequest(url: str):
    httprequest = urllib.request.Request(
        url,
        method="GET")

    return urllib.request.urlopen(httprequest)
