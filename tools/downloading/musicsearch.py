#!/usr/bin/python
#http://ex.fm/api/v3/song/search/rameau?results=
import argparse, os, urllib, json, subprocess, urllib2

parser = argparse.ArgumentParser(description='Searches for music files')

parser.add_argument('-c', dest='limit', action='store', default='10',
                   help='maximum amount of results to show (don\'t overdo it please)')

parser.add_argument('-v', dest='vlc', action='store_true', default='false',
                   help='play in VLC media player')

parser.add_argument('query', metavar='QUERY', type=str, nargs='+',
                   help='destination path for generated class files.')

args = parser.parse_args()
options = vars(args)

query = " ".join(options['query'])
limit = int(options['limit'])

results = urllib.urlopen("http://ex.fm/api/v3/song/search/%s?results=%d" % (urllib.quote_plus(query), limit)).read()

try:
	result_object = json.loads(results)
except ValueError:
	print "No valid result was returned from the ex.fm API. Exiting..."
	exit(1)

if result_object['status_code'] != 200:
	print "An error code was returned by the ex.fm API. Exiting..."
	exit(1)

print "Searching for '%s'..." % query

if result_object['total'] <= 0:
	print "No results."
	exit(1)

print ""

for track in result_object['songs']:
	if track['artist'] is None:
		artist = "Unknown"
	else:
		artist = track['artist']
	
	if track['album'] is None:
		album = "Unknown"
	else:
		album = track['album']
	
	if track['title'] is None:
		title = "Unknown"
	else:
		title = track['title']
	
	print "Artist: %s\t Album: %s" % (artist, album)
	print "Title: %s" % title
	print "  %s" % track['url']
	print ""

if options['vlc'] == True:
	print "Playing the first working result in VLC media player..."
	
	working_url = ""
	
	for track in result_object['songs']:
		try:
			response = urllib2.urlopen(track['url'])
		except urllib2.URLError, e:
			continue
		
		headers = response.info()
		
		if "text/html" in headers['Content-Type']:
			continue
		
		working_url = track['url']
		
		break
		
	if working_url != "":
		with open(os.devnull, 'w') as stfu:
			subprocess.Popen(["vlc", "--one-instance", working_url], stdin=None, stdout=stfu, stderr=stfu)
		exit(0)
	else:
		print "No working URLs found."
		exit(1)
