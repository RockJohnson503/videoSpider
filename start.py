# encoding: utf-8

"""
File: start.py
Author: Rock Johnson
"""
import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "qiyi"])