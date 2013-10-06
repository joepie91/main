#!/usr/bin/python

import re, mechanize, subprocess, sys

if len(sys.argv) < 2:
	print "Syntax: putlocker-vlc <putlocker/sockshare url>"
	sys.exit(1)

url = sys.argv[1]
matches = re.search("\/(file|embed)\/([A-Z0-9]+)", url)

if matches is None:
	print "The URL you provided does not appear to be a valid PutLocker or SockShare URL."
	sys.exit(1)

video_id = matches.group(2)
matches = re.search("(http:\/\/[^/]+)\/", url)
domain = matches.group(1)
print "Video ID: %s | Host: %s" % (video_id, domain)

try:
	print "Retrieving ad page..."
	browser = mechanize.Browser()
	browser.set_handle_robots(False)
	browser.open("%s/embed/%s" % (domain, video_id))
except:
	print "Something went wrong; the server might be down."
	sys.exit(1)

try:
	print "Skipping ad..."
	browser.select_form(nr=0)
	result = browser.submit()
except:
	print "The file has been removed, or the URL is incorrect."
	sys.exit(1)

matches = re.search("playlist: '([^']+)'", result.read())
playlist = matches.group(1)
print "Retrieved playlist URL."

browser.open(domain + playlist)
print "Retrieved playlist data."
matches = re.search("url=\"([^\"]+)\" type=\"video\/x-flv\"", browser.response().read())
video_file = re.sub("&amp;","&",matches.group(1))
print "Found video URL."

print "Launching VLC with the specified video file..."
cmd = ["vlc", "--play-and-exit"]
cmd.append(video_file)
subprocess.call(cmd)
