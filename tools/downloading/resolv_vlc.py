#!/usr/bin/python

import sys, subprocess, resolv

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
	cmd = ["vlc", "--play-and-exit"]
	cmd.append(url)
	subprocess.call(cmd)
except IndexError:
	print "That was not an option."
