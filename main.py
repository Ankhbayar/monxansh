#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from mongolbank import get_data, CURRENCY_RATE_URL
from google.appengine.ext.webapp import template
import simplejson as json
import traceback
import os
_DEBUG = False
class HanshHandler(webapp.RequestHandler):
	def get(self):
		try:
			hansh_list  = get_data()
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
	
		self.response.out.write(json.dumps(hansh_list))
	
		self.response.out.write(traceback.format_exc())
		#self.response.out.write('Hello world!')

		#
		
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
			hansh_list  = get_data()
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

def main():
	application = webapp.WSGIApplication([
		('/', IndexHandler,), 
		("/xansh.json", HanshHandler),
		("/xansh.html", HanshHTMLHandler),
		], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
