# coding:utf-8

import traceback
from google.appengine.api import memcache
from google.appengine.ext import db


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