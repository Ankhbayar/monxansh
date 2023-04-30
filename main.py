# coding:utf-8
"""
    Монгол банкны ханш татагч
    Author: @Ankhbayar
"""
import traceback

from flask import request
from flask import Flask
from flask import render_template
from flask_cors import CORS, cross_origin
from flask_cachecontrol import cache
from flask_cachecontrol import dont_cache
from google.appengine.api import wrap_wsgi_app
from google.appengine.api import memcache

from mongolbank.models import Xansh
from mongolbank.models import catch_key_ordered
from mongolbank.models import catch_key
from mongolbank.crawler import SOURCE_LINK
from mongolbank.crawler import get_data_old
from mongolbank.crawler import download_from_mongolbank

HTTP_MAX_AGE = 2 * 3600  # 2 цаг

app = Flask(__name__)
app.wsgi_app = wrap_wsgi_app(app.wsgi_app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})



@app.route("/xansh.json",  methods=['GET', 'POST'])
@dont_cache()
@cross_origin()
def xansh_json_handler():
    filter_currency = request.args.get("currency", False)
    myorder = request.args.get("myorder", False)

    ret_list = []

    if filter_currency:
        filter_currency = filter_currency.upper().split("|")

    if filter_currency and myorder:
        hansh_list = Xansh.get_all_to_dic()
        # Хэрэглэгч өөрийнхөө дараалалаар байрлуулах боломж
        for code in filter_currency:
            row = hansh_list.get(code)
            if row:
                ret_list.append(row)
    elif filter_currency:
        hansh_list = Xansh.get_all_to_dic_order()

        for row in hansh_list:
            if row.get("code", False) in filter_currency:
                ret_list.append(row)
    else:
        ret_list = Xansh.get_all_to_dic_order()

    return ret_list

@app.route("/",  methods=['GET', ])
@cache(max_age=HTTP_MAX_AGE, public=True)
def index_handler():
    return render_template("index.html", )

@app.route("/xansh.html",  methods=['GET', "POST" ])
@dont_cache()
@cross_origin()
def xansh_html_handler():
    filter_currency = request.args.get("currency", False)
    myorder = request.args.get("myorder", False)
    ret_list = []

    if filter_currency:
        filter_currency = filter_currency.upper().split("|")

    if filter_currency and myorder:
        hansh_list = Xansh.get_all_to_dic()
        # Хэрэглэгч өөрийнхөө дараалалаар байрлуулах боломж
        for code in filter_currency:
            row = hansh_list.get(code)
            if row:
                ret_list.append(row)
    elif filter_currency:
        hansh_list = Xansh.get_all_to_dic_order()

        for row in hansh_list:
            if row.get("code", False) in filter_currency:
                ret_list.append(row)
    else:
        ret_list = Xansh.get_all_to_dic_order()

    context = {
        "hansh_list": ret_list,
        "source_link": SOURCE_LINK,
        "currency_title": request.args.get("currency_title", "Валют"),
        "currency_rate_title": request.args.get("currency_rate_title", "Албан ханш"),
        "source": request.args.get("source", "Эх сурвалж"),
        "use_conv_tool": request.args.get("conv_tool", False),
    }
    return render_template("hansh.html", **context)

@app.route("/update_old.html", methods=['GET', "POST" ])
@dont_cache()
def update_handler():
    lines = []
    data_lst = get_data_old()
    # app.logger.info("data_lst %s" % data_lst)

    for count, row in enumerate(data_lst, start=1):
        code = row.get("code")

        # Skip
        if code is None:
            continue

        Xansh.save_rate(code=code,
                        name=row.get("name"),
                        rate=row.get("rate"),
                        erembe=count)
        lines.append("%d.%s Ханш хадгалав\n" % (count, code))

    lines.append("Амжилттай\n")
    # Clear catch
    memcache.delete(catch_key)
    memcache.delete(catch_key_ordered)
    lines.append("Cache cleared")
    return lines


@app.route("/update.html", methods=['GET', "POST" ])
@dont_cache()
def update_new_handler():
    lines = []
    datas = download_from_mongolbank()
    for count, row in enumerate(datas, start=0):
        code = row.get("code")

        # Skip
        if code is None:
            continue

        Xansh.save_rate(code=code,
                        name=row.get("name"),
                        rate=row.get("rate"),
                        rate_date=row.get("rate_date"),
                        erembe=count)
        lines.append("%d.%s Ханш хадгалав\n" % (count, code))

    lines.append("Амжилттай\n")
    # Clear catch
    memcache.delete(catch_key)
    memcache.delete(catch_key_ordered)
    lines.append("Cache cleared")

    return lines
