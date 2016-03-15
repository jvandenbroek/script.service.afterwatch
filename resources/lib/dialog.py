# -*- coding: utf-8 -*-
#import xbmc
import xbmcgui
from resources.lib.utils import info, lang, setting

def proceed(title, subtitle):
	proceed = True
	if setting('confirm') == 'true':
		proceed = xbmcgui.Dialog().yesno(info('name'), title, lang(30526) % subtitle)
	return proceed

def warning(module, count):
	proceed = True
	threshold = int(setting('fm_warn'))
	if count > threshold:
		proceed = xbmcgui.Dialog().yesno(info('name'), lang(30588) % (module, count))
	return proceed

def error(msg):
	xbmcgui.Dialog().ok(info('name'), str(msg))

def notification(msg):
	xbmc.executebuiltin('Notification(%s,%s,5000,%s)' % (info('name'), msg, info('icon')))
	# todo xbmcgui.Dialog().notification('Movie Trailers', 'Finding Nemo download finished.', xbmcgui.NOTIFICATION_INFO, 5000)

def rating(title):
	l = ['10 **********','9 *********','8 ********','7 *******','6 ******','5 *****','4 ****','3 ***','2 **','1 *']
	i = xbmcgui.Dialog().select(lang(30512) % (info('name'), title), l)
	if not i == -1:
		rating = 10 - i
		return rating
