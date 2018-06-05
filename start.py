# encoding: utf-8

"""
File: start.py
Author: Rock Johnson
"""
from datetime import datetime
from scrapy.cmdline import execute

choose = input("1. 爱奇艺全站爬取\n2. 优酷全站爬取\n3. 爱奇艺定向爬取 \n4. 优酷定向爬取\n5. 运行单独测试\n请选择(默认5): ")

if choose == "1":
    where = "iqiyi"
elif choose == "2":
    where = "youku"
elif choose == "3":
    where = "iqiyiDir"
elif choose == "4":
    where = "youkuDir"
else:
    execute(["scrapy", "crawl", "alone_test", "-s", "LOG_STDOUT=False"])

try:
    execute(["scrapy", "crawl", where, "-s", "LOG_FILE=logs/%s_%s.log" % (where, datetime.now())])
except Exception as e:
    print("爬取错误")
    print(e)