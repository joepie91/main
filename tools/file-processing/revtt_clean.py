#!/usr/bin/python
import sys

lines = open(sys.argv[1]).readlines()

accounts = {}
password_count = 0

for line in lines:
	try:
		username, password = line.split("-")
		
		username = username.strip()[1:-1]
		password = password.strip()[1:-1]
		
		if username not in accounts:
			accounts[username] = [password]
			password_count += 1
		else:
			if password not in accounts[username]:
				accounts[username].append(password)
				password_count += 1
	except ValueError, e:
		pass


for username, passwords in accounts.iteritems():
	for password in passwords:
		print "%s\t\t%s" % (username, password)
	
print "Done, %d accounts with a total of %d passwords." % (len(accounts), password_count)
