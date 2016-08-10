
import sys,Queue,leveldb,threading,urllib2,signal
from hashlib import md5
from xml.sax import handler, make_parser,SAXParseException
from httplib import IncompleteRead,BadStatusLine
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()
from xml.parsers.expat import ExpatError
import xml.etree.cElementTree as etree

NUM_THREADS=32

newdb= leveldb.LevelDB('/media/New Volume/ldbnew',block_cache_size=64*1024*1024,write_buffer_size=64*1024*1024)
olddb= leveldb.LevelDB('ldbold',block_cache_size=64*1024*1024,)

#newdb= leveldb.LevelDB('/media/A77F-2D41/ldbnew',block_cache_size=64*1024*1024,write_buffer_size=512*1024*1024)
#olddb= leveldb.LevelDB('/media/A77F-2D41/ldbold',block_cache_size=64*1024*1024,)


def sync():
	newdb.Put("kdesi","cosi",sync=True)
	olddb.Put("kdesi","cosi",sync=True)

def terminate():
	sync()

	tmp=True
	while tmp:
		tmp = queue.get()
		tmp = queue.task_done()
		print ",",

	sys.exit()

signal.signal(signal.SIGTERM,terminate)

def p(*s):
	sys.stderr.write(" ".join(map(str,s))+"\n")

class Downloader(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:

			url = self.queue.get()
			self.proccess_url(url)

			# newdb.sync()
			# send a signal to the queue that the job is done
			self.queue.task_done()

	def proccess_url(self, url):
		
		print "."

		u = url.strip()
		price=None
		context=None
		data=None
		url=""
		try:
			data = urllib2.urlopen(u, timeout=60)
			context =etree.iterparse(data, events=("start", "end"))
			context = iter(context)
			event, root = context.next()

			for event, elem in context:
				name = elem.tag.upper()
				content = elem.text
				if event=="start":
					if name=="SHOPITEM":
						price=None
						url=None
				elif event=="end":
					if name == 'SHOPITEM':
						# print price,url
						if price and url:
							hashed=md5(url).hexdigest()
							try:
								# older = olddb[hashed]
								older = olddb.Get(hashed)
							except KeyError:
								older=None
							# newdb[hashed]=str(self.price)
							newdb.Put(hashed,str(price))
							# newdb.sync()
							olderPrice=None
							if older:
								try:
									olderPrice = float(older)
								except ValueError:
									elem.clear()
									continue
							if not olderPrice:
								elem.clear()
								continue
							if price/olderPrice < 0.40 and olderPrice>500:	#treshold
								p("%.2f" % (100-(price/olderPrice)*100),price,olderPrice, url)
					elif name=="URL":
						url=content
						elem.clear()
					elif name == "PRICE_VAT":
						try:
							price=float(content)
						except (ValueError,TypeError):
							elem.clear()
							continue

					elif name == "PRICE" and not price:
						try:
							price=float(content)
						except (ValueError,TypeError):
							elem.clear()
							continue
					else:
						elem.clear()

					elem.clear()
			root.clear()
		except (ExpatError, IOError, IncompleteRead,BadStatusLine,SyntaxError):
			pass
		del context
		del data

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


