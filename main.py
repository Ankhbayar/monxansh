# coding:utf-8
"""
    Монгол банкны ханш татагч
    Author: @Ankhbayar
"""
import webapp2
from web import routes

app = webapp2.WSGIApplication(routes.get_routes(), debug=True)