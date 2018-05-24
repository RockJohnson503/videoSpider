# encoding: utf-8

"""
File: start.py
Author: Rock Johnson
"""
import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

choose = input("1. 爱奇艺全站爬取\n2. 爱奇艺定向爬取\n3. 优酷全站爬取\n4. 优酷定向爬取\n5. 运行单独测试\n请选择(默认5): ")

if choose == "1":
    where = "iqiyi"
elif choose == "2":
    where = "iqiyiDir"
elif choose == "3":
    where = "youku"
elif choose == "4":
    where = "youkuDir"
else:
    execute(["scrapy", "crawl", "alone_test"])
    quit()

i = 1
while True:
    try:
        print("第%s轮爬取开始" % i)
        execute(["scrapy", "crawl", where])
        print("第%s轮爬取结束" % i)
    except Exception as e:
        print("爬取错误")
        print(e)
    i += 1