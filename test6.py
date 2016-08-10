
# November 2013: just make it work

# Plan:
# use hdd: is it really that bad?
# use something more reliable and memory efficient than ldb
#	pouzit lepsi db pro oldurls, tohle zabira hodne pameti
# 	zjistit jestli to fakt zabira hodne pameti
# oldurlfile: pickle->dbm

import sys,Queue,leveldb,threading,urllib2,signal,socket,time,shutil
from hashlib import md5
from xml.sax import handler, make_parser,SAXParseException
from httplib import IncompleteRead,BadStatusLine
from IPython.Shell import IPShellEmbed
import cPickle as pickle

import anydbm

ipshell = IPShellEmbed()

NUM_THREADS=8
TIMEOUT=5

LDB_PATH= "."

newdb_path=LDB_PATH+'/ldbnew'
olddb_path=LDB_PATH+'/ldbold'

newdb = anydbm.open(newdb_path, 'c')
olddb = anydbm.open(olddb_path, 'c')
# newdb= leveldb.LevelDB(newdb_path,block_cache_size=64*1024*1024,write_buffer_size=512*1024*1024)
# olddb= leveldb.LevelDB(olddb_path,block_cache_size=64*1024*1024,)

old_urls_path=LDB_PATH+"/oldUrls"
old_urls=anydbm.open(old_urls_path, "c")

socket.setdefaulttimeout(TIMEOUT)

def sync():
	newdb.sync()
	# olddb.sync()
	# newdb.Put("kdesi","cosi",sync=True)
	# olddb.Put("kdesi","cosi",sync=True)

def p(*s):
	sys.stderr.write(" ".join(map(str,s))+"\n")

counter = 0

class MySaxDocumentHandler(handler.ContentHandler):
	def __init__(self):
		pass

	def startDocument(self):
		self.price=None
		self.url=None

	def endDocument(self):
		sys.stdout.flush()
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
				global counter
				global olddb
				global newdb

				counter+=1
				try:
					older = olddb[hashed]
					# older = olddb.Get(hashed)
				except KeyError:
					older=None

				newdb[hashed]=str(self.price)
				# newdb.Put(hashed,str(self.price))
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
					#print (old_urls.get(hashed))
					#if self.url not in old_urls:
					old_urls[hashed] = self.url
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

queue.join()

print (counter)
shutil.move(newdb_path, olddb_path)
