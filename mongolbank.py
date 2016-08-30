# coding: utf-8
"""
    Монгол банкны ханш татагч
    Author : @Ankhbayar
"""
import re
from google.appengine.api import urlfetch


CURRENCY_RATE_URL = "http://www.mongolbank.mn/dblistofficialdailyrate.aspx"

def get_data():
    r = urlfetch.fetch("http://www.mongolbank.mn/dblistofficialdailyrate.aspx")

    assert r.status_code == 200

    regex = re.compile(u"<tr>\\s*<td.*>.*</td>\\s*<td.*>(?P<name>.*)</td>\\s*<td.*>"
                       u"<span id=\"ContentPlaceHolder1_lbl(?P<code>\\w{3})\">"
                       u"(?P<rate>.*)</span></td></tr>")

    return [r.groupdict() for r in regex.finditer(r.content)]
