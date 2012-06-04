#coding:utf-8
"""Монгол банкы ханш татагч
    author : @ankhaatk
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

#from google.appengine.dist import use_library
#use_library('django', '1.3')


import webapp2
from google.appengine.ext.webapp import util
from mongolbank import get_data, CURRENCY_RATE_URL
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db

from xml.dom.minidom import Document

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
            row = { "code": xansh.code, 
                    "name": xansh.name, 
                    "rate": xansh.rate, 
                    "last_date" : xansh.updated.strftime("%Y-%m-%d %H:%M:%S") 
                    }
            big_dic.append(row)
        return big_dic




class BaseRequestHandler(webapp2.RequestHandler):
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


class HanshHandler(webapp2.RequestHandler):
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
        # Thanks. http://stackoverflow.com/questions/477816/the-right-json-content-type
        self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
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
            self.generate("../templates/index.html" )
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
        self.generate("hansh.html", {
            'hansh_list': hansh_list,
            'source_link':source_link,
            'currency_title': self.request.get('currency_title', u"Валют"),
            'currency_rate_title': self.request.get('currency_rate_title', u"Албан ханш"),
            'source': self.request.get('source', u"Эх сурвалж"),
            } )

class UpdateRateHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain;charset=utf-8'
        
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
                    self.response.out.write(u"%d.%s Ханш хадгалав\n" %(count, code) )
            
            
            self.response.out.write(u"Амжилттай\n" )
            # Clear catch
            memcache.delete(catch_key)
            self.response.out.write(u"Cache cleared " )
        except:
            self.response.out.write(u"Татаж чадсангүй\n")
            self.response.out.write(traceback.format_exc())

class Robots(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(u"User-agent: *\n")
        self.response.out.write(u"Allow:/")


class SitemapXML(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(u"""<?xml version="1.0" encoding="UTF-8"?>
   <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
   <url>
      <loc>http://monxansh.appspot.com/</loc>
   </url>
   <url>
      <loc>http://monxansh.appspot.com/xansh.html</loc>
      <changefreq>always</changefreq>
   </url>
   <url>
      <loc>http://monxansh.appspot.com/xansh.json</loc>
      <changefreq>always</changefreq>
   </url>
   <url>
      <loc>http://monxansh.appspot.com/xansh.html?currency=USD|EUR|JPY|GBP|RUB|CNY|KRW</loc>
      <changefreq>always</changefreq>
   </url>
</urlset>
""")

        
def conv_unicode(var):
    if isinstance(var, str):
        var = unicode(var, 'utf-8')
    else:
        var = unicode(var)
    return var


app = webapp2.WSGIApplication([
    ('/', IndexHandler,), 
    ("/xansh.json", HanshHandler),
    ("/xansh.html", HanshHTMLHandler),
    ("/update.html", UpdateRateHandler),
    ("/robots.txt", Robots),
    ("/sitemap.xml", SitemapXML),
    ], debug=True)
