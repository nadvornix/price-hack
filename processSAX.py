
import sys,Queue,leveldb,threading,urllib2,signal,socket
from hashlib import md5
from xml.sax import handler, make_parser,SAXParseException
from httplib import IncompleteRead,BadStatusLine
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()

NUM_THREADS=8

newdb= leveldb.LevelDB('/media/DATATRAVELE/ldbnew',block_cache_size=64*1024*1024,write_buffer_size=512*1024*1024)
olddb= leveldb.LevelDB('/media/DATATRAVELE/ldbold',block_cache_size=64*1024*1024,)

#newdb= leveldb.LevelDB('/media/A77F-2D41/ldbnew',block_cache_size=64*1024*1024,write_buffer_size=512*1024*1024)
#olddb= leveldb.LevelDB('/media/A77F-2D41/ldbold',block_cache_size=64*1024*1024,)

TIMEOUT=60
socket.setdefaulttimeout(TIMEOUT)


def sync():
	newdb.Put("kdesi","cosi",sync=True)
	olddb.Put("kdesi","cosi",sync=True)

# def terminate():
# 	sync()

# 	tmp=True
# 	while tmp:
# 		tmp = queue.get()
# 		tmp = queue.task_done()

# 	sys.exit()

# signal.signal(signal.SIGTERM,terminate)


def p(*s):
	sys.stderr.write(" ".join(map(str,s))+"\n")

class MySaxDocumentHandler(handler.ContentHandler):
	def __init__(self):
		pass

	def startDocument(self):
		self.price=None
		self.url=None

	def endDocument(self):
		sys.stdout.flush()
		# olddb.sync()
		sync()
		pass

	def startElement(self, name, attrs):
		name=name.upper()
		if name=="SHOPITEM":
			self.price=None
			self.url=None
		self.content=""

	def endElement(self, name):
		name=name.upper()
		content=self.content

		if name == 'SHOPITEM':
			if self.price and self.url:
				hashed=md5(self.url).hexdigest()
				try:
					# older = olddb[hashed]
					older = olddb.Get(hashed)
				except KeyError:
					older=None
				# newdb[hashed]=str(self.price)
				newdb.Put(hashed,str(self.price))
				# newdb.sync()
				olderPrice=None
				if older:
					try:
						olderPrice = float(older)
					except ValueError:
						return
				if not olderPrice:
					return
				if self.price/olderPrice < 0.40 and olderPrice>500:	#treshold
					p("%.2f" % (100-(self.price/olderPrice)*100),self.price,olderPrice, self.url)

		elif name=="URL":
			self.url=content
		elif name == "PRICE_VAT":
			try:
				self.price=float(content)
			except ValueError:
				return
		elif name == "PRICE" and not self.price:
			try:
				self.price=float(content)
			except ValueError:
				return

	def characters(self, content):
		self.content += content


class Downloader(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.daemon = True
		self.setDaemon(True)
	
	def run(self):
		while True:

			url = self.queue.get()
			self.proccess_url(url)

			# newdb.sync()
			# send a signal to the queue that the job is done
			self.queue.task_done()

	def proccess_url(self, url):
		""""""
		try:
			if url.startswith("http"):
				data = urllib2.urlopen(url, timeout=TIMEOUT)
			else:
				data = file(url)
			import time
			time.sleep(2)
			handler = MySaxDocumentHandler()
			parser = make_parser()
			parser.setContentHandler(handler)

			parser.parse(data)
		except (SAXParseException, IOError, IncompleteRead,BadStatusLine):
			return

queue = Queue.Queue()

for i in range(NUM_THREADS):
	t = Downloader(queue)
	t.setDaemon(True)
	t.start()

# give the queue some data
for url in sys.stdin.readlines():
	queue.put(url.strip())

# wait for the queue to finish
queue.join()


