
"""
test timeoutu

"""

import sys,Queue,leveldb,threading,urllib2,signal,socket
from hashlib import md5
from xml.sax import handler, make_parser,SAXParseException
from httplib import IncompleteRead,BadStatusLine
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()




TIMEOUT=5
socket.setdefaulttimeout(TIMEOUT)

for i,url in enumerate(sys.stdin.readlines()):
	url=url.strip()
	try:
		uf = urllib2.urlopen(url, timeout=TIMEOUT)
		a=uf.read(1000)
		print i, len(a)
	except:
		print "E"

