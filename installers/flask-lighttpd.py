import os, stat, argparse

template_fcgi = '''#!/usr/bin/env python
from flup.server.fcgi import WSGIServer
from app import app
from werkzeug.contrib.fixers import LighttpdCGIRootFix

if __name__ == '__main__':
	WSGIServer(LighttpdCGIRootFix(app)).run()
'''

template_config = '''$HTTP["host"] =~ "%s" {
	server.document-root = "%s"

	fastcgi.server = ("/" =>
		((
			"socket" => "%s",
			"bin-path" => "%s",
			"check-local" => "disable",
			"max-procs" => 1
		))
	)

	alias.url = (
		"/static" => "%s"
	)

	url.rewrite-once = (
		"^(/static($|/.*))$" => "$1"
	)
}
'''

template_app = '''#!/usr/bin/env python
from flask import Flask
app = Flask(__name__)
'''

template_run = '''from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app
app.debug = True

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(1234)
IOLoop.instance().start()
'''

parser = argparse.ArgumentParser(description='Creates and configures a new Flask project for a server running lighttpd.')

parser.add_argument('--name', dest='name', action='store', required=True,
			help='(required) lowercase alphanumeric name of the project')

parser.add_argument('--hostname', dest='hostname', action='store', required=True,
			help='(required) the hostname on which the project should be available')

parser.add_argument('--config', dest='config', action='store', default="/etc/lighttpd/lighttpd.conf",
			help='path to the lighttpd configuration file')

parser.add_argument('--path', dest='path', action='store', default="/var/apps",
			help='path to the apps directory')

args = parser.parse_args()
options = vars(args)

# Figure out the docroot
docroot = "%s/%s" % (options['path'], options['name'])

# The lighttpd configuration file can only include relative paths, so we'll have to figure out how deep we are.
config_depth = len([x for x in options['config'].split("/") if x != ""]) - 1
basepath = "../" * config_depth

# Generate included configuration paths
relative_include = "%s/%s/lighttpd.conf" % (basepath[:-1], docroot[1:])
absolute_include = "%s/lighttpd.conf" % docroot

# Generate path to socket
socket_path = "/tmp/%s-fcgi.sock" % options['name']

# Generate path to main .fcgi file
fcgi_path = "%s/app.fcgi" % docroot

# Generate path to static directory
static_path = "%s/static" % docroot

print "Document root: %s" % docroot
print "Relative include path: %s" % relative_include
print "Absolute include path: %s" % absolute_include
print "Socket path: %s" % socket_path
print "FCGI path: %s" % fcgi_path
print "Static file path: %s" % static_path
print "Hostname: %s" % options['hostname']
raw_input("Press enter to continue...")

print "Creating document root..."
# Create document root
os.makedirs(docroot)

print "Creating static file directory..."
# Create static file directory
os.makedirs(static_path)

print "Creating main .fcgi file..."
# Create main .fcgi file
f = open(fcgi_path, "w")
f.write(template_fcgi)
f.close()

print "Creating configuration include..."
# Create configuration include
f = open(absolute_include, "w")
f.write(template_config % (options['hostname'], docroot, socket_path, fcgi_path, static_path))
f.close()

print "Creating application template..."
f = open("%s/app.py" % docroot, "w")
f.write(template_app)
f.close()

print "Creating run script..."
f = open("%s/run.py" % docroot, "w")
f.write(template_run)
f.close()

print "Setting main .fcgi file as executable..."
os.chmod(fcgi_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)

print "Appending include path to main lighttpd configuration file..."
# Append include to the main lighttpd configuration file
f = open(options['config'], "a")
f.write("\ninclude \"%s\"\n" % relative_include)
f.close()

print "Done!"
