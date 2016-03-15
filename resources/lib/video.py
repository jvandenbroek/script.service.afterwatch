# -*- coding: utf-8 -*-
## TYPES
class Video:
	def show_quit_menu(self):
		xbmc.executebuiltin('ActivateWindow(shutdownmenu)')

	def logoff_user(self):
		xbmc.executebuiltin('System.LogOff')

	def turn_display_off(self):
		if sys.platform.startswith('win') and not player.isPlaying():
			path = xbmc.translatePath('special://home/addons/script.afterwatch/resources/lib/Sleeper.exe')
			os.startfile(path)
