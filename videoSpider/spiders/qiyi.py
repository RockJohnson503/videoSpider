# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from tools.selenium_spider import get_last
from scrapy.http import Request
from videoSpider.items import *


class QiyiSpider(scrapy.Spider):
    name = 'qiyi'
    allowed_domains = ['list.iqiyi.com/www/2/----------------iqiyi--.html', 'iqiyi.com']
    start_urls = ['http://list.iqiyi.com/www/2/----------------iqiyi--.html/']

    def parse(self, response):
        # 对视频列表的解析
        post_nodes = response.css(".wrapper-piclist ul li div.site-piclist_pic a")
        list_type = response.css(
            "div.mod_sear_menu div.mod_sear_list:nth-child(1) ul li.selected a::text").extract_first("")
        for post_node in post_nodes:
            image_url = parse.urljoin(response.url, post_node.css("img::attr(src)").extract_first(""))
            post_url = post_node.css("::attr(href)").extract_first("")
            if list_type == "电视剧":
                yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url, "list_type": list_type}, callback=self.parse_detail_1)
            elif list_type == "电影":
                pass
            elif list_type == "综艺":
                pass
            elif list_type == "动漫":
                pass

        # 提取下一页的路径
        next_url = response.css("div.mod-page a.a1::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
        else:
            pass

    def parse_detail_1(self, response):
        # 对电视剧细节的解析
        # 处理电视剧的路径
        play_urls = {}
        album_items = response.css(".albumSubTab-wrap .piclist-wrapper ul li")
        tab_pills = response.css(".albumTabPills:nth-child(1) li")
        for album_item in album_items:
            if not album_item.css(".site-piclist_pic > a i.icon-yugao-new"):
                url = album_item.css(".site-piclist_pic > a::attr(href)").extract_first("")
                num = album_item.css(".site-piclist_info .site-piclist_info_title a::text").extract_first("").strip(" ").strip("\n")
                play_urls[num] = url

        if len(tab_pills) > 1:
            for i in get_last(response.url, len(tab_pills)):
                play_urls[i[0]] = i[1]

        # 将解析后的数据添加如Item
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)
        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", [response.meta.get("list_type", "")])
        item_loader.add_css("video_des", "div.episodeIntro div.episodeIntro-brief[data-moreorless='moreinfo'] span::text")
        item_loader.add_css("video_name", "div.info-intro h1::attr(data-paopao-wallname)")
        item_loader.add_css("spell_name", "div.info-intro h1::attr(data-paopao-wallname)")
        item_loader.add_css("video_addr", ".episodeIntro-area a::text")
        item_loader.add_css("video_type", ".episodeIntro-type a::text")
        item_loader.add_css("video_time", ".episodeIntro-lang[itemprop='datePublished'] a::text")
        item_loader.add_css("video_actor", "div.actorJoin .headImg-wrap[data-moreorless='lessinfo'] li .headImg-bottom a::text")
        item_loader.add_css("video_director", ".episodeIntro-director a::text")
        item_loader.add_css("video_language", ".episodeIntro-lang[itemprop='inLanguage'] a::text")
        item_loader.add_value("front_image_url", [response.meta.get("front_image_url", "")])
        item_loader.add_css("video_update_time", ".update-way::text")

        video_item = item_loader.load_item()
        yield video_item