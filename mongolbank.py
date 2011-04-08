#coding:utf-8
"""Монгол банкы ханш татагч
	author : @ankhaatk
"""

__author__ = 'L.Ankhbayar'


from sgmllib import SGMLParser

CURRENCY_RATE_URL = "http://www.mongolbank.mn/listexchange.aspx?did=2"

class MB_FX_TableParser(SGMLParser):
	datas = None
	current_row = None
	def reset(self):
		SGMLParser.reset(self)
		self.datas = []
		self.current_row = {}
		self.start_fx_ul = False
		self.dic_key = None
	def start_ul(self, attrs):
		if len(attrs) == 0:
			self.start_fx_ul = True
	def start_li(self, attrs):
		if self.start_fx_ul:
			# New UL
			self.current_row = {}
			self.dic_key = None
			self.datas.append(self.current_row)
	
	def start_span(self, attrs):
		if self.start_fx_ul:
			if attrs:
				# TODO: Fix hard code
				code = attrs[0][1][-3:]
				self.current_row['code'] = code
			self.dic_key = "rate"
	
	def handle_starttag(self, tag, method, attrs):
		if tag == "ul" and self.start_fx_ul == False:
			method(attrs)
		elif tag in ["li","td", "span"] and self.start_fx_ul is True:
			method(attrs)
		else:
			self.dic_key = None
	def start_td(self, attrs):
		if self.start_fx_ul and attrs == [('align', 'left')] :
			self.dic_key = "name"
	
	def handle_data(self, text):
		if self.start_fx_ul and self.dic_key is not None:
			self.current_row[self.dic_key] = text
			self.dic_key = None

def open_url_data(url):
	from google.appengine.api import urlfetch
	#result = urlfetch.fetch(CURRENCY_RATE_URL, deadline = 30 )
	result = urlfetch.fetch(CURRENCY_RATE_URL)
	return result.content
	
	
def get_data():
	
	
	html_text = open_url_data(CURRENCY_RATE_URL)
	
	if html_text is not None:
		parser = MB_FX_TableParser()
		
		parser.reset()
		parser.feed(html_text)
		parser.close()

		return parser.datas
	else:
		return "error mb connect error"

