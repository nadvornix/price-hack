

import sys,leveldb,threading,urllib2,signal
from hashlib import md5
from xml.sax import handler, make_parser,SAXParseException
from xml.parsers.expat import ExpatError
from httplib import IncompleteRead,BadStatusLine
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()

# d=[]
# for url in sys.stdin.readlines():
# 	url = url.strip()
# 	print url
# 	try:
# 		data = urllib2.urlopen(url, timeout=60)
# 		d.append(data)
# 	except (SAXParseException, IOError, IncompleteRead,BadStatusLine): 
# 		pass

import xml.etree.ElementTree as etree

# parser = etree.XMLTreeBuilder()

# def end_tag_event(tag):
#     node = parser._end(tag)
#     print node

# parser._parser.EndElementHandler = end_tag_event

# def data_received(data):
#     parser.feed(data)


for url in sys.stdin.readlines():
	u = url.strip()
	price=None
	url=""
	print "1"
	try:
		data = urllib2.urlopen(u, timeout=60)
		print "2"
		context =etree.iterparse(data, events=("start", "end"))
		context = iter(context)
		event, root = context.next()

		# for event, elem in etree.iterparse(data, events=("start", "end")):
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
						# print url, name,price
						# print url
						# hashed=md5(self.url).hexdigest()
						# try:
						# 	# older = olddb[hashed]
						# 	older = olddb.Get(hashed)
						# except KeyError:
						# 	older=None
						# # newdb[hashed]=str(self.price)
						# newdb.Put(hashed,str(self.price))
						# # newdb.sync()
						# olderPrice=None
						# if older:
						# 	try:
						# 		olderPrice = float(older)
						# 	except ValueError:
						# 		return
						# if not olderPrice:
						# 	return
						# if price/olderPrice < 0.40 and olderPrice>500:	#treshold
						# 	p("%.2f" % (100-(price/olderPrice)*100),price,olderPrice, url)
						pass
				elif name=="URL":
					# print dir(elem)
					# print elem.text
					url=content
				elif name == "PRICE_VAT":
					try:
						price=float(content)
					except (ValueError,TypeError):
						continue

				elif name == "PRICE" and not price:
					try:
						price=float(content)
					except (ValueError,TypeError):
						continue
				elem.clear()
		root.clear()

	except (ExpatError, IOError, IncompleteRead,BadStatusLine):
		pass
	#     if elem.tag == "item":
	#         print repr(elem.findtext("link"))
	#         elem.clear() # won't need this again
	# for event, elem in ET.iterparse("blog.rss"):
	#     if elem.tag == "title":
	#         print repr(elem.text)
	#         break # we're done




