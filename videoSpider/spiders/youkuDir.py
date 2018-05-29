# -*- coding: utf-8 -*-
import os, scrapy, re
from urllib import parse
from scrapy.http import Request
from videoSpider.items import *
from tools.selenium_spider import *
from tools.common import episode_format, error_video


class YoukudirSpider(scrapy.Spider):
    name = 'youkuDir'
    allowed_domains = ['youku.com']
    start_urls = ['http://list.youku.com/category/show/c_100.html',
                  'http://list.youku.com/category/show/c_97.html',
                  'http://list.youku.com/category/show/c_96.html',
                  'http://list.youku.com/category/show/c_85.html']

    def parse(self, response):
        # 对视频列表的解析
        post_nodes = response.css("li.yk-col4")
        list_type = response.css("#filterPanel div:nth-child(1) li.current span::text").extract_first("")
        for post_node in post_nodes:
            image_url = parse.urljoin(response.url, post_node.css(".p-thumb img::attr(src)").extract_first(""))
            post_url = post_node.css(".p-thumb a::attr(href)").extract_first("")
            video_name = post_node.css(".info-list .title a::text").extract_first("")
            if list_type == "剧集":
                list_type = "电视剧"
            v_state = post_node.css(".p-time span::text").extract_first("")
            if v_state != "预告" and v_state != "资料":
                yield Request(url=parse.urljoin("http://v.youku.com/", post_url),
                              meta={"front_image_url": image_url,
                                    "list_type": list_type,
                                    "video_name": video_name}, callback=self.href_details)

        # 提取下一页
        next_url = response.css(".yk-pager .next a::attr(href)").extract_first("")
        if len(next_url) != 0:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def href_details(self, response):
        # 跳转到细节页面
        list_type = response.meta.get("list_type", "")
        play_url = response.url
        body = response.text
        if 'tvinfo' in body:
            po = body.index("tvinfo")
            body = body[po:]
            res = re.match('.*tvinfo.*href=\\\\"(.*?)\\\\" target.*', body)
            if res:
                yield Request(url=parse.urljoin("http://list.youku.com/", res.group(1)),
                              meta={"front_image_url": response.meta.get("front_image_url", ""),
                                    "list_type": list_type,
                                    "play_url": play_url,
                                    "video_name": response.meta.get("video_name", "")},
                              callback=self.parse_details)

    def parse_details(self, response):
        # 对电视剧细节的解析
        # 处理电视剧的分页问题
        print("正在爬取: %s" % response.meta.get("video_name", ""))
        play_urls = {}
        list_type = response.meta.get("list_type", "")
        iterable = None
        if list_type == "电视剧":
            iterable = get_youku_tv(response.url, os.path.abspath("tools/phantomjs"))
        elif list_type == "电影":
            play_urls = response.meta.get("play_url", "")
        elif list_type == "综艺":
            iterable = get_youku_variety(response.url, os.path.abspath("tools/phantomjs"))
        else:
            edi = response.css(".p-title .edition").extract_first("")
            if edi != "剧场版":
                iterable = get_youku_anime(response.url, os.path.abspath("tools/phantomjs"))
            else:
                play_urls = response.meta.get("play_url", "")
        iterable = iterable if iterable else range(0)
        for i, k in iterable:
            play_urls[episode_format(i)] = k.replace(k[k.index(".html?s") + 5:], "")

        all_infos = response.css(".p-base > ul li")
        addr = v_type = v_actor = v_director = None
        for info in all_infos:
            info = info.css("::text").extract()
            if "地区：" in info:
                addr = info[1]
            if "类型：" in info:
                v_type = info[1::2]
            if "主演：" in info:
                v_actor = info[1::2]
            if "导演：" in info:
                v_director = info[1]

        # 将解析后的数据添加如Item
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", ".p-intro .text::text")
        item_loader.add_value("video_name", response.meta.get("video_name", ""))
        item_loader.add_value("spell_name", response.meta.get("video_name", ""))
        item_loader.add_value("video_addr", addr)
        item_loader.add_value("video_type", v_type)
        item_loader.add_css("video_time", ".p-title span::text")
        item_loader.add_value("video_actor", v_actor)
        item_loader.add_value("video_origin", "优酷")
        item_loader.add_value("video_director", v_director)
        item_loader.add_value("video_language", addr)
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        if len(video_item) < 6 or play_urls == {}:
            error_video(response.meta.get("list_type", ""),
                        response.url,
                        response.meta.get("video_name", ""))
        else:
            yield video_item
        print("爬取完毕: %s" % response.meta.get("video_name", ""))