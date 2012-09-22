import socket, argparse, sys, time, re
from collections import deque
from threading import Thread

dnsbls = open("dnsbl.txt").readlines()

socket.setdefaulttimeout(0.5)

total_checking = 0

class CheckThread(Thread):
	def __init__(self, username, ip):
		Thread.__init__(self)
		self.username = username
		self.ip = ip
		
	def run(self):
		global total_checking
		reversed_ip = ".".join(self.ip.split(".")[::-1])
		
		for dnsbl in dnsbls:
			dnsbl = dnsbl.strip()
			
			try:
				socket.gethostbyname(reversed_ip + "." + dnsbl)
				
				# This is bad.
				#sock.send("MODE #bottest +b *@%s\r\n" % self.ip)
				#sock.send("KICK #bottest %s :User %s is blacklisted in %s!\r\n" % (self.username, self.username, dnsbl))
				#sock.send("PRIVMSG #bottest :User %s is blacklisted in %s!\r\n" % (self.username, dnsbl))
				#sock.send("PRIVMSG #bottest :User %s is blacklisted in %s!\r\n" % (self.username, dnsbl))
				sock.send("KILL %s :User %s is blacklisted in %s!\r\n" % (self.username, self.username, dnsbl))
				print "IP %s is blacklisted in %s!" % (self.ip, dnsbl)
				total_checking -= 1
				return False
			except:
				# This is good.
				print "No blacklist matches found for %s" % self.ip
				pass
		
		sock.send("PRIVMSG #bottest :User %s is clean.\r\n" % self.username)
		total_checking -= 1
		return True

def run_tocheck():
	if total_checking <= 20 and len(to_check) > 0:
		nickname = to_check.popleft()
		ip = users[nickname]
		t = CheckThread(nickname, ip)
		t.start()

def split_irc(message):
	message = re.sub("(?<=[0-9A-Fa-fI]):(?=[0-9A-Fa-fI])", "[..]", message)
	
	if ":" in message:
		first, second = message.split(":", 1)
		return first.rstrip().split(" ") + [second]
	else:
		return message.split(" ")

parser = argparse.ArgumentParser(description='Connects to an IRC network and scans for proxies.')

parser.add_argument('-H', dest='hostname', action='store', required=True,
                   help='server to connect to')
                   
parser.add_argument('-o', dest='port', action='store', required=True,
                   help='port* to connect to')

parser.add_argument('-u', dest='username', action='store', required=True,
                   help='oper username')
                   
parser.add_argument('-p', dest='password', action='store', required=True,
                   help='oper password')

args = parser.parse_args()
options = vars(args)

to_check = deque([])
users = {}

print "Connecting...",

sock = socket.socket()
sock.settimeout(None)
sock.connect((options['hostname'], int(options['port'])))
readbuffer = ""

print "connected"

sock.send("NICK botkill\r\n")
sock.send("USER botkill %s 0 :ipcheck.py\r\n" % options['hostname'])

print "Registered."

while True:
	readbuffer = readbuffer + sock.recv(1024)
	lines = readbuffer.split("\n")
	readbuffer = lines.pop()
	
	for line in lines:
		run_tocheck()
		
		if line.startswith(":"):
			origin, line = line.split(" ", 1)
			
		line = line.rstrip()
		parts = split_irc(line)
		
		if parts[0] == "PING":
			sock.send("PONG %s\r\n" % parts[1])
			print "Completed connection challenge."
		elif parts[0] == "001":
			sock.send("OPER %s %s\r\n" % (options['username'], options['password']))
		elif parts[0] == "381":
			print "Authenticated as oper."
			sock.send("JOIN #bottest\r\n")
		elif parts[0] == "JOIN":
			if parts[1].lower() == "#bottest":
				username = origin[1:].split("!")[0]
				print username + " joined"
				sock.send("USERIP %s\r\n" % username)
		elif parts[0] == "340":
			try:
				data = parts[2].split("=", 1)
				nickname = data[0]
				
				if nickname.endswith("*"):
					nickname = nickname[:-1]
				
				ip = data[1].split("@", 1)[1]
				users[nickname] = ip
				to_check.append(nickname)
				run_tocheck()
				print "User %s has IP %s" % (nickname, ip)
			except:
				pass
		elif parts[0] == "491":
			print "Invalid oper credentials given."
			exit(1)

	time.sleep(0.005)
