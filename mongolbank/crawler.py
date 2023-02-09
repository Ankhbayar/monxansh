# coding: utf-8
"""
    Монгол банкны ханш татагч
    Author : @Ankhbayar
"""

import re

CURRENCY_RATE_URL = "https://old.mongolbank.mn/dblistofficialdailyrate.aspx"
# Thanks. @ubs121
REGX_PATTERN = u"<tr>\\s*<td.*>.*</td>\\s*<td.*>(?P<name>.*)</td>\\s*<td.*><span id=\"ContentPlaceHolder1_lbl(?P<code>\\w{3})\">(?P<rate>.*)</span></td></tr>"


def open_url_data(url):
    from google.appengine.api import urlfetch
    result = urlfetch.fetch(CURRENCY_RATE_URL, deadline=30, headers={
        "Cache-Control": "no-cache,max-age=0",
        "Pragma": "no-cache"
    })
    return result.content


def get_data():
    html_data = open_url_data(CURRENCY_RATE_URL)
    html_text = html_data.decode("utf-8")

    if html_text is not None:
        pattern = re.compile(REGX_PATTERN)
        return [r.groupdict() for r in pattern.finditer(html_text)]
    else:
        return "error mb connect error"
