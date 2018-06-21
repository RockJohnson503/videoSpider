# encoding: utf-8

"""
File: plan.py
Author: Rock Johnson
"""
from tools.inc_server import inc
from threading import Timer
import os, datetime


def plan_run(where):
    loctime = str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_")
    os.system("scrapy crawl %s -s LOG_FILE=logs/%s_%s.log" % (where, where, loctime))
    t = Timer(10, plan_run, [where])
    t.start()
    inc()


if __name__ == '__main__':
    choose = input("1. 爱奇艺爬取计划\n2. 优酷爬取计划\n3. 腾讯爬取计划\n请选择(默认3): ")
    if choose == "1":
        where = "iqiyiDir"
    elif choose == "2":
        where = "youkuDir"
    else:
        where = "tenceDir"
    plan_run(where)