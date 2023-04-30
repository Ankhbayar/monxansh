# coding: utf-8
"""
    Монгол банкны ханш татагч
    Author : @Ankhbayar
"""

import re
import datetime
import json
from google.appengine.api import urlfetch

CURRENCY_RATE_URL_OLD = "https://old.mongolbank.mn/dblistofficialdailyrate.aspx"
CURRENCY_RATE_URL = "https://www.mongolbank.mn/mn/currency-rate/data"
SOURCE_LINK = "https://www.mongolbank.mn/mn/currency-rate"

# Thanks. @ubs121
REGX_PATTERN = u"<tr>\\s*<td.*>.*</td>\\s*<td.*>(?P<name>.*)</td>\\s*<td.*><span id=\"ContentPlaceHolder1_lbl(?P<code>\\w{3})\">(?P<rate>.*)</span></td></tr>"


def get_data_old():
    result = urlfetch.fetch(CURRENCY_RATE_URL_OLD, deadline=30, method="GET", headers={
        "Cache-Control": "no-cache,max-age=0",
        "Pragma": "no-cache"
    })
    if result.status_code == 200:
        html_text = result.content.decode("utf-8")
    else:
        html_text = None

    if html_text is None:
        return "error mb connect error"
    pattern = re.compile(REGX_PATTERN)
    return [r.groupdict() for r in pattern.finditer(html_text)]


def download_from_mongolbank():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    # https://www.mongolbank.mn/mn/currency-rate/data?startDate=2022-04-30&endDate=2023-04-30
    result = urlfetch.fetch("{url}?startDate={today}&endDate={today}".format(url=CURRENCY_RATE_URL, today=today_str), deadline=30, method="POST")
    resp_code = result.status_code 
    if resp_code == 200:
        resp_content = result.content.decode("utf-8")
    else:
        resp_content = None
    if resp_content is None:
        return "error mb connect error %s" % resp_code
    data = json.loads(resp_content)
    rate_history_data = data.get("data", [])
    currencyNames = data.get("langData", {}).get("currencyNames", {})
    prep_data = []
    for h_data in rate_history_data:
        ognoo = h_data.pop("RATE_DATE", "")
        if today_str == ognoo:
            for key, value in h_data.items():
                c_data = currencyNames.get(key, {})
                prep_data.append({
                    "name": c_data.get("name", key),
                    "code": key,
                    "rate": value,
                    "rate_date": ognoo,
                })
    return prep_data
    # code
    # name
    # rate