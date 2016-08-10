
import sys,Queue,leveldb,threading,urllib2,signal,socket
from hashlib import md5
from xml.sax import handler, make_parser,SAXParseException
from httplib import IncompleteRead,BadStatusLine
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()

NUM_THREADS=8
TIMEOUT = 60

socket.setdefaulttimeout(TIMEOUT)
import time,random

def randsleep(a,b):
	r=random.randint(a,b)
	print "sleep for", r 
	time.sleep(r)

def sync():
	pass

def p(*s):
	sys.stderr.write(" ".join(map(str,s))+"\n")


class Downloader(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.daemon = True
	
	def run(self):
		while True:

			i = self.queue.get(block=True)
			self.proccess_url(i)

			# send a signal to the queue that the job is done
			self.queue.task_done()

	def proccess_url(self, url):
		try:
			# if url.startswith("http"):
			# 	data = urllib2.urlopen(url, timeout=TIMEOUT)
			# else:
			# 	data = file(url)
			# while True:
			# 	d=data.read(10000)
			# 	if d==None:
			# 		break
			time.sleep(0.1)
			print ".",
			
			# handler = MySaxDocumentHandler()
			# parser = make_parser()
			# parser.setContentHandler(handler)

			# parser.parse(data)
		except (SAXParseException, IOError, IncompleteRead,BadStatusLine):
			return

queue = Queue.Queue()

for i in range(NUM_THREADS):
	t = Downloader(queue)

	t.daemon = True
	t.start()
time.sleep(10)
# give the queue some data
for url in sys.stdin.readlines():
	queue.put(url.strip())
#time.sleep(10)
# wait for the queue to finish
queue.join()

# while threading.active_count() > 0:
#     time.sleep(1)
#     print threading.active_count(),"<<<"

