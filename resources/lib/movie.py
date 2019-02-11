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
        try:
            j = utilxbmc.xjson({
                "jsonrpc": "2.0",
                "method": "Player.GetItem",
                "params": { "playerid": 1, "properties": ["file", "title", "playcount"] },
                "id": 1
            })
            self.type = 'movie'
            self.movieid = j['item']['id']
            p = j['item']['file']
            if setting('fm_alternate') == 'true' or [y for y in ("smb://", "nfs://") if p.lower().startswith(y)]:
                self.path = xbmc.validatePath(p)
                self.alt_method = True
            else:
                self.path = os.path.abspath(p)
                self.alt_method = False
            log("Movie: self.path=%s, alt_method=%s" % (self.path, self.alt_method))
            self.title = j['item']['title']
            self.playcount = j['item']['playcount']
            self.rating = None
            self.tag = None
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)


    MOVE_STEPS = 4
    def __move(self, progress):
        progress.start_module(lang(30131), self.MOVE_STEPS)
        try:
            progress.update(lang(30590)) # detecting library place
            if setting('fm_movies_structure') == '0':
                lib_source = os.path.dirname(os.path.dirname(self.path))
            else:
                lib_source = os.path.dirname(self.path)
            if self.destination == lib_source:
                 raise Exception(lang(30607))
            progress.update(lang(30506)) # moving files
            source = os.path.dirname(self.path)
            if setting('fm_movies_structure') == '0': # multiple folders
                count = utilfile.count_manage_directory(self.alt_method, source)
                if not dialog.warning(lang(30131), count):
                    raise Exception(lang(30609))
                utilfile.move_directory(self.alt_method, source, self.destination)
                self.path = os.path.join(self.destination, self.path.split(os.sep)[-2], os.path.basename(self.path))
            else: # single folder
                match = os.path.splitext(os.path.basename(self.path))[0]
                count = utilfile.count_manage_files(self.alt_method, source, match)
                if not dialog.warning(lang(30131), count):
                    raise Exception(lang(30609))
                utilfile.move_files(self.alt_method, source, self.destination, match)
                self.path = os.path.join(self.destination, os.path.basename(self.path))
            log("Movie.__move: source=%s, destination=%s, self.path=%s, alt_method=%s" % (source, self.destination, self.path, self.alt_method))
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
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
        finally:
            progress.finish_module()


    DELETE_STEPS = 2
    def __delete(self, progress):
        progress.start_module(lang(30132), self.DELETE_STEPS)
        try:
            progress.update(lang(30516)) # deleting files
            source = os.path.dirname(self.path)
            remove_empty = setting('fm_movie_remove_empty') == 'true'
            if setting('fm_movies_structure') == '0': # multiple folders
                count = utilfile.count_manage_directory(self.alt_method, source)
                if not dialog.warning(lang(30132), count):
                    raise Exception(lang(30609))
                utilfile.delete_directory(self.alt_method, source)
            else: # single folder
                match = os.path.splitext(os.path.basename(self.path))[0]
                count = utilfile.count_manage_files(self.alt_method, source, match)
                log("Movie.__delete: match=%s" % match)
                if not dialog.warning(lang(30132), count):
                    raise Exception(lang(30609))
                utilfile.delete_files(self.alt_method, source, match, remove_empty)
            progress.update(lang(30513)) # updating library
            progress.update_library(self.path)
            self.movieid = None
            self.path = None
        except OSError:
            dialog.error(lang(30610))
        except ValueError as err:
            ValueErrorHandler(err)
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
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
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
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
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
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
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
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
        except Exception as e:
            if debug.get():
                log(debug.traceback.print_exc(), xbmc.LOGERROR)
            debug.exception_dialog(e)
        finally:
            progress.finish_module()


    def ended(self):
        excludelist = setting('fm_movies_excludelist').lower().split(',')
        log("Movie.ended: excludelist=%s" % excludelist)
        if any(self.path.lower().find (v.strip()) >= 1 for v in excludelist):
            log("Movie.ended: Exclude word matched, stop further processing")
            return
        # pre confirm
        steps = 0
        move = False
        delete = False
        preserve_playcount = False
        set_tag = False
        rate_lib = False
        rate_tag = False
        if setting('confirm') == 'true':
            wait_dialog = setting('wait_dialog')
            log("Movie.ended: confirm dialog %d sec delayed" % wait_dialog)
            monitor.waitForAbort(int(setting('wait_dialog')))
        if setting('fm_movies_manage') == '2' or setting('fm_movies_manage') == '3': # delete
            if dialog.proceed(self.title, lang(30132)):
                delete = True
                steps += self.DELETE_STEPS
        if setting('fm_movies_manage') == '1' or (setting('fm_movies_manage') == '3' and not delete): # move
            if dialog.proceed(self.title, lang(30131)):
                move = True
                steps += self.MOVE_STEPS
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
            destination = setting('fm_movies_destination')
            if self.alt_method or destination.lower().startswith('smb://') or destination.lower().startswith('nfs://'):
                self.destination = xbmc.validatePath(destination)
                self.alt_method = True
            else:
                self.destination = os.path.abspath(destination)
            while not self.destination or self.destination == '.':
                destination = xbmcgui.Dialog.browse(3, lang(30525) % info('name'), 'files')
                if self.alt_method or destination.lower().startswith('smb://') or destination.lower().startswith('nfs://'):
                    self.destination = xbmc.validatePath(destination)
                    self.alt_method = True
                else:
                    self.destination = os.path.abspath(destination)
            log("Movie.ended: self.destination=%s, alt_method=%s" % (self.destination, self.alt_method))
            set_setting('fm_movies_destination', self.destination)

        # pre process
        progress = Progress(steps)
        if not setting('remove_video') == 'true':
            if rate_tag:
                tag = setting('rt_movies_tag_text')
                while not tag:
                    tag = xbmcgui.Dialog.input(lang(30206))
                set_setting('rt_movies_tag_text', tag)
                # pre context
            if set_tag:
                tag = xbmcgui.Dialog.input(lang(30599) % self.title)
                while not tag:
                    tag = xbmcgui.Dialog.input(lang(30599) % self.title)
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
