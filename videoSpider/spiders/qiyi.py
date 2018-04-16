# -*- coding: utf-8 -*-
import os
import scrapy
from urllib import parse
from tools.selenium_spider import *
from scrapy.http import Request
from videoSpider.items import *


class QiyiSpider(scrapy.Spider):
    name = 'qiyi'
    allowed_domains = ['iqiyi.com']
    start_urls = ['http://list.iqiyi.com/www/6/----------------iqiyi--.html/']

    def parse(self, response):
        # 对视频列表的解析
        post_nodes = response.css(".wrapper-piclist ul li div.site-piclist_pic a")
        list_type = response.css(
            "div.mod_sear_menu div.mod_sear_list:nth-child(1) ul li.selected a::text").extract_first("")
        for post_node in post_nodes:
            image_url = parse.urljoin(response.url, post_node.css("img::attr(src)").extract_first(""))
            post_url = post_node.css("::attr(href)").extract_first("")
            if list_type == "电视剧":
                callback = self.parse_detail_1
            elif list_type == "电影":
                callback = self.parse_detail_2
            elif list_type == "综艺":
                callback = self.parse_detail_3
            elif list_type == "动漫":
                callback = self.parse_detail_4
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": image_url, "list_type": list_type}, callback=callback)

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
        for album_item in album_items:
            if not album_item.css(".site-piclist_pic > a i.icon-yugao-new"):
                url = album_item.css(".site-piclist_pic > a::attr(href)").extract_first("")
                num = album_item.css(".site-piclist_info .site-piclist_info_title a::text").extract_first("").strip(" ").strip("\n")
                play_urls[num] = url
            else:
                break

        tab_pills = response.css("#widget-tab-3 .selEpisodeTab-wrap ul li").extract()
        if len(tab_pills) > 1:
            for i, k in get_last_tv(response.url, os.path.abspath("tools/phantomjs")):
                play_urls[i] = k

        # 将解析后的数据添加如Item
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", "div.episodeIntro div.episodeIntro-brief[data-moreorless='lessinfo'] span::text")
        item_loader.add_css("video_name", "div.info-intro h1::attr(data-paopao-wallname)")
        item_loader.add_css("spell_name", "div.info-intro h1::attr(data-paopao-wallname)")
        item_loader.add_css("video_addr", ".episodeIntro-area a::text")
        item_loader.add_css("video_type", ".episodeIntro-type a::text")
        item_loader.add_css("video_time", ".episodeIntro-lang[itemprop='datePublished'] a::text")
        item_loader.add_css("video_actor", "div.actorJoin .headImg-wrap[data-moreorless='lessinfo'] li .headImg-bottom a::text")
        item_loader.add_css("video_director", ".episodeIntro-director a::text")
        item_loader.add_css("video_language", ".episodeIntro-lang[itemprop='inLanguage'] a::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))
        item_loader.add_css("video_update_time", ".update-way::text")

        video_item = item_loader.load_item()
        yield video_item


    def parse_detail_2(self, response):
        # 对电影细节的解析
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", response.url)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", ".partDes::attr(data-description)")
        item_loader.add_css("video_name", ".vInfoSide_rTit::text")
        item_loader.add_css("spell_name", ".vInfoSide_rTit::text")
        item_loader.add_css("video_addr", ".vInfoSide_rSpan a[rseat='707181_region']::text")
        item_loader.add_css("video_type", ".vInfoSide_rSpan a[rseat='707181_genres']::text")
        item_loader.add_css("video_actor", ".start_nameTxt::text")
        item_loader.add_css("video_director", ".vInfoSide_rName a::text")
        item_loader.add_css("video_language", ".vInfoSide_rSpan a[rseat='707181_region']::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        yield video_item


    def parse_detail_3(self, response):
        # 对综艺细节的解析
        play_urls = {}
        album_items = response.css("#albumpic-showall-wrap li")
        for album_item in album_items:
            url = album_item.css(".site-piclist_pic > a::attr(href)").extract_first("")
            num = album_item.css(".mod-listTitle_right::text").extract_first("")
            play_urls[num] = url

        tab_pills = response.css("#album_pic_paging[style='display:none;']")
        if len(tab_pills) == 0:
            for i, k in get_last_variety(response.url, os.path.abspath("tools/phantomjs")):
                play_urls[i] = k

        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", ".episodeIntro-brief[data-moreorless='lessinfo'] .briefIntroTxt::text")
        item_loader.add_css("video_name", "h1[itemprop='name'] .info-intro-title::text")
        item_loader.add_css("spell_name", "h1[itemprop='name'] .info-intro-title::text")
        item_loader.add_css("video_addr", ".episodeIntro-area a::text")
        item_loader.add_css("video_type", ".episodeIntro-type a::text")
        item_loader.add_css("video_time", ".episodeIntro-lang[itemprop='datePublished'] a::text")
        item_loader.add_css("video_language", ".episodeIntro-lang[itemprop='inLanguage'] a::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))
        item_loader.add_css("video_update_time", ".episodeIntro-update span::text")

        video_item = item_loader.load_item()
        yield video_item


    def parse_detail_4(self, response):
        # 对动漫细节的解析
        pass