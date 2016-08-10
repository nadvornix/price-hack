
import sys,Queue,leveldb,threading,urllib2,signal,socket,time,shutil
from hashlib import md5
from xml.sax import handler, make_parser,SAXParseException
from httplib import IncompleteRead,BadStatusLine
from IPython.Shell import IPShellEmbed
import cPickle as pickle

ipshell = IPShellEmbed()

NUM_THREADS=8
TIMEOUT=5
LDB_PATH= "/media/DATATRAVELE/"

newdb_path=LDB_PATH+'/ldbnew'
olddb_path=LDB_PATH+'/ldbold'

newdb= leveldb.LevelDB(newdb_path,block_cache_size=64*1024*1024,write_buffer_size=512*1024*1024)
olddb= leveldb.LevelDB(olddb_path,block_cache_size=64*1024*1024,)

oldUrlsFile=LDB_PATH+"/oldUrls.pickle"

try:
	oldUrls = pickle.load(file(oldUrlsFile))
except IOError:
	oldUrls=[]

socket.setdefaulttimeout(TIMEOUT)

def sync():
	newdb.Put("kdesi","cosi",sync=True)
	olddb.Put("kdesi","cosi",sync=True)

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
					if self.url not in oldUrls:
						oldUrls.append(self.url)
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


def get_url(q,tid):
	while True:
		url=q.get(block=True)
		try:
			if url.startswith("http"):
				data = urllib2.urlopen(url, timeout=TIMEOUT)
			else:
				data = file(url)

			handler = MySaxDocumentHandler()
			parser = make_parser()
			parser.setContentHandler(handler)

			parser.parse(data)
			
		except (SAXParseException, IOError, IncompleteRead,BadStatusLine):
			pass
#		except:
#			print "E"
		
		q.task_done()

queue = Queue.Queue()

for url in sys.stdin.readlines():
	queue.put(url.strip())

for i in range(10):
    t = threading.Thread(target=get_url, args = (queue,i))
    t.daemon = True
    t.start()

while 1:
	if queue.empty(): 
		break
	time.sleep(0.1)


shutil.rmtree(olddb_path)
shutil.move(newdb_path, olddb_path)

pickle.dump(oldUrls,open(oldUrlsFile,"w"))

