# -*- coding: utf-8 -*-
import os
import shutil
import xbmcvfs
import re
from utils import log
from debug import debug

## PUBLIC MANAGEMENT
def move_directory(alt_method, source, destination):
	if not alt_method:
		__move_directory(source, destination)
	else:
		__copy_directory_alt(source, destination)
		__delete_directory_alt(source)

def move_files(alt_method, source, destination, match, del_empty=False):
	if not alt_method:
		__move_files(source, destination, match, del_empty)
	else:
		__copy_files_alt(source, destination, match)
		__delete_files_alt(source, match, del_empty)

def delete_directory(alt_method, source):
	if not alt_method:
		__delete_directory(source)
	else:
		__delete_directory_alt(source)

def delete_files(alt_method, source, match, del_empty=False):
	if not alt_method:
		__delete_files(source, match, del_empty)
	else:
		__delete_files_alt(source, match, del_empty)


## PUBLIC COUNT
def count_manage_directory(alt_method, source):
	if not alt_method:
		count = __count_manage_directory(source)
	else:
		count = __count_manage_directory_alt(source)
	return count

def count_manage_files(alt_method, source, match):
	if not alt_method:
		count = __count_manage_files(source, match)
	else:
		count = __count_manage_files_alt(source, match)
	return count



## PRIVATE REGULAR
def __copy_directory(source, destination):
	shutil.copytree(source,destination)

def __move_directory(source, destination):
	shutil.move(source,destination)

def __move_files(source, destination, match, del_empty):
	# create directories if needed
	if not os.path.isdir(destination):
		os.makedirs(destination)
	# move files from source to destination if match
	files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
	for f in files:
		if os.path.splitext(f)[0].startswith(match):
			# Don't match copies of files
			m = re.match(r'^(.((?!\(\d+\)$)))*$', os.path.splitext(f)[0])
			if re.search(r'(\(\d+\)$)', match) or (m and m.group(0).startswith(match)):
				shutil.move(os.path.join(source, f), destination)
	# delete source directory if empty
	if del_empty and len(os.listdir(source)) == 0:
		os.rmdir(source)

def __delete_directory(source):
	shutil.rmtree(source)

def __delete_files(source, match, del_empty):
	# delete files from source if match
	count = 0
	hidden = ['Thumbs.db','.DS_Store']
	files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
	for f in files:
		if os.path.splitext(f)[0].startswith(match):
			# Don't match copies of files
			if not re.search(r'(\(\d+\)$)', match):
				m = re.match(r'^(.((?!\(\d+\)$)))*$', os.path.splitext(f)[0])
				if not (m and m.group(0).startswith(match)):
					continue
			f = os.path.join(source, f)
			#os.chmod(f, 0777)
			try:
				log("delete_files: os.remove: f=%s" % (f))
				os.remove(os.path.realpath(f))
			except OSError as e:
				raise ValueError('os.remove (' + e.errno + ')', os.path.realpath(f))
		else:
			for h in hidden:
				if os.path.splitext(f)[0].startswith(h):
					count += 1
	# delete source directory if empty
	length = len(os.listdir(source))
	log("delete_files: del_emtpy=%d, length=%d, count=%d, source=%s" % (del_empty, length, count, source))
	if del_empty and length == count:
		try:
			if count > 0:
				for h in hidden:
					if os.path.isfile(os.path.join(source, h)):
						log("delete_files: os.remove: f=%s, count=%s" % (h, count))
						try:
							os.remove(h)
						except OSError:
							raise ValueError('os.remove', h)
			os.rmdir(source)
		except OSError:
			raise ValueError('os.rmdir', source)

def __copy_directory_alt(source, destination):
	destination = os.path.join(destination, os.path.basename(source))
	if not xbmcvfs.mkdirs(destination):
		raise ValueError('xbmcvfs.mkdirs', destination)
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		src = os.path.join(source, f)
		dest = os.path.join(destination, f)
		if not xbmcvfs.copy(src, dest):
			raise ValueError('xbmcvfs.copy', src, dest)
	for d in dirs:
		src = os.path.join(source, d)
		dest = os.path.join(destination, d)
		if not xbmcvfs.mkdirs(dest):
			raise ValueError('xbmcvfs.mkdirs', dest)
		dirs2, files2 = xbmcvfs.listdir(src)
		for d2 in dirs2:
			dest2 = os.path.join(dest, d2)
			if not xbmcvfs.mkdirs(dest2):
				raise ValueError('xbmcvfs.mkdirs', dest2)
		for f2 in files2:
			src2 = os.path.join(src, f2)
			dest2 = os.path.join(dest, f2)
			if not xbmcvfs.copy(src2, dest2):
				raise ValueError('xbmcvfs.copy', src2, dest2)
