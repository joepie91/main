#!/usr/bin/python

import sys, urllib2, re

contents = urllib2.urlopen(sys.argv[1]).read()

data = re.search('<a class="highlighted-btn" href="([^"]+)">Premium', contents)
url = data.group(1)

print url
