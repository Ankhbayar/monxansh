# coding:utf-8
"""
    Монгол банкны ханш татагч
    Author: @Ankhbayar
"""
import os
import json
import webapp2
import traceback
import mongolbank
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template


_DEBUG = False


# For local catch
local_catch_time = 3600  # 1 hour
catch_key = "xansh_list_no_order"
catch_key_ordered = "xansh_list_order"


class Xansh(db.Model):
    """ Xansh Model """
    code = db.StringProperty(verbose_name=u"Код", required=True)
    name = db.StringProperty(verbose_name=u"Нэр")
    # Тооцоолол хийхгүй
    rate = db.StringProperty(verbose_name=u"Ханш", required=True)
    rate_float = db.FloatProperty(verbose_name=u"Ханш")

    # Сүүлд хадгалсан огноо
    updated = db.DateTimeProperty(auto_now=True)

    # Эрэмбэ
    erembe = db.IntegerProperty(verbose_name=u"Эрэмбэ", required=True)

    @staticmethod
    def save_rate(code, name, rate, erembe):
        xansh = Xansh.all().filter("code = ", code).get()
        if xansh is None:
            xansh = Xansh(code=code, rate=rate, erembe=erembe)

        xansh.name = name
        cleaned_rate = rate.replace(",", "").replace(" ", "")
        try:
            xansh.rate_float = float(cleaned_rate)
        except:
            # Алдаа их гардаг
            print traceback.format_exc()
            xansh.rate_float = 0
        xansh.rate = rate
        xansh.erembe = erembe

        xansh.put()
        return

    @staticmethod
    def get_all_to_dic_order():
        big_dic = memcache.get(catch_key_ordered)
        if big_dic is not None:
            return big_dic
        big_dic = []
        for xansh in Xansh.all().order("erembe"):
            row = {
                "code": xansh.code,
                "name": xansh.name,
                "rate": xansh.rate,
                "rate_float": xansh.rate_float,
                "last_date": xansh.updated.strftime("%Y-%m-%d %H:%M:%S")
            }
            big_dic.append(row)
        memcache.add(key=catch_key_ordered, value=big_dic,
                     time=local_catch_time)
        return big_dic

    @staticmethod
    def get_all_to_dic():
        big_dic = memcache.get(catch_key)
        if big_dic is not None:
            return big_dic

        big_dic = {}
        for xansh in Xansh.all().order("erembe"):
            big_dic[xansh.code] = {
                "code": xansh.code,
                "name": xansh.name,
                "rate": xansh.rate,
                "rate_float": xansh.rate_float,
                "last_date": xansh.updated.strftime("%Y-%m-%d %H:%M:%S")
            }
        memcache.add(key=catch_key, value=big_dic, time=local_catch_time)
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
        path = os.path.join(directory,
                            os.path.join("templates", template_name))
        self.response.out.write(template.render(path, values, debug=_DEBUG))


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


class IndexHandler(BaseRequestHandler):
    def post(self):
        return self.get()

    def get(self):
        try:
            self.generate("index.html")
        except:
            self.response.out.write(traceback.format_exc())


class HanshHTMLHandler(BaseRequestHandler):
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

        self.generate("hansh.html", {
            "hansh_list": ret_list,
            "source_link": mongolbank.CURRENCY_RATE_URL,
            "currency_title": self.request.get("currency_title", u"Валют"),
            "currency_rate_title": self.request.get("currency_rate_title", u"Албан ханш"),
            "source": self.request.get("source", u"Эх сурвалж"),
            "use_conv_tool": self.request.get("conv_tool", False),
        })


class UpdateRateHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain;charset=utf-8"

        try:
            for count, row in enumerate(mongolbank.get_data(), start=1):
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
