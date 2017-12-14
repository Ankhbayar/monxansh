# coding:utf-8
"""
    Монгол банкны ханш татагч
    Author: @Ankhbayar
"""
import json
import webapp2
import traceback
from mongolbank import crawler
from mongolbank.models import Xansh
from google.appengine.api import memcache
from google.appengine.ext.webapp import template


# For local catch
local_catch_time = 3600  # 1 hour
catch_key = "xansh_list_no_order"
catch_key_ordered = "xansh_list_order"

class HanshHandler(webapp2.RequestHandler):
    def get(self):
        filter_currency = self.request.get("currency", False)
        myorder = self.request.get("myorder", False)

        self.response.headers["Content-Type"] = "application/json;charset=utf-8"
        # Ref: http://www.w3.org/TR/access-control/
        self.response.headers["Access-Control-Allow-Origin"] = "*"
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

        self.response.out.write(json.dumps(ret_list))


class IndexHandler(webapp2.RequestHandler):
    def post(self):
        return self.get()

    def get(self):
        try:
            self.response.out.write(template.render("templates/index.html", {}, debug=False))
        except:
            self.response.out.write(traceback.format_exc())


class HanshHTMLHandler(webapp2.RequestHandler):
    def get(self):
        filter_currency = self.request.get("currency", False)
        myorder = self.request.get("myorder", False)
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
            "source_link": crawler.CURRENCY_RATE_URL,
            "currency_title": self.request.get("currency_title", u"Валют"),
            "currency_rate_title": self.request.get("currency_rate_title", u"Албан ханш"),
            "source": self.request.get("source", u"Эх сурвалж"),
            "use_conv_tool": self.request.get("conv_tool", False),
        }
        self.response.out.write(template.render("templates/hansh.html", context, debug=False))


class UpdateRateHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain;charset=utf-8"

        try:
            for count, row in enumerate(crawler.get_data(), start=1):
                code = row.get("code")

                # Skip
                if code is None:
                    continue

                Xansh.save_rate(code=code,
                                name=conv_unicode(row.get("name")),
                                rate=row.get("rate"),
                                erembe=count)
                self.response.out.write(u"%d.%s Ханш хадгалав\n" % (count, code))

            self.response.out.write(u"Амжилттай\n")
            # Clear catch
            memcache.delete(catch_key)
            memcache.delete(catch_key_ordered)
            self.response.out.write(u"Cache cleared")
        except:
            self.response.out.write(u"Татаж чадсангүй\n")
            self.response.out.write(traceback.format_exc())


def conv_unicode(var):
    if isinstance(var, str):
        var = unicode(var, "utf-8")
    else:
        var = unicode(var)
    return var


app = webapp2.WSGIApplication([
    ("/", IndexHandler,),
    ("/xansh.json", HanshHandler),
    ("/xansh.html", HanshHTMLHandler),
    ("/update.html", UpdateRateHandler),
], debug=True)
