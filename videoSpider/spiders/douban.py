# -*- coding: utf-8 -*-
import scrapy


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['http://movie.douban.com/']

    def parse(self, response):
        urls = "https://movie.douban.com/j/new_search_subjects?sort=R&range=0,10&start=%s"
        start = 0
        while True:
            pass
