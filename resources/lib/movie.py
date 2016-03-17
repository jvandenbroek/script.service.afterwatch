# -*- coding: utf-8 -*-
import xbmc
import os
import utilxbmc
import dialog, utilfile, utilxbmc
from progress import Progress
from utils import log, info, lang, setting, set_setting, rpc, ValueErrorHandler
from video import Video

monitor = xbmc.Monitor()

class Movie(Video):
	def __init__(self):
		j = utilxbmc.xjson('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":1,"properties":["file","title","playcount"]},"id":1}')
		self.type = 'movie'
		self.movieid = j['result']['item']['id']
		p = j['result']['item']['file']
		if setting('fm_alternate') == 'true' or p.startswith('smb://') or p.startswith('nfs://'):
			alt_method = True
			self.path = xbmc.validatePath(p)
		else:
			self.path = os.path.abspath(p)
		log("Movie: self.path: %s" % self.path)
		self.title = j['result']['item']['title']
		self.playcount = j['result']['item']['playcount']
		self.rating = None
		self.tag = None


	MOVE_STEPS = 4
	def __move(self, progress):
		progress.start_module(lang(30132), self.MOVE_STEPS)
		try:
			progress.update(lang(30590)) # detecting library place
			destination = setting('fm_movies_destination')
			if alt_method or destination.startswith('smb://') or destination.startswith('nfs://'):
				lib_destiny = xbmc.validatePath(destination)
			else:
				lib_destiny = os.path.abspath(destination)
			if setting('fm_movies_structure') == '0':
				lib_source = os.path.dirname(os.path.dirname(self.path))
			else:
				lib_source = os.path.dirname(self.path)
		 	if lib_destiny == lib_source:
		 		raise Exception(lang(30607))
			progress.update(lang(30506)) # moving files
			destination = lib_destiny
			source = os.path.dirname(self.path)
			if setting('fm_movies_structure') == '0': # multiple folders
				count = utilfile.count_manage_directory(alt_method, source)
				if not dialog.warning(lang(30132), count):
					raise Exception(lang(30609))
				log("Movie: move source (multiple): %s" % source)
				log("Movie: move destination (multiple): %s" % destination)
				utilfile.move_directory(alt_method, source, destination)
				self.path = os.path.join(destination, self.path.split(os.sep)[-2], os.path.basename(self.path))
				log("Movie: Self path (lib/title/files.*): %s" % self.path)
			else: # single folder
				match = os.path.splitext(os.path.basename(self.path))[0]
				count = utilfile.count_manage_files(alt_method, source, match)
				if not dialog.warning(lang(30132), count):
					raise Exception(lang(30609))
				log("Movie: move source (single): %s" % source)
				log("Movie: move destination (single): %s" % destination)
				utilfile.move_files(alt_method, source, destination, match)
				self.path = os.path.join(destination, os.path.basename(self.path))
				log("Movie: Self path: %s" % self.path)
			progress.update(lang(30513)) # updating library
			progress.update_library(self.path)
			self.movieid = utilxbmc.get_movieid_by_path(self.path)
			if self.movieid:
				progress.update(lang(30514)) # setting watched
				utilxbmc.set_movie_playcount(self.movieid, self.playcount+1)
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
			alt_method = setting('fm_alternate') == 'true'
			remove_empty = setting('fm_movie_remove_empty') == 'true'
			if setting('fm_movies_structure') == '0': # multiple folders
				count = utilfile.count_manage_directory(alt_method, source)
				if not dialog.warning(lang(30133), count):
					raise Exception(lang(30609))
				utilfile.delete_directory(alt_method, source)
			else: # single folder
				match = os.path.splitext(os.path.basename(self.path))[0]
				count = utilfile.count_manage_files(alt_method, source, match)
				log("Movie: delete match: %s" % match)
				if not dialog.warning(lang(30133), count):
					raise Exception(lang(30609))
				utilfile.delete_files(alt_method, source, match, remove_empty)
			progress.update(lang(30513)) # updating library
			progress.update_library(self.path)
			self.movieid = None
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
			if not self.movieid:
				raise Exception(lang(30604))
			progress.update(lang(30598)) # setting old playcount
			utilxbmc.set_movie_playcount(self.movieid, self.playcount)
		except Exception, e:
			dialog.error(e.message)
		finally:
			progress.finish_module()


	SET_TAG_STEPS = 1
	def __set_tag(self, progress):
		progress.start_module(lang(30702), self.SET_TAG_STEPS)
		try:
			if not self.movieid:
				raise Exception(lang(30604))
			progress.update(lang(30597)) # setting tag
			utilxbmc.set_movie_tag(self.movieid, self.tag)
		except Exception, e:
			dialog.error(e.message)
		finally:
			progress.finish_module()


	RATE_LIB_STEPS = 1
	def __rate_lib(self, progress):
		progress.start_module(lang(30204), self.RATE_LIB_STEPS)
		try:
			if not self.movieid:
				raise Exception(lang(30604))
			progress.update(lang(30522)) # updating rating
			log("Movie ID is %d" % self.movieid)
			utilxbmc.set_movie_rating(self.movieid, self.rating)
		except Exception, e:
			dialog.error(e.message)
		finally:
			progress.finish_module()


	RATE_TAG_STEPS = 1
	def __rate_tag(self, progress):
		progress.start_module(lang(30205), self.RATE_TAG_STEPS)
		try:
			if not self.movieid:
				raise Exception(lang(30604))
			progress.update(lang(30524)) # setting tag
			tag = setting('rt_movies_tag_text')
			if '%s' in tag:
				tag = tag % self.rating
			utilxbmc.set_movie_tag(self.movieid, tag)
		except Exception, e:
			dialog.error(e.message)
		finally:
			progress.finish_module()


	def ended(self):
		log("Movie: Playback ended")
		# pre confirm
		steps = 0
		move = False
		delete = False
		preserve_playcount = False
		set_tag = False
		rate_lib = False
		rate_tag = False
		if setting('confirm') == 'true':
			log("Movie: Show confirm dialog")
			monitor.waitForAbort(int(setting('wait_dialog')))
		if setting('fm_movies_manage') == '1': # move
			if dialog.proceed(self.title, lang(30132)):
				move = True
				steps += self.MOVE_STEPS
		elif setting('fm_movies_manage') == '2': # delete
			if dialog.proceed(self.title, lang(30133)):
				delete = True
				steps += self.DELETE_STEPS
		if setting('pt_movies_playcount') == 'true':
				preserve_playcount = True
				steps += self.PRESERVE_PLAYCOUNT_STEPS
		if setting('pt_movies_tag') == 'true':
				set_tag = True
				steps += self.SET_TAG_STEPS
		if setting('rt_movies_lib') == 'true':
				rate_lib = True
				steps += self.RATE_LIB_STEPS
		if setting('rt_movies_tag') == 'true':
				rate_tag = True
				steps += self.RATE_TAG_STEPS

		# pre settings
		if move:
			alt_method = setting('fm_alternate') == 'true'
			if alt_method:
				destiny = xbmc.validatePath(setting('fm_movies_destination'))
			else:
				destiny = os.path.abspath(setting('fm_movies_destination'))
			while not destiny or destiny == '.':
				destiny = xbmcgui.Dialog().browse(3, lang(30525) % info('name'), 'files')
				if alt_method:
					destiny = xbmc.validatePath(destiny)
				else:
					destiny = os.path.abspath(destiny)
			set_setting('fm_movies_destination', destiny)

		# pre process
		progress = Progress(steps)
		if not setting('remove_video') == 'true':
			if rate_tag:
				tag = setting('rt_movies_tag_text')
				while not tag:
					tag = xbmcgui.Dialog().input(lang(30206))
				set_setting('rt_movies_tag_text', tag)
				# pre context
			if set_tag:
				tag = xbmcgui.Dialog().input(lang(30599) % self.title)
				while not tag:
					tag = xbmcgui.Dialog().input(lang(30599) % self.title)
				self.tag = tag
			if rate_lib or rate_tag:
				rating = dialog.rating(self.title)
				while not rating:
					rating = dialog.rating(self.title)
				self.rating = rating
			if preserve_playcount:
				self.__preserve_playcount(progress)
			if set_tag:
				self.__set_tag(progress)
			if rate_lib:
				self.__rate_lib(progress)
			if rate_tag:
				self.__rate_tag(progress)
		if move:
			self.__move(progress)
		elif delete:
			self.__delete(progress)

		# post confirm
		quit_menu = False
		logoff = False
		display_off = False
		if setting('ps_movies_quit_menu') == 'true':
			if dialog.proceed(self.title, lang(30402)):
				quit_menu = True
		if setting('ps_movies_logoff') == 'true':
			if dialog.proceed(self.title, lang(30407)):
				logoff = True
		if setting('ps_movies_display_off') == 'true':
			if dialog.proceed(self.title, lang(30404)):
				display_off = True
		# post processing
		if quit_menu:
			self.show_quit_menu()
		if logoff:
			self.logoff_user()
		if display_off:
			self.turn_display_off()
