# -*- coding: utf-8 -*-
import os, scrapy
from urllib import parse
from scrapy.http import Request
from videoSpider.items import *
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class YoukuSpider(CrawlSpider):
    name = 'youku'
    allowed_domains = ['youku.com']
    start_urls = ['http://list.youku.com/category/show/c_97.html']

    # 爬取规则,只对电影 电视剧 综艺 动漫进行跟进,
    # 状态和付费栏的路径直接忽略.
    rules = (
        Rule(LinkExtractor(allow=(r'list.youku.com/category/show/c_97.*',
                                  r'list.youku.com/category/show/c_96.*',
                                  r'list.youku.com/category/show/c_85.*',
                                  r'list.youku.com/category/show/c_100.*'),
                           deny=(r'list.youku.com/category/show/c_\d+_s_\d+_d_\d+_u\d+.*',
                                 r'list.youku.com/category/show/c_\d+_u_\d+_s_\d+_d_\d+.*',
                                 r'list.youku.com/category/show/c_\d+_s_\d+_d_\d+_pt_\d+.*',
                                 r'list.youku.com/category/show/c_\d+_pt_\d+_s_\d+_d_\d+.*'))
             , callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        # 对视频列表的解析
        post_nodes = response.css("li.yk-col4")
        list_type = response.css("#filterPanel div:nth-child(1) li.current span::text").extract_first("")
        for post_node in post_nodes:
            image_url = parse.urljoin(response.url, post_node.css(".p-thumb img::attr(src)").extract_first(""))
            post_url = post_node.css(".p-thumb a::attr(href)").extract_first("")
            video_name = post_node.css(".info-list .title a::text").extract_first("")
            video_actor = post_node.css(".info-list .actor a::text").extract()
            if list_type == "剧集":
                list_type = "电视剧"
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": image_url,
                                "list_type": list_type,
                                "video_name": video_name,
                                "video_actor": video_actor,
                                "video_origin": "优酷"}, callback=self.href_details)

    def href_details(self, response):
        # 跳转到细节页面
        list_type = response.meta.get("list_type", "")
        post_url = response.css(".tvinfo h2 a::attr(href)").extract_first("")
        if list_type == "电视剧":
            callback = self.parse_detail_1
        elif list_type == "电影":
            callback = self.parse_detail_2
        elif list_type == "综艺":
            callback = self.parse_detail_3
        else:
            callback = self.parse_detail_4
        yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": response.meta.get("front_image_url", ""),
                                "list_type": list_type,
                                "video_name": response.meta.get("video_name", ""),
                                "video_actor": response.meta.get("video_actor", ""),
                                "video_origin": "优酷"},
                          callback=callback)

    def parse_detail_1(self, response):
        # 对电视剧细节的解析
        # 处理电视剧的分页问题
        play_urls = {}
        for i, k in get_youku_tv(response.url, os.path.abspath("tools/phantomjs")):
            play_urls[i] = k

        # 将解析后的数据添加如Item
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", ".p-intro .text::text")
        item_loader.add_value("video_name", response.meta.get("video_name", ""))
        item_loader.add_value("spell_name", response.meta.get("video_name", ""))
        item_loader.add_css("video_addr", ".p-base > ul li::text")
        item_loader.add_css("video_type", ".p-base > ul li::text")
        item_loader.add_css("video_time", ".p-title span::text")
        item_loader.add_value("video_actor", response.meta.get("video_actor", ""))
        item_loader.add_value("video_origin", response.meta.get("video_origin", ""))
        item_loader.add_css("video_director", ".p-base > ul li::text")
        item_loader.add_css("video_language", ".p-base > ul li::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        if len(video_item) > 3:
            yield video_item