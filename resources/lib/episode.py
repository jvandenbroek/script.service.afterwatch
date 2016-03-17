# -*- coding: utf-8 -*-
import xbmc
import os
import utilxbmc
import dialog, utilfile, utilxbmc
from progress import Progress
from utils import log, info, lang, setting, set_setting, rpc, ValueErrorHandler
from video import Video

monitor = xbmc.Monitor()


class Episode(Video):
	def __init__(self):
		j = utilxbmc.xjson('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":1,"properties":["file","title","playcount"]},"id":1}')
		self.type = 'episode'
		self.episodeid = j['result']['item']['id']
		p = j['result']['item']['file']
		if setting('fm_alternate') == 'true' or p.lower().startswith('smb://') or p.lower().startswith('nfs://'):
			self.path = xbmc.validatePath(p)
			self.alt_method = True
			log
		else:
			self.path = os.path.abspath(p)
			self.alt_method = False
		log("Episode: self.path |alt_method=%s|: %s" % (self.alt_method, self.path))
		self.title = j['result']['item']['title']
		self.playcount = j['result']['item']['playcount']
		self.rating = None


	MOVE_STEPS = 4
	def __move(self, progress):
		progress.start_module(lang(30132), self.MOVE_STEPS)
		try:
			progress.update(lang(30590)) # detecting library place
	 		lib_source = os.path.dirname(os.path.dirname(os.path.dirname(self.path)))
		 	if self.destination == lib_source:
		 		raise Exception(lang(30602))
			progress.update(lang(30506)) # moving files
			source = os.path.dirname(self.path)
			match = os.path.splitext(os.path.basename(self.path))[0]
			count = utilfile.count_manage_files(self.alt_method, source, match)
			if not dialog.warning(lang(30132), count):
				raise Exception(lang(30609))
			log("Episode: move source path: %s" % source)
			if setting('fm_episodes_structure') == '0': # multiple folders
				destination = os.path.join(self.destination, self.path.split(os.sep)[-3], self.path.split(os.sep)[-2])
				log("Episode: move destination (multiple) |alt_method=%s|: %s" % (self.alt_method, destination))
			else: # single folder
				destination = os.path.join(self.destination, self.path.split(os.sep)[-2])
				log("Episode: move destination (single) |alt_method=%s|: %s" % (self.alt_method, destination))
			utilfile.move_files(self.alt_method, source, destination, match, True)
			progress.update(lang(30513)) # updating library
			progress.update_library(self.path)
			self.path = os.path.join(destination, os.path.basename(self.path))
			self.episodeid = utilxbmc.get_episodeid_by_path(self.path)
			if self.episodeid: # if still in lib source folders
				progress.update(lang(30514)) # setting watched
				utilxbmc.set_episode_playcount(self.episodeid, self.playcount+1)
		except OSError:
			dialog.error(lang(30610))
		except ValueError as err:
			ValueErrorHandler(err)
		except Exception, e:
			dialog.error(e.message)
		finally:
			progress.finish_module()


	DELETE_STEPS = 2
	def __delete(self, progress):
		progress.start_module(lang(30133), self.DELETE_STEPS)
		try:
			progress.update(lang(30516)) # deleting files
			source = os.path.dirname(self.path)
			remove_empty = setting('fm_episodes_remove_empty') == 'true'
			match = os.path.splitext(os.path.basename(self.path))[0]
			log("Episode: delete match: %s" % match)
			count = utilfile.count_manage_files(self.alt_method, source, match)
			if not dialog.warning(lang(30133), count):
				raise Exception(lang(30609))
			utilfile.delete_files(self.alt_method, source, match, remove_empty)
			progress.update(lang(30513)) # updating library
			progress.update_library(self.path)
			self.episodeid = None
			self.path = None
		except OSError:
			dialog.error(lang(30610))
		except ValueError as err:
			ValueErrorHandler(err)
		except Exception, e:
			dialog.error(e.message)
		finally:
			progress.finish_module()


	PRESERVE_PLAYCOUNT_STEPS = 1
	def __preserve_playcount(self, progress):
		progress.start_module(lang(30701), self.PRESERVE_PLAYCOUNT_STEPS)
		try:
			if not self.episodeid:
				raise Exception(lang(30601))
			progress.update(lang(30598)) # setting old playcount
			utilxbmc.set_episode_playcount(self.episodeid, self.playcount)
		except Exception, e:
			dialog.error(e.message)
		finally:
			progress.finish_module()


	RATE_LIB_STEPS = 1
	def __rate_lib(self, progress):
		progress.start_module(lang(30204), self.RATE_LIB_STEPS)
		try:
			if not self.episodeid:
				raise Exception(lang(30601))
			progress.update(lang(30522)) # updating rating
			utilxbmc.set_episode_rating(self.episodeid, self.rating)
		except Exception, e:
			dialog.error(e.message)
		finally:
			progress.finish_module()


	def ended(self):
		log("Episode: Playback ended")
		# pre confirm
		steps = 0
		move = False
		delete = False
		preserve_playcount = False
		rate_lib = False
		if setting('confirm') == 'true':
			log("Episode: Show confirm dialog")
			wait_dialog = setting('wait_dialog')
			if not (wait_dialog == '' or wait_dialog == '0'):
				monitor.waitForAbort(int(wait_dialog))
		if setting('fm_episodes_manage') == '1': # move
			if dialog.proceed(self.title, lang(30132)):
				move = True
				steps += self.MOVE_STEPS
		elif setting('fm_episodes_manage') == '2': # delete
			if dialog.proceed(self.title, lang(30133)):
				delete = True
				steps += self.DELETE_STEPS
		if not setting('remove_video') == 'true':
			if setting('pt_episodes_playcount') == 'true':
				preserve_playcount = True
				steps += self.PRESERVE_PLAYCOUNT_STEPS
			if setting('rt_episodes_lib') == 'true':
				rate_lib = True
				steps += self.RATE_LIB_STEPS
		# pre settings
		if move:
			destination = setting('fm_episodes_destination')
			if self.alt_method or destination.lower().startswith('smb://') or destination.lower().startswith('nfs://'):
				self.destination = xbmc.validatePath(destination)
				self.alt_method = True
			else:
				self.destination = os.path.abspath(destination)
			while not self.destination or self.destination == '.':
				destination = xbmcgui.Dialog().browse(3, lang(30525) % info('name'), 'files')
				if self.alt_method or destination.lower().startswith('smb://') or destination.lower().startswith('nfs://'):
					self.destination = xbmc.validatePath(destination)
					self.alt_method = True
				else:
					self.destination = os.path.abspath(destination)
			log("set_setting fm_episodes_destination |alt_method=%s|: %s" % (self.alt_method, self.destination))
			set_setting('fm_episodes_destination', self.destination)
		# pre context
		# pre process
		progress = Progress(steps)
		if not setting('remove_video') == 'true':
			if rate_lib:
				rating = dialog.rating(self.title)
				while not rating:
					rating = dialog.rating(self.title)
				self.rating = rating
			if preserve_playcount:
				self.__preserve_playcount(progress)
			if rate_lib:
				self.__rate_lib(progress)
		if move:
			self.__move(progress)
		elif delete:
			self.__delete(progress)

		# post confirm
		quit_menu = False
		logoff = False
		display_off = False
		if setting('ps_episodes_quit_menu') == 'true':
			if dialog.proceed(self.title, lang(30402)):
				quit_menu = True
		if setting('ps_episodes_logoff') == 'true':
			if dialog.proceed(self.title, lang(30407)):
				logoff = True
		if setting('ps_episodes_display_off') == 'true':
			if dialog.proceed(self.title, lang(30404)):
				display_off = True
		# post processing
		if quit_menu:
			self.show_quit_menu()
		if logoff:
			self.logoff_user()
		if display_off:
			self.turn_display_off()
