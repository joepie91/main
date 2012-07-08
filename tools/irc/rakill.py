import socket, argparse, sys, time, re

def split_irc(message):
	message = re.sub("(?<=[0-9A-FI]):(?=[0-9A-FI])", "[..]", message)
	
	if ":" in message:
		first, second = message.split(":", 1)
		return first.rstrip().split(" ") + [second]
	else:
		return message.split(" ")

parser = argparse.ArgumentParser(description='Connects to an IRC network and executes a rakill.')

parser.add_argument('-H', dest='hostname', action='store', required=True,
                   help='server to connect to')
                   
parser.add_argument('-o', dest='port', action='store', required=True,
                   help='port* to connect to')

parser.add_argument('-u', dest='username', action='store', required=True,
                   help='oper username')
                   
parser.add_argument('-p', dest='password', action='store', required=True,
                   help='oper password')
                   
parser.add_argument('-r', dest='regex', action='store', required=True,
                   help='regex to match')
                   
parser.add_argument('-d', dest='duration', action='store', default="30d",
                   help='gline duration')
                   
parser.add_argument('-m', dest='message', action='store', default="You were banned during an automated bot kill. If this is in error, contact an operator.",
                   help='gline/kill message')


parser.add_argument('--list', dest='action_list', action='store_true',
                   help='list all matching users')

parser.add_argument('--gline', dest='action_gline', action='store_true',
                   help='gline all matching users')
                   
parser.add_argument('--kill', dest='action_kill', action='store_true',
                   help='kill all matching users')

args = parser.parse_args()
options = vars(args)

print "Connecting...",

sock = socket.socket()
sock.connect((options['hostname'], int(options['port'])))
readbuffer = ""

print "connected"

sock.send("NICK botkill\r\n")
sock.send("USER botkill %s 0 :rakill.py\r\n" % options['hostname'])

print "Registered."

while True:
	readbuffer = readbuffer + sock.recv(1024)
	lines = readbuffer.split("\n")
	readbuffer = lines.pop()
	
	for line in lines:
		if line.startswith(":"):
			line = line.split(" ", 1)[1]
			
		line = line.rstrip()
		parts = split_irc(line)
		
		if parts[0] == "PING":
			sock.send("PONG %s\r\n" % parts[1])
			print "Completed connection challenge."
		elif parts[0] == "001":
			sock.send("OPER %s %s\r\n" % (options['username'], options['password']))
		elif parts[0] == "381":
			print "Authenticated as oper."
			sock.send("WHO ** h\r\n")
			print "Requested userlist."
		elif parts[0] == "352":
			ident = parts[3]
			host = parts[4].replace("[..]", ":")
			leaf = parts[5]
			nick = parts[6]
			realname = parts[8][3:]
			
			if re.match(options['regex'], nick):
				if options['action_gline']:
					sock.send("GLINE *@%s %s :[%s] %s\r\n" % (host, options['duration'], nick, options['message']))
					print "Glined *@%s" % host
				if options['action_kill']:
					sock.send("KILL %s :%s\r\n" % (nick, options['message']))
					print "Killed %s" % nick
				if options['action_list']:
					print "Matched user: %s!%s@%s" % (nick, ident, host)
		elif parts[0] == "315":
			print "All users checked, exiting..."
			sock.send("QUIT :rakill.py bot killer\r\n")
			time.sleep(1)
			exit(0)
		elif parts[0] == "491":
			print "Invalid oper credentials given."
			exit(1)

	time.sleep(0.005)
