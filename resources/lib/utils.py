# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Thomas Amland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import os
import re
import sys
import xbmc
import xbmcgui
import json
import xbmcaddon
import dialog
from urllib import unquote
from threading import Condition

__addon__ = xbmcaddon.Addon()

def log(msg, level=xbmc.LOGDEBUG):
	if setting('debug') == 'true':
		xbmc.log(('[%s] %s' % (info('name'), msg)), level)


def info(id):
	return __addon__.getAddonInfo(id)


def lang(id):
	return  __addon__.getLocalizedString(id)


def setting(id):
	return __addon__.getSetting(id)


def set_setting(id, val):
	__addon__.setSetting(id, val)


def encode_path(path):
    """os.path does not handle unicode properly, i.e. when locale is C, file
    system encoding is assumed to be ascii. """
    if sys.platform.startswith('win'):
        return path
    return path.encode('utf-8')


def decode_path(path):
    if sys.platform.startswith('win'):
        return path
    return path.decode('utf-8')


def is_url(path):
    return re.match(r'^[A-z]+://', path) is not None


def escape_param(s):
    escaped = s.replace('\\', '\\\\').replace('"', '\\"')
    return '"' + escaped + '"'


def rpc(method, **params):
    params = json.dumps(params, encoding='utf-8')
    query = '{"jsonrpc": "2.0", "method": "%s", "params": %s, "id": 1}' % (method, params)
    return json.loads(xbmc.executeJSONRPC(query), encoding='utf-8')


def ValueErrorHandler(err):
	if err[0] == 'xbmcvfs.mkdirs':
		log("ValueError Exception: Error creating folder: %s" % err[1])
		dialog.error(lang(30611) + ' %s' % err[1])
	if err[0] == 'xbmcvfs.rmdir':
		log("ValueError Exception: Error removing folder: %s" % err[1])
		dialog.error(lang(30612) + ' %s' % err[1])
	if err[0] == 'xbmcvfs.delete':
		log("ValueError Exception: Error removing file: %s" % err[1])
		dialog.error(lang(30613) + ' %s' % err[1])
	if err[0] == 'xbmcvfs.copy':
		log("ValueError Exception: Error copying %s to %s" % (err[1], err[2]))
		dialog.error(lang(30614) + ' %s -> %s' % (err[1], err[2]))
