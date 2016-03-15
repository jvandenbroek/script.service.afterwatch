# -*- coding: utf-8 -*-
import xbmc
import json

def xjson(cmd):
	r = xbmc.executeJSONRPC(cmd)
	j = json.loads(r)
	return j

def version():
	j = xjson('{"jsonrpc":"2.0","method":"Application.GetProperties","params":{"properties":["version"]},"id":1}')
	version = j['result']['version']['major']
	return version

def get_movieid_by_path(path):
	j = xjson('{"jsonrpc":"2.0","method":"VideoLibrary.GetMovies","params":{"properties":["file"]},"id":1}') # todo isto json assim dah erro?
	if 'movies' in j['result']:
		for movie in j['result']['movies']:
			if movie['file'] == path:
				return movie['movieid']

def get_movieid_by_imdb(imdb):
	j = xjson('{"jsonrpc":"2.0","method":"VideoLibrary.GetMovies","params":{"properties":["imdbnumber"]},"id":1}')
	if 'movies' in j['result']:
		for movie in j['result']['movies']:
			if movie['imdbnumber'] == imdb:
				return movie['movieid']

def get_movie_title(movieid):
	j = xjson('{"jsonrpc":"2.0","method":"VideoLibrary.GetMovieDetails","params":{"movieid":%s,"properties":["title"]},"id":1}' % movieid)
	return j['result']['moviedetails']['title']

def get_episodeid_by_path(path):
	j = xjson('{"jsonrpc":"2.0","method":"VideoLibrary.GetEpisodes","params":{"properties":["file"]},"id":1}')
	if 'episodes' in j['result']:
		for episode in j['result']['episodes']:
			if episode['file'] == path:
				return episode['episodeid']

def set_movie_playcount(movieid, playcount):
	cmd = '{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":%d,"playcount":%d},"id":1}' % (movieid, playcount)
	xbmc.executeJSONRPC(cmd)

def set_episode_playcount(episodeid, playcount):
	cmd = '{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":%d,"playcount":%d},"id":1}' % (episodeid, playcount)
	xbmc.executeJSONRPC(cmd)

def set_movie_rating(movieid, rating):
	cmd = '{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":%d,"rating":%s},"id":1}' % (movieid, str(rating))
	xbmc.executeJSONRPC(cmd)

def set_episode_rating(episodeid, rating):
	cmd = '{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":%d,"rating":%s},"id":1}' % (episodeid, str(rating))
	xbmc.executeJSONRPC(cmd)

def set_movie_tag(movieid, tag):
	cmd = '{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":%d,"tag":["%s"]},"id":1}' % (movieid, tag)
	xbmc.executeJSONRPC(cmd)

def play_movie(movieid):
	cmd = '{"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"movieid":%d}},"id":1}' % movieid
	xbmc.executeJSONRPC(cmd)
