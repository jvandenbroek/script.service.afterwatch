# -*- coding: utf-8 -*-
import os
import xbmcgui
from resources.lib import dialog, utilfile, utilxbmc
from resources.lib.debug import debug
from resources.lib.utils import setting, log
from resources.lib.progress import Progress
from resources.lib.movie import Movie
from resources.lib.episode import Episode

## MONITOR
class AfterWatchMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        debug.set()

    def onSettingsChanged(self):
        log("AfterWatchMonitor.onSettingsChanged: called")
        debug.set()

## PLAYER
class AfterWatchPlayer(xbmc.Player):
    def onPlayBackStarted(self):
        self.playing = None
        try:
            for x in range(3): # retry 2 times before giving up
                try:
                    j = utilxbmc.xjson({ "jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1 })
                    t = j[0]['type']
                    i = j[0]['playerid']
                except (IndexError, TypeError) as e:
                    log("onPlayBackStarted: Can't retrieve active player status, retrying.. %d" % x, xbmc.LOGWARNING)
                    if monitor.waitForAbort(1):
                        break
                    if x < 2:
                        continue
                    else:
                        log("onPlayBackStarted: Could not get player info, giving up!", xbmc.LOGERROR)
                        raise
                break
            log("onPlayBackStarted: t=%s, i=%s" % (t, i))
            if t == 'video':
                j = utilxbmc.xjson({ "jsonrpc": "2.0", "method": "Player.GetItem", "params": { "playerid": i }, "id": 1 })
                type = j['item']['type']
                log("onPlayBackStarted: type=%s" % type)
                if type == 'movie':
                    self.playing = Movie()
                    self.__time()
                elif type == 'episode':
                    self.playing = Episode()
                    self.__time()
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
            self.playing = None

    def onPlayBackEnded(self):
        try:
            if hasattr(self, 'playing') and self.playing:
                self.playing.ended()
                self.playing = None
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
        finally:
            self.playing = None

    def onPlayBackStopped(self):
        try:
            if hasattr(self, 'playing') and self.playing:
                minimum = float(setting('assume'))
                if hasattr(self, 'total_time') and self.total_time > 0 and hasattr(self, 'current') and self.current > 0:
                    percent = self.current * 100 / self.total_time
                else:
                    percent = 0
                if minimum <= percent:
                    self.playing.ended()
                log("AfterWatchPlayer.onPlayBackStopped: percent=%d, self.total_time=%d, self.current=%d" % (percent, self.total_time, self.current))
                self.playing = None
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
        finally:
            self.playing = None

    def __time(self):
        try:
            self.current = self.getTime()
            self.total_time = self.getTotalTime()
            if not int(setting('assume')) == 100:
                while self.isPlaying():
                    if self.total_time == 0:
                        self.total_time = self.getTotalTime()
                    self.current = self.getTime()
                    if monitor.waitForAbort(5):
                        break
            log("AfterWatchPlayer.__time: self.current=%d, self.total_time=%d" % (self.current, self.total_time))
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)

monitor = AfterWatchMonitor()
player = AfterWatchPlayer()
log("started")
monitor.waitForAbort()
log("stopped")
