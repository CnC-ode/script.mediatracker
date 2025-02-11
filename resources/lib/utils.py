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

def logAndNotify(message, level, notify):
    xbmc.log(f"###MediaTracker###: {message}", level)
    if notify and getSettingAsBool('notifyError'):
        xbmcgui.Dialog().notification('MediaTracker', message, ADDON_ICON, 5000, False)

def getSetting(setting):
    return __addon__.getSetting(setting).strip()

def getSettingAsBool(setting):
    return getSetting(setting).lower() == "true"

def getSettingAsFloat(setting):
    try:
        return float(getSetting(setting))
    except ValueError:
        return 0

def getSettingAsInt(setting):
    try:
        return int(getSettingAsFloat(setting))
    except ValueError:
        return 0

def getInfoLabel(label):
    return xbmc.getInfoLabel(label)