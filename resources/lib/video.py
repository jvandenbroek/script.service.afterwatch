# -*- coding: utf-8 -*-
import os
import sys
from utils import log
## TYPES
class Video:
    def show_quit_menu(self):
        xbmc.executebuiltin('ActivateWindow(shutdownmenu)')

    def logoff_user(self):
        xbmc.executebuiltin('System.LogOff')

    def turn_display_off(self):
        if not hasattr(self, 'player') or not player.isPlaying():
            if sys.platform.startswith('win'):
                path = xbmc.translatePath('special://home/addons/script.afterwatch/resources/lib/Sleeper.exe')
                os.startfile(path)
            elif sys.platform.startswith('linux'):
                for path in filter(lambda y: os.path.isfile(y + "/cec-client"), ( "/usr/bin", "/usr/local/bin", "~/bin" )):
                    log("Video.turn_display_off: execute %s/cec-client -s -d 1" % path)
                    os.system("echo standby 0 | %s/cec-client -s -d 1" % path)
                    return
                log("Video.turn_display_off: could not find cec-client", xmbc.LOGWARNING)
