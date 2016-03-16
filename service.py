# -*- coding: utf-8 -*-
import os
import xbmcgui
from resources.lib import dialog, utilfile, utilxbmc
from resources.lib.utils import setting
from resources.lib.progress import Progress
from resources.lib.movie import Movie
from resources.lib.episode import Episode

## PLAYER
class AfterWatchPlayer(xbmc.Player):
	def onPlayBackStarted(self):
		self.playing = None
		j = utilxbmc.xjson('{"jsonrpc":"2.0","method":"Player.GetActivePlayers","id":1}')
		t = j['result'][0]['type']
		i = j['result'][0]['playerid']
		if t == 'video':
			j = utilxbmc.xjson('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":%s},"id":1}' % i)
			type = j['result']['item']['type']
			if type == 'movie':
				self.playing = Movie()
				self.__time()
			elif type == 'episode':
				self.playing = Episode()
				self.__time()


	def onPlayBackEnded(self):
		if self.playing:
			self.playing.ended()
			self.playing = None


	def onPlayBackStopped(self):
		if self.playing:
			percent = self.current * 100 / self.time
			minimum = float(setting('assume'))
			if minimum <= percent:
				self.playing.ended()
			self.playing = None


	def __time(self):
		self.current = 0
		self.time = self.getTotalTime()
		if not int(setting('assume')) == 100:
			while self.isPlaying():
				self.current = self.getTime()
				monitor.waitForAbort(2)

monitor = xbmc.Monitor()
player = AfterWatchPlayer()
monitor.waitForAbort()
