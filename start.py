# encoding: utf-8

"""
File: start.py
Author: Rock Johnson
"""
from datetime import datetime
from scrapy.cmdline import execute

choose = input("1. 爱奇艺全站爬取\n2. 优酷全站爬取\n3. 爱奇艺定向爬取 \n4. 优酷定向爬取\n5. 腾讯定向爬取\n6. 运行单独测试\n请选择(默认6): ")

apd = None
if choose == "1":
    where = "iqiyi"
    apd = ["-s", "CONCURRENT_REQUESTS=250"]
elif choose == "2":
    where = "youku"
    apd = ["-s", "CONCURRENT_REQUESTS=250"]
elif choose == "3":
    where = "iqiyiDir"
elif choose == "4":
    where = "youkuDir"
elif choose == "5":
    where = "tenceDir"
else:
    execute(["scrapy", "crawl", "alone_test", "-s", "LOG_STDOUT=False"])

try:
    time = str(datetime.now().replace(microsecond=0)).replace(" ", "_")
    cmd = ["scrapy", "crawl", where, "-s", "LOG_FILE=logs/%s_%s.log" % (where, time)]
    if apd:
        cmd += apd
    execute(cmd)
except Exception as e:
    print("爬取错误")
    print(e)