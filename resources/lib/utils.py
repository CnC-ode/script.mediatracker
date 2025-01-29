import xbmc
import xbmcaddon
import xbmcgui
from xbmcvfs import translatePath
import json

__addon__ = xbmcaddon.Addon()
ADDON_ICON = translatePath(__addon__.getAddonInfo('icon'))

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

def logAndNotify(message, notify):
    xbmc.log(f"###MediaTracker###: {message}", xbmc.LOGDEBUG)
    if notify:
        xbmcgui.Dialog().notification('MediaTracker', message, ADDON_ICON, 5000, False)

def getSetting(setting):
    return __addon__.getSetting(setting).strip()

def getInfoLabel(label):
    return xbmc.getInfoLabel(label)