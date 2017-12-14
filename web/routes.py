# coding:utf-8
from handlers import IndexHandler
from handlers import HanshHandler
from handlers import HanshHTMLHandler
from handlers import UpdateRateHandler

_routes = [
    ("/", IndexHandler,),
    ("/xansh.json", HanshHandler),
    ("/xansh.html", HanshHTMLHandler),
    ("/update.html", UpdateRateHandler),
]

def get_routes():
    return _routes