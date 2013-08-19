import requests, re, json, sys

import lxml.html
from lxml import etree
from lxml.etree import XMLParser

# Dependencies: requests, lxml
# Usage: python flickrgrab.py http://url.to.flickr/profile/page
# Saves to working directory

# http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
def DownloadFile(url):
	local_filename = url.split('/')[-1]
	r = requests.get(url, stream = True) # here we need to set stream = True parameter
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
				f.flush()
	return local_filename

pagedata = requests.get(sys.argv[1]).text

parser = XMLParser(ns_clean=True, recover=True)
doc = lxml.html.fromstring(pagedata)

elem = doc.xpath("//div[@class='Pages']/@data-page-count")

if len(elem) > 0:
	page_count = int(elem[0])
else:
	print "No page count found"
	exit(1)

print "Retrieving %d pages worth of images..." % page_count

total_done = 0

for i in xrange(1, page_count + 1):
	pictures = requests.get("%s?data=1&page=%d&append=1" % (sys.argv[1], i)).json()
	
	for picture in pictures:
		try:
			filename = picture['sizes']['o']['file']
			url = picture['sizes']['o']['url']
			DownloadFile(url)
			
			total_done += 1
			print "Downloaded %d full-size images..." % total_done
		except KeyError, e:
			print "Skipped image because of missing URL or filename"
			
	print "Flipping to page %d..." % i
