#coding:utf-8
"""Монгол банкы ханш татагч
	author : @ankhaatk
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from mongolbank import get_data, CURRENCY_RATE_URL
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db

import simplejson as json
import traceback
import os
_DEBUG = False

# For local catch
local_catch_time = 60 # 1 цаг
catch_key = "xansh_list"


class Xansh(db.Model):
	"""Xansh Model
	"""
	code = db.StringProperty(verbose_name = u"Код",required=True)
	name = db.StringProperty(verbose_name = u"Нэр")
	# Тооцоолол хийхгүй
	rate = db.StringProperty(verbose_name = u"Ханш",required=True)
	
	# Сүүлд хадгалсан огноо
	updated = db.DateTimeProperty(auto_now=True)
	
	# Эрэмбэ
	erembe = db.IntegerProperty(verbose_name = u"Эрэмбэ",required=True)
	
	@staticmethod
	def save_rate(code, name, rate, erembe):
		
		xansh = Xansh.all().filter('code = ', code).get()
		if xansh is None:
			xansh = Xansh(code = code, rate = rate, erembe = erembe)
		
		xansh.name = name
		xansh.rate = rate
		xansh.erembe = erembe
		
		xansh.put()
		return 
		
	@staticmethod	
	def get_all_to_dic():
		big_dic = []
		for xansh in Xansh.all().order("erembe"):
			row = {"code": xansh.code, "name": xansh.name, "rate": xansh.rate, "last_date" : xansh.updated.strftime("%Y-%m-%d %H:%M:%S") }
			big_dic.append(row)
		return big_dic




class BaseRequestHandler(webapp.RequestHandler):
	"""Supplies a common template generation function.

	When you call generate(), we augment the template variables supplied with
	the current user in the 'user' variable and the current webapp request
	in the 'request' variable.
	"""
	def generate(self, template_name, template_values={}):
		values = {}
		values.update(template_values)
		directory = os.path.dirname(__file__)
		path = os.path.join(directory, os.path.join('templates', template_name))
		self.response.out.write(template.render(path, values, debug=_DEBUG))


class HanshHandler(webapp.RequestHandler):
	def get(self):
		try:
			
			hansh_list = memcache.get(catch_key)
			if hansh_list is None:
				hansh_list = Xansh.get_all_to_dic()
				memcache.add(catch_key, hansh_list,  local_catch_time )
		except:
			self.response.out.write(traceback.format_exc())
			hansh_list = []
		filter_currency = self.request.get('currency', False)
		if filter_currency:
			tmp_list = []
			filter_currency = filter_currency.split("|")
			for row in hansh_list:
				if row.get("code", False) in filter_currency:
					tmp_list.append(row)
			hansh_list = tmp_list
	
		self.response.out.write(json.dumps(hansh_list))

class IndexHandler(BaseRequestHandler):
	def post(self):
		return self.get()
	def get(self):
		try:
			self.generate("index.html" )
		except:
			self.response.out.write(traceback.format_exc())

class HanshHTMLHandler(BaseRequestHandler):
	def get(self):
		try:
			hansh_list = memcache.get(catch_key)
			if hansh_list is None:
				hansh_list = Xansh.get_all_to_dic()
				memcache.add(catch_key, hansh_list,  local_catch_time )
		except:
			hansh_list = []
		
		filter_currency = self.request.get('currency', False)
		if filter_currency:
			tmp_list = []
			filter_currency = filter_currency.split("|")
			for row in hansh_list:
				if row.get("code", False) in filter_currency:
					tmp_list.append(row)
			hansh_list = tmp_list
		source_link = CURRENCY_RATE_URL
		self.generate("hansh.html", locals() )

class UpdateRateHandler(webapp.RequestHandler):
	def get(self):
		try:
			count = 0
			hansh_list = get_data()
			for row in hansh_list:
				count += 1
				code = row.get("code")
				if code is not None:
					Xansh.save_rate(code = code, 
									name = conv_unicode(row.get("name") ), 
									rate = row.get("rate"), 
									erembe = count)
					self.response.out.write(u"%d.%s Ханш хадгалав<br/>" %(count, code) )
			
			
			self.response.out.write(u"Амжилттай<br/>" )
			# Clear catch
			memcache.delete(catch_key)
			self.response.out.write(u"Cach cleared " )
		except:
			self.response.out.write(u"Татаж чадсангүй<br/>")
			self.response.out.write(traceback.format_exc())


def conv_unicode(var):
	if isinstance(var, str):
		var = unicode(var, 'utf-8')
	else:
		var = unicode(var)
	return var

def main():
	application = webapp.WSGIApplication([
		('/', IndexHandler,), 
		("/xansh.json", HanshHandler),
		("/xansh.html", HanshHTMLHandler),
		("/update.html", UpdateRateHandler),
		], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
