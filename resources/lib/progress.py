# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import utilxbmc
import videolibrary
from utils import info, lang, setting

monitor = xbmc.Monitor()

class Progress:
	def __init__(self, steps):
		self.enable = setting('hide_progress') == 'false'
		self.steps = steps
		self.current = 0
		if steps > 0:
			if self.enable:
				if utilxbmc.version() >= 13:
					self.bar = xbmcgui.DialogProgressBG()
				else:
					self.bar = xbmcgui.DialogProgress()
				self.bar.create(info('name'))
				self.bar.update(0, info('name'))

	def start_module(self, module_title, module_steps):
		self.module_title = module_title
		self.module_steps = module_steps
		self.module_current = 0

	def update(self, msg):
		percent = self.current * 100 / self.steps
		if self.enable:
			self.bar.update(percent, info('name'), lang(30531) % (self.module_title, msg))
		self.current += 1
		self.module_current += 1

	def finish_module(self):
		if not self.module_steps == self.module_current:
			skip = self.module_steps - self.module_current
			self.current += skip
			self.module_current += skip
		percent = self.current * 100 / self.steps
		if self.current == self.steps:
			if self.enable:
				self.bar.update(100, info('name'), 'Done')
				monitor.waitForAbort(1)
				self.bar.close()

	def update_library(self, path=False):
		if path and setting('remove_video') == 'true':
			videolibrary.remove_video(path)
#			if self.enable:
#				self.bar.close()
#				self.bar = None
		if setting('update_library') == 'true':
			xbmc.executebuiltin('UpdateLibrary(video)')
			while not xbmc.getCondVisibility('Library.IsScanningVideo'):
				pass
			while xbmc.getCondVisibility('Library.IsScanningVideo'):
				xbmc.sleep(20)
			percent = (self.current-1) * 100 / self.steps
			if self.enable:
				if utilxbmc.version() >= 13:
					self.bar = xbmcgui.DialogProgressBG()
				else:
					self.bar = xbmcgui.DialogProgress()
				self.bar.create(info('name'))
				self.bar.update(percent, info('name'),  lang(30531) % (self.module_title, lang(30513)))
