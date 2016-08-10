
import urllib2

url="http://dl.dropboxusercontent.com/u/3195612/kindleslovnik/k.zip"
print 1
req = urllib2.Request(url)
sock = urllib2.urlopen(req)
print 2
l=0
from time import sleep
for i in range(1000):
	data=sock.read(1000)
	sleep(1)
	l+=len(data)
print l