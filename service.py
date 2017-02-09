# -*- coding: utf-8 -*-

import os
import xbmc
import xbmcaddon
import xbmcvfs
import json

ADDON               = xbmcaddon.Addon()
ADDON_ID            = ADDON.getAddonInfo('id')
ADDON_PATH          = xbmc.translatePath(ADDON.getAddonInfo('path'))
ADDON_PATH_DATA     = xbmc.translatePath(os.path.join('special://profile/addon_data/', ADDON_ID)).replace('\\', '/') + '/'
ADDON_PATH_LIB      = os.path.join(ADDON_PATH, 'resources', 'lib' )
ADDON_LANG          = ADDON.getLocalizedString

sys.path.append(ADDON_PATH_LIB)

import debug

profiles = ['1', '2', '3', '4']
map_type = { 'movie': 'auto_movies', 'video': 'auto_videos', 'episode': 'auto_tvshows', 'channel': 'auto_pvr', 'musicvideo': 'auto_musicvideo', 'song': 'auto_music', 'unknown': 'auto_unknown' }

class Monitor(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        
        # gui
        self.changeProfile(ADDON.getSetting('auto_gui'))
            
    def onNotification(self, sender, method, data):
        
        data = json.loads(data)
        
        if 'Player.OnStop' in method or 'System.OnWake' in method:
            debug.debug("[MONITOR] METHOD: " + str(method) + " DATA: " + str(data))
            
            # gui
            self.changeProfile(ADDON.getSetting('auto_gui'))
        
        if 'Player.OnPlay' in method:
            debug.debug("[MONITOR] METHOD: " + str(method) + " DATA: " + str(data))
            
            
            # auto show dialog
            if 'true' in ADDON.getSetting('player_show'):
                xbmc.executebuiltin('XBMC.RunScript(' + ADDON_ID + ', popup)')
            
            # auto switch
            if 'item' in data and 'type' in data['item']:
                type = data['item']['type']
                set = map_type.get(type)
                
                # if video is not from library assign to auto_videos
                if 'movie' in type and 'id' not in data['item']:
                    set = 'auto_videos'
                
                # distinguish pvr TV and pvr RADIO
                if 'channel' in type and 'channeltype' in data['item']:
                    if 'tv' in data['item']['channeltype']:
                        set = 'auto_pvr_tv'
                    elif 'radio' in data['item']['channeltype']:
                        set = 'auto_pvr_radio'
                    else:
                        set = None
                
                if set is not None:
                    self.changeProfile(ADDON.getSetting(set))
                
    def changeProfile(self, profile):
        
        if profile in profiles:
            # get last loaded profile
            lastProfile = self.getLastProfile()
            debug.debug("[MONITOR] Last loaded profile: " + lastProfile + " To switch profile: " + profile)
            
            if lastProfile != profile:
                xbmc.executebuiltin('XBMC.RunScript(' + ADDON_ID + ', ' + profile + ')')
            else:
                debug.debug("[MONITOR] Switching omitted (same profile)")
    
    def getLastProfile(self):
        try:
            f = xbmcvfs.File(ADDON_PATH_DATA + 'profile')
            p = f.read()
            f.close()
            if p in profiles:
                return p
            else:
                return ''
        except:
            return ''
    
monitor = Monitor()

while(not xbmc.abortRequested):
    xbmc.sleep(100)
    