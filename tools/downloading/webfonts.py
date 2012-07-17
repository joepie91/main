#!/usr/bin/python

import sys, urllib, urllib2, re, os, random, string

url = raw_input("Stylesheet URL: ")

def random_string(length):
	return ''.join(random.choice(string.letters) for i in xrange(length))

def create_dir():
	target_dir = "fonts/%s" % random_string(10)
	
	try:
		os.makedirs(target_dir + "/fonts")
		os.makedirs(target_dir + "/stylesheets")
	except OSError:
		return create_dir()
	else:
		return target_dir

def retrieve_page(url, useragent):
	request = urllib2.Request(url, None, {'User-Agent': useragent})
	return urllib2.urlopen(request).read()
	
def get_links(url, useragent):
	contents = retrieve_page(url, useragent)
	return re.findall('https?://([^\)]+)', contents)

target_dir = create_dir()
font_files = []

#for font_file in get_links(url, "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"):
#	font_files.append(font_file)
	
#for font_file in get_links(url, "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"):
#	font_files.append(font_file)
	
for font_file in get_links(url, "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1190.0 Safari/537.1 SUSE/22.0.1190.0"):
	font_files.append(font_file)

total = len(font_files)
done = 0

for result in font_files:
	file_url = "http://%s" % result
	filename = os.path.basename(file_url)
	urllib.urlretrieve(file_url, "%s/fonts/%s" % (target_dir, filename))
	done += 1
	print "[%d/%d] Downloaded %s" % (done, total, filename)

print "The font files and stylesheet can be found in %s" % target_dir
