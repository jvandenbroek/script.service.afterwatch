import os
import shutil
import xbmcvfs

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
			shutil.move(os.path.join(source, f), destination)
	# delete source directory if empty
	if del_empty and len(os.listdir(source)) == 0:
		os.rmdir(source)

def __delete_directory(source):
	shutil.rmtree(source)

def __delete_files(source, match, del_empty):
	# delete files from source if match
	files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
	for f in files:
		if os.path.splitext(f)[0].startswith(match):
			f = os.path.join(source, f)
			#os.chmod(f, 0777)
			os.remove(f)
	# delete source directory if empty
	if del_empty and len(os.listdir(source)) == 0:
		os.rmdir(source)

def __copy_directory_alt(source, destination):
	destination = os.path.join(destination, os.path.basename(source))
	xbmcvfs.mkdirs(destination) # todo error if exists?
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		src = os.path.join(source, f)
		dest = os.path.join(destination, f)
		xbmcvfs.copy(src, dest)
	for d in dirs:
		d = os.path.join(source, d)
		__copy_directory(d, destination)

def __copy_files_alt(source, destination, match):
	# create directories if needed
	xbmcvfs.mkdirs(destination)
	# move files from source to destination if match
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		if os.path.splitext(f)[0].startswith(match):
			src = os.path.join(source, f)
			dest = os.path.join(destination, f)
			xbmcvfs.copy(src, dest) # todo error

def __delete_directory_alt(source):
	dirs, files = xbmcvfs.listdir(source)
	log("_delete_directory_alt dirs: %s files: %s" % dirs, files)
	for d in dirs:
		d = os.path.join(source, d)
		__delete_directory(d)
	for f in files:
		f = os.path.join(source, f)
		xbmcvfs.delete(f)
	xbmcvfs.rmdir(source)

def __delete_files_alt(source, match, del_empty):
	# delete files from source if match
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		if os.path.splitext(f)[0].startswith(match):
			f = os.path.join(source, f)
			xbmcvfs.delete(f)
	# delete source directory if empty
	if del_empty and len(xbmcvfs.listdir(source)) == 0:
		xbmcvfs.rmdir(source)

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
