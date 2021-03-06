#!/usr/bin/python

# This script will run the appropriate command to print archive contents to stdout
# Written by Sven Slootweg, Licensed under WTFPL - in other words, feel free to reuse for whatever purpose you desire.

import os, argparse, sys, subprocess

parser = argparse.ArgumentParser(description='Prints the uncompressed contents of archives to stdout, based on certain criteria.')

parser.add_argument('pattern', metavar='FILES', type=str, nargs='+',
                   help='files to parse')
                   
parser.add_argument('-s', dest='size', action='store', default=None,
                   help='size requirement that has to be satisfied for a file to be printed (use < and >)')

args = parser.parse_args()
options = vars(args)

def exit_script():
	sys.stderr.write("Exiting...\n")
	exit(1)
	
def to_bytes(size):
	size = size.lower().strip()
	
	if size.endswith("t"):
		return int(size[:-1]) * 1024 * 1024 * 1024 * 1024
	elif size.endswith("g"):
		return int(size[:-1]) * 1024 * 1024 * 1024
	elif size.endswith("m"):
		return int(size[:-1]) * 1024 * 1024
	elif size.endswith("k"):
		return int(size[:-1]) * 1024
	else:
		return int(size)

def from_bytes(size, unit):
	size = int(size)
	unit = unit.lower()
	
	if unit == 't':
		return size * 1.0 / (1024 * 1024 * 1024 * 1024)
	elif unit == 'g':
		return size * 1.0 / (1024 * 1024 * 1024)
	elif unit == 'm':
		return size * 1.0 / (1024 * 1024)
	elif unit == 'k':
		return size * 1.0 / (1024)
	else:
		return size

specifications = {}

if options['size'] is not None:
	# Parse size specification
	for specification in options['size'].split(","):
		if specification[:1] == "<":
			specifications['<'] = specification[1:].strip()
		elif specification[:1] == ">":
			specifications['>'] = specification[1:].strip()
		elif specification[:1] == "=":
			specifications['='] = specification[1:].strip()
		else:
			sys.stderr.write("Incorrect size specification: %s\n" % specification)
			exit_script()

# Select all files matching the given pattern
file_list = options['pattern']

for item in file_list:
	data = os.stat(item)
	filesize = data.st_size
	
	try:
		if filesize >= to_bytes(specifications['<']):
			continue
	except KeyError, e:
		pass
	
	
	try:
		if filesize <= to_bytes(specifications['>']):
			continue
	except KeyError, e:
		pass
	
	
	try:
		if int(from_bytes(filesize, specifications['='][-1:])) != specifications['=']:
			continue
	except KeyError, e:
		pass
	
	# Passed all size tests, let's process it
	with open(os.devnull, 'w') as stfu:
		if item.endswith(".7z"):
			processor = "7zip"
			returncode = subprocess.call(['7z', 'e', '-so', item], stderr=stfu)
		elif item.endswith(".tar"):
			processor = "tar"
			returncode = subprocess.call(['tar', '-Oxf', item], stderr=stfu)
		elif item.endswith(".tar.gz"):
			processor = "tar/gzip"
			returncode = subprocess.call(['tar', '-Oxzf', item], stderr=stfu)
		elif item.endswith(".tar.bz2"):
			processor = "tar/bzip2"
			returncode = subprocess.call(['tar', '-Oxjf', item], stderr=stfu)
		elif item.endswith(".gz"):
			processor = "gzip"
			returncode = subprocess.call(['gzip', '-cd', item], stderr=stfu)
		elif item.endswith(".bz2"):
			processor = "bzip2"
			returncode = subprocess.call(['bzip2', '-cd', item], stderr=stfu)
		elif item.endswith(".zip"):
			processor = "unzip"
			returncode = subprocess.call(['unzip', '-p', item], stderr=stfu)
		else:
			sys.stderr.write("WARNING: Skipping item %s, not a recognized archive type\n" % item)
			continue
	
	if returncode == 0:
		sys.stderr.write("Successfully output %s\n" % item)
	elif returncode == 2:
		sys.stderr.write("ERROR: Could not run the needed command - are you sure you have %s installed?\n" % processor)
	else:
		sys.stderr.write("ERROR: Failed to output %s\n" % item)
