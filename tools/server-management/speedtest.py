#!/usr/bin/env python

import urllib2, time, urllib
from lxml import etree

def avg(inp):
	return (reduce(lambda x, y: x + y, inp) / len(inp))

referer = "http://c.speedtest.net/flash/speedtest.swf?v=316125"
num = 1353968072002
config_url = "http://speedtest.net/speedtest-config.php?x=%d" % num
server_url = "http://speedtest.net/speedtest-servers.php?x=%d" % num
download_path = "/random%dx%d.jpg?x=%d&y=%d"
upload_path = "/upload.php?x=%d" % num
latency_path = "/latency.txt?x=%d" % num
sizes = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]

servers = []
server_count = 0

# First, get our own details.
result = urllib2.urlopen(config_url)

for event, element in etree.iterparse(result):
	if element.tag == "client":
		my_ip = element.get("ip")
		my_isp = element.get("isp")
		my_latitude = float(element.get("lat"))
		my_longitude = float(element.get("lon"))
		dl_average = float(element.get("ispdlavg"))
		ul_average = float(element.get("ispulavg"))
		
		print "You are %s (%s), with latitude %f and longitude %f. Your ISPs average download speed is %.3f MB/sec, and their average upload speed is %.3f MB/sec." % (my_ip, my_isp, my_latitude, my_longitude, dl_average / 8 / 1024 / 1024, ul_average / 8 / 1024 / 1024)

print "Retrieving server list...",

# Retrieve and parse list of servers.
result = urllib2.urlopen(server_url)

for event, element in etree.iterparse(result):
	if element.tag == "server":
		hostname = element.get("url").replace("/upload.php", "")
		latitude = float(element.get("lat"))
		longitude = float(element.get("lon"))
		location = element.get("name")
		country = element.get("country")
		sponsor = element.get("sponsor")
		
		distance = abs(my_latitude - latitude) + abs(my_longitude - longitude)
		
		servers.append((distance, hostname, latitude, longitude, location, country, sponsor))
		server_count += 1
		
		print "\rRetrieving server list... %d servers found so far" % server_count,
		
# Sort the server list by distance.
servers = sorted(servers, key=lambda server: server[0])

print "\nFound 5 closest servers. Determining optimal latency..."

fastest_server = ()
fastest_latency = 0

for server in servers[:5]:
	# Take 3 samples of each server.
	latencies = []
	
	for i in xrange(0, 3):
		request = urllib2.Request(server[1] + latency_path)
		
		start_time = time.time()
		urllib2.urlopen(request)
		end_time = time.time()
		
		latencies.append((end_time - start_time) * 1000)
	
	latency = avg(latencies)
	
	if fastest_latency == 0 or latency < fastest_latency:
		fastest_latency = latency
		fastest_server = server
	
	print "\rFastest server so far is '%s' with %dms ping... (%s)" % (fastest_server[6], fastest_latency, latencies),

print "\nTarget server is '%s'. Testing download speed..." % fastest_server[6]

latency = fastest_latency

size = 0

while size < 8:
	# Take 3 samples
	speeds = []
	times = []
	
	for i in xrange(0, 3):
		target_file = download_path % (sizes[size], sizes[size], num, i + 1)
		request = urllib2.urlopen(fastest_server[1] + target_file)
		filesize = int(request.info()['Content-Length'])
		block_size = 4096
		r = 0
		start_time = time.time()
		
		while r < filesize:
			request.read(block_size)
			r += block_size
			speed = r / (time.time() - start_time)
			print "\rSize %d, attempt %d... %.3f MB/sec" % (sizes[size], i + 1, speed / 1024 / 1024),
		
		end_time = time.time()
		
		speeds.append(speed)
		times.append(end_time - start_time)
		
		print ""
		request.close()
	
	if avg(times) < 4:
		size += 1
	else:
		break

# Take result from last speedtest as authorative.
if size >= 8:
	size = 7

download_speed = avg(speeds)

#print "Average speed, sample size %d, is %.3f MB/sec" % (sizes[size], download_speed / 1024 / 1024)

print "Latency: %dms\tDownload speed: %.3f MB/sec" % (latency, download_speed / 1024 / 1024)
print "NOTE: Due to function call overhead, the latency is, at best, an estimation."
