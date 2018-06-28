# encoding: utf-8

"""
File: plan.py
Author: Rock Johnson
"""
from threading import Timer
import os, datetime

i = 1
num = 0

def plan_run(where):
    global i

    loctime = str(datetime.datetime.now().replace(microsecond=0)).replace(" ", "_")
    os.system("scrapy crawl %s -s LOG_FILE=logs/%s_%s.log" % (where, where, loctime))

    if num == 0:
        t = Timer(10, plan_run, [where])
        t.start()
    if i < num:
        i += 1
        t = Timer(10, plan_run, [where])
        t.start()


if __name__ == '__main__':
    choose = input("1. 爱奇艺爬取计划\n2. 优酷爬取计划\n3. 腾讯爬取计划\n请选择(默认3): ")
    if choose == "1":
        where = "iqiyiDir"
    elif choose == "2":
        where = "youkuDir"
    else:
        where = "tenceDir"
    num = int(input("爬取几次(0表示无限): "))
    plan_run(where)