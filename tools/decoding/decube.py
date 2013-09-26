# Decodes Ioncube-encoded HTML page source from a terminal
#
# Instructions:
#    python decube.py <URL of page>
#
# Author: Sven Slootweg
# License: WTFPL, use it as you wish

import re, sys, urllib, math

body = re.search("<script[^>]*>(.*)<\/script>", urllib.urlopen(sys.argv[1]).read()).group(1)
#script = re.search('eval\(unescape\("([^"]+)"\)\);', body).group(1)   # We don't actually need this, but we might in the future
first_payload = re.search('c="([^"]+)"', body).group(1)
second_payload = re.search('x\("([^"]+)"\);', body).group(1)

deobfuscated = ""

for i in xrange(0, len(first_payload)):
	if i % 3 == 0:
		deobfuscated += "%"
	else:
		deobfuscated += first_payload[i]

decoded = urllib.unquote(deobfuscated)

charmap = [int(x) for x in re.search("Array\(([^)]+)\)", decoded).group(1).split(",")]
block_size = int(re.search(",b=([0-9]+),", decoded).group(1))
payload_left = len(second_payload)

block_count = int(math.ceil(float(payload_left) / block_size))
shift = 0
bit_buffer = 0  # This holds unprocessed data
output_buffer = ""

for block_num in xrange(0, block_count):
	# Extract the data for this block
	block_start = block_num * block_size
	block_end = (block_num + 1) * block_size
	block = second_payload[block_start:block_end]
	
	for pos in xrange(0, min(block_size, payload_left)):
		charnum = ord(block[pos]) - 48
		bit_buffer |= (charmap[charnum] << shift)
		
		if shift > 0:
			output_buffer += chr(165 ^ bit_buffer & 255)
			bit_buffer >>= 8
			shift -= 2
		else:
			# Loop the shift value around
			shift = 6
			
		payload_left -= 1

print output_buffer
