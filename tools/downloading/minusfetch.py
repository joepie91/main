#!/usr/bin/python

import sys, urllib2, re

contents = urllib2.urlopen(sys.argv[1]).read()

data = re.search('"name": ?"([^"]+)", "', contents)
filename = data.group(1)

data = re.search('"secure_prefix": ?"([^"]+)"', contents)
secure_prefix = data.group(1)

data = re.search('"id": ?"([^"]+)"', contents)
link_id = data.group(1)

url = "http://i.minus.com%s/d%s/%s" % (secure_prefix, link_id, filename)

print url
