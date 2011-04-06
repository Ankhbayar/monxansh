#coding:utf-8
"""Монгол банкы ханш татагч
	author : @ankhaatk
"""

__author__ = 'L.Ankhbayar'


from sgmllib import SGMLParser
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

CURRENCY_RATE_URL = "http://www.mongolbank.mn/web/guest/137"

class MB_FX_TableParser(SGMLParser):
	datas = None
	current_row = None
	def reset(self):
		SGMLParser.reset(self)
		self.datas = []
		self.current_row = []
	def start_tr(self, attrs):
		self.current_row  = []
		self.datas.append(self.current_row)
	def handle_data(self, text):
		self.current_row.append(text)


def get_data():

	result = urlfetch.fetch(CURRENCY_RATE_URL )
	html_text = result.content
	# result.close()

	if result.status_code == 200:
		# Аштайхан болгох
		fx_table_start = html_text.index("""<div id="tab_style">""") - 20
		fx_table_end = html_text.index("""</div>""", fx_table_start)
		fx_table = html_text[fx_table_start:fx_table_end]
		#print "fx_table", fx_table
		parser = MB_FX_TableParser()
		
		parser.reset()
		parser.feed(fx_table)
		parser.close()

		return parser.datas
	else:
		return "error mb connect error"

	
