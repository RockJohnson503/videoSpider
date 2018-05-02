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
    start_urls = ['http://list.iqiyi.com/www/2/----------------iqiyi--.html/']
    url_nums = ["2", "1", "6", "4"]

    def parse(self, response):
        # 对视频列表的解析
        post_nodes = response.css(".wrapper-piclist ul li")
        list_type = response.css(
            "div.mod_sear_menu div.mod_sear_list:nth-child(1) ul li.selected a::text").extract_first("")
        for post_node in post_nodes:
            image_url = parse.urljoin(response.url, post_node.css(".site-piclist_pic a img::attr(src)").extract_first(""))
            post_url = post_node.css(".site-piclist_pic a::attr(href)").extract_first("")
            video_name = post_node.css(".site-piclist_info .site-piclist_info_title a::text").extract_first("")
            video_actor = post_node.css(".site-piclist_info .role_info em a::text").extract()
            if list_type == "电视剧":
                callback = self.parse_detail_1
            elif list_type == "电影":
                callback = self.parse_detail_2
            elif list_type == "综艺":
                callback = self.parse_detail_3
            else:
                callback = self.parse_detail_4
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": image_url,
                                "list_type": list_type,
                                "video_name": video_name,
                                "video_actor": video_actor}, callback=callback)

        # 提取下一页的路径
        next_url = response.css("div.mod-page .a1[data-key='down']::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
        else:
            i = response.url[response.url.index("www/") + 4:response.url.index("/-")]
            try:
                num = self.url_nums[self.url_nums.index(i) + 1]
            except:
                num = self.url_nums[0]
            yield Request(url="http://list.iqiyi.com/www/" + str(num) + "/----------------iqiyi--.html/", callback=self.parse)


    def parse_detail_1(self, response):
        # 对电视剧细节的解析
        # 处理电视剧的分页问题
        play_urls = {}
        album_items = response.css(".albumSubTab-wrap .piclist-wrapper ul li")
        for album_item in album_items:
            if not album_item.css(".site-piclist_pic > a i.icon-yugao-new"):
                url = album_item.css(".site-piclist_pic > a::attr(href)").extract_first("")
                num = album_item.css(".site-piclist_info .site-piclist_info_title a::text")\
                    .extract_first("")\
                    .strip()\
                    .strip("\n")\
                    .strip("\r")
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
        item_loader.add_value("video_name", response.meta.get("video_name", ""))
        item_loader.add_value("spell_name", response.meta.get("video_name", ""))
        item_loader.add_css("video_addr", ".episodeIntro-area a::text")
        item_loader.add_css("video_type", ".episodeIntro-type a::text")
        item_loader.add_css("video_time", ".episodeIntro-lang[itemprop='datePublished'] a::text")
        item_loader.add_value("video_actor", response.meta.get("video_actor", ""))
        item_loader.add_css("video_director", ".episodeIntro-director a::text")
        item_loader.add_css("video_language", ".episodeIntro-lang[itemprop='inLanguage'] a::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        if len(video_item) > 3:
            yield video_item


    def parse_detail_2(self, response):
        # 对电影细节的解析
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", response.url)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", ".partDes::attr(data-description)")
        item_loader.add_value("video_name", response.meta.get("video_name", ""))
        item_loader.add_value("spell_name", response.meta.get("video_name", ""))
        item_loader.add_css("video_addr", ".vInfoSide_rSpan a[rseat='707181_region']::text")
        item_loader.add_css("video_type", ".vInfoSide_rSpan a[rseat='707181_genres']::text")
        item_loader.add_value("video_actor", response.meta.get("video_actor", ""))
        item_loader.add_css("video_director", ".vInfoSide_rName a::text")
        item_loader.add_css("video_language", ".vInfoSide_rSpan a[rseat='707181_region']::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        yield video_item


    def parse_detail_3(self, response):
        # 对综艺细节的解析
        # 处理综艺的分页问题
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
        item_loader.add_value("video_name", response.meta.get("video_name", ""))
        item_loader.add_value("spell_name", response.meta.get("video_name", ""))
        item_loader.add_css("video_addr", ".episodeIntro-area a::text")
        item_loader.add_css("video_type", ".episodeIntro-type a::text")
        item_loader.add_css("video_time", ".episodeIntro-lang[itemprop='datePublished'] a::text")
        item_loader.add_css("video_language", ".episodeIntro-lang[itemprop='inLanguage'] a::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        if len(video_item) > 3:
            yield video_item


    def parse_detail_4(self, response):
        # 对动漫细节的解析
        # 处理动漫的分页问题
        play_urls = {}
        album_items = response.css(".wrapper-piclist ul li")
        for album_item in album_items:
            url = album_item.css(".site-piclist_pic > a::attr(href)").extract_first("")
            num = album_item.css(".site-piclist_info .site-piclist_info_title a::text")\
                .extract_first("")\
                .strip()\
                .strip("\n")\
                .strip("\r")
            play_urls[num] = url

        tab_pills = response.css("#block-H .mod-album_tab_num a").extract()
        if len(tab_pills) > 1:
            for i, k in get_last_anime(response.url, os.path.abspath("tools/phantomjs")):
                play_urls[i] = k

        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", "*[data-moreorless='lessinfo'][itemprop='description'] span:not(.c-999)::text")
        item_loader.add_value("video_name", response.meta.get("video_name", ""))
        item_loader.add_value("spell_name", response.meta.get("video_name", ""))
        item_loader.add_css("video_addr", "*[itemprop='contentLocation'] a::text")
        item_loader.add_css("video_type", "*[itemprop='genre'] a::text")
        item_loader.add_css("video_time", ".main_title span::text")
        item_loader.add_css("video_language", "*[itemprop='inLanguage'] a::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        if len(video_item) > 3:
            yield video_item