#!/usr/bin/python

import os, argparse, hashlib, glob

parser = argparse.ArgumentParser(description='Renames files according to their own SHA1 hash.')

parser.add_argument('-p', dest='pattern', action='store', default='*',
                   help='glob pattern (including path) that has to be matched for a file to be renamed')

args = parser.parse_args()
options = vars(args)

# Select all files matching the given pattern
file_list = glob.glob(options['pattern'])

finished = 0

for targetfile in file_list:	
	try:
		f = open(targetfile, 'rb')
	except IOError:
		continue
	
	try:
		sha1_hash = hashlib.sha1(f.read()).hexdigest()
	except IOError:
		continue
	finally:
		f.close()
		
	file_name, file_extension = os.path.splitext(targetfile)
	
	if file_extension != "":
		new_path = "%s/%s%s" % (os.path.dirname(targetfile), sha1_hash, file_extension)
	else:
		new_path = "%s/%s" % (os.path.dirname(targetfile), sha1_hash)
	
	os.rename(targetfile, new_path)
	
	print "%s -> %s" % (targetfile, new_path)
		
	finished += 1
	
print "Renamed %d files." % finished