#		__copy_directory(d, destination)

def __copy_files_alt(source, destination, match):
	# create directories if needed
	if not xbmcvfs.mkdirs(destination):
		raise ValueError('xbmcvfs.mkdirs', destination)
	# move files from source to destination if match
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		if os.path.splitext(f)[0].startswith(match):
			# Don't match copies of files
			m = re.match(r'^(.((?!\(\d+\)$)))*$', os.path.splitext(f)[0])
			if re.search(r'(\(\d+\)$)', match) or (m and m.group(0).startswith(match)):
				src = os.path.join(source, f)
				dest = os.path.join(destination, f)
				if not xbmcvfs.copy(src, dest):
					raise ValueError('xbmcvfs.copy', src, dest)

def __delete_directory_alt(source):
	hidden = ['Thumbs.db','.DS_Store']
	dirs, files = xbmcvfs.listdir(source)
	for d in dirs:
		d = os.path.join(source, d)
		dirs2, files2 = xbmcvfs.listdir(d)
		for d2 in dirs2:
			d2 = os.path.join(d, d2)
			if not xbmcvfs.rmdir(d2):
				raise ValueError('xbmcvfs.rmdir', d2)
		for f2 in files2:
			f2 = os.path.join(d, f2)
			if not xbmcvfs.delete(f2):
				raise ValueError('xbmcvfs.delete', f2)
		for h in hidden:
			h = os.path.join(d, h)
			if xbmcvfs.exists(h):
				if not xbmcvfs.delete(h):
					raise ValueError('xbmcvfs.delete', h)
		if not xbmcvfs.rmdir(d):
			raise ValueError('xbmcvfs.rmdir', d)

	for f in files:
		f = os.path.join(source, f)
		if not xbmcvfs.delete(f):
			raise ValueError('xbmcvfs.delete', f)
	for h in hidden:
		h = os.path.join(source, h)
		if xbmcvfs.exists(h):
			if not xbmcvfs.delete(h):
				raise ValueError('xbmcvfs.delete', h)

	if not xbmcvfs.rmdir(source):
		raise ValueError('xbmcvfs.rmdir', source)



def __delete_files_alt(source, match, del_empty):
	# delete files from source if match
	count = 0
	hidden = ['Thumbs.db','.DS_Store']
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		if os.path.splitext(f)[0].startswith(match):
			# Don't match copies of files
			if not re.search(r'(\(\d+\)$)', match):
				m = re.match(r'^(.((?!\(\d+\)$)))*$', os.path.splitext(f)[0])
				if not (m and m.group(0).startswith(match)):
					continue
			f = os.path.join(source, f)
			log("xbmcvfs.delete: f=%s" % (f))
			if not xbmcvfs.delete(f):
				raise ValueError('xbmcvfs.delete', f)
		else:
			for h in hidden:
				if os.path.splitext(f)[0].startswith(h):
					count += 1

	# delete source directory if empty
	dirs, files = xbmcvfs.listdir(source)
	length = len(files)
	if del_empty and length > 0 and debug.get():
		files_left = ""
		if length > 1:
			files_left = "%s (and %d more)" % (files[0], length - 1)
		log("xbmcvfs.listdir: file(s) left in folder=%s" % files_left)
	log("xbmcvfs.rmdir: del_empty=%d, length=%d, count=%d, source=%s" % (del_empty, length, count, source))
	if del_empty and length == count:
		if count > 0:
			for h in hidden:
				f = os.path.join(source, h)
				log("xbmcvfs.delete: f=%s, count=%d" % (f, count))
				if not xbmcvfs.delete(f):
					raise ValueError('xbmcvfs.delete', f)
		log("xbmcvfs.rmdir: source=%s" % (source))
		if not xbmcvfs.rmdir(source):
			raise ValueError('xbmcvfs.rmdir', source)


## PRIVATE COUNT
def __count_manage_directory(source):
	count = 0
	dirs = [f for f in os.listdir(source) if not os.path.isfile(os.path.join(source, f))]
	files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
	for d in dirs:
		d = os.path.join(source, d)
		count += __count_manage_directory(d)
	for f in files:
		count += 1
	return count

def __count_manage_files(source, match):
	count = 0
	files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
	for f in files:
		if match == os.path.splitext(f)[0]:
			count += 1
	return count

def __count_manage_directory_alt(source):
	count = 0
	dirs, files = xbmcvfs.listdir(source)
	for d in dirs:
		d = os.path.join(source, d)
		count += __count_manage_directory_alt(d)
	for f in files:
		count += 1
	return count

def __count_manage_files_alt(source, match):
	count = 0
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		if match == os.path.splitext(f)[0]:
			count += 1
	return count
