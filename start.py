# encoding: utf-8

"""
File: start.py
Author: Rock Johnson
"""
import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
i = 1
# while True:
#     try:
#         execute(["scrapy", "crawl", "qiyi"])
#     except Exception as e:
#         print("爬取错误")
while True:
    try:
        print("第%s轮爬取开始" % i)
        execute(["scrapy", "crawl", "youku"])
        print("第%s轮爬取结束" % i)
    except:
        print("爬取错误")
    i += 1
# execute(["scrapy", "crawl", "alone_test"])