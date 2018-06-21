# -*- coding: utf-8 -*-
import os, scrapy, re
from urllib import parse
from scrapy.http import Request
from videoSpider.items import *
from tools.selenium_spider import *
from tools.common import episode_format, error_video
from videoSpider.middlewares import SpiderStateMiddleware


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
                                    "video_name": video_name},
                              callback=self.href_details,
                              priority=9)

        # 提取下一页
        next_url = response.css(".yk-pager .next a::attr(href)").extract_first("")
        if len(next_url) != 0:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def href_details(self, response):
        # 跳转到细节页面
        body = response.text
        po = body.find("tvinfo")
        if po > 0:
            body = body[po:po + 250]
            res = re.match('tvinfo.*href="(.*?)".*title="%s".*' % response.meta.get("video_name", ""), body, re.S)
            if res:
                yield Request(url=parse.urljoin("http://list.youku.com/", res.group(1)),
                              meta={"front_image_url": response.meta.get("front_image_url", ""),
                                    "list_type": response.meta.get("list_type", ""),
                                    "play_url": response.url,
                                    "video_name": response.meta.get("video_name", "")},
                              callback=self.parse_details,
                              priority=10)
                SpiderStateMiddleware.crawling += 1

    def parse_details(self, response):
        # 对视频细节的解析
        v_name = response.meta.get("video_name", "")
        print("正在爬取: %s" % v_name)
        play_urls = {}
        list_type = response.meta.get("list_type", "")
        iterable = None

        # 处理分页问题
        if list_type == "电视剧":
            iterable = get_youku_tv(response.url, os.path.abspath("tools/chromedriver"))
        elif list_type == "电影":
            play_urls = response.meta.get("play_url", "")
        elif list_type == "综艺":
            iterable = get_youku_variety(response.url, os.path.abspath("tools/chromedriver"))
        else:
            edi = response.css(".edition::text").extract_first("")
            if edi != "剧场版":
                iterable = get_youku_anime(response.url, os.path.abspath("tools/chromedriver"))
            else:
                play_urls = response.meta.get("play_url", "")
        iterable = iterable if iterable else range(0)
        for i, k in iterable:
            play_urls[episode_format(i)] = k.replace(k[k.find(".html?s") + 5:], "")

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
        item_loader.add_value("list_type", list_type)
        item_loader.add_css("video_des", ".p-intro .text::text")
        item_loader.add_value("video_name", v_name)
        item_loader.add_value("spell_name", v_name)
        item_loader.add_value("video_addr", addr)
        item_loader.add_value("video_type", v_type)
        item_loader.add_css("video_time", ".p-title span::text")
        item_loader.add_value("video_actor", v_actor)
        item_loader.add_value("video_origin", "优酷")
        item_loader.add_value("video_director", v_director)
        item_loader.add_value("video_language", addr)
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        reason = None
        if play_urls == {}:
            reason = "没有播放路径"
        elif len(video_item.values()) < 6:
            reason = "抓取的字段不足"
        else:
            yield video_item
        if reason:
            error_video(list_type,
                        response.url,
                        reason,
                        v_name)
        print("爬取完毕: %s" % v_name)
        SpiderStateMiddleware.crawled += 1