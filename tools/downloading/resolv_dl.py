#!/usr/bin/python

import sys, urllib, resolv

result = resolv.recurse(sys.argv[1])

if 'videos' in result:
	urls = result['videos']
elif 'files' in result:
	urls = result['files']
else:
	print "Not a video or file."
	exit(1)

print "Title: %s" % result['title']

good_urls = []

if len(urls) > 0:
	for url in urls:
		if url['priority'] == 1:
			good_urls.append(url)

i = 0

for url in good_urls:
	filetype = url['format']
	print "%d. %s" % (i, url['format'])
	i += 1
	
choice = int(raw_input("Make a filetype choice: "))

try:
	url = good_urls[choice]['url']
	dest = raw_input("Pick a filename to store the file as: ")
	print "Downloading...",
	urllib.urlretrieve (url, dest)
	print "Done!"
except IndexError:
	print "That was not an option."
