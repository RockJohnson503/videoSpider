# -*- coding: utf-8 -*-
import os, scrapy
from urllib import parse
from tools.common import *
from scrapy.http import Request
from videoSpider.items import *
from tools.selenium_spider import *
from videoSpider.middlewares import SpiderStateMiddleware


class IqiyidirSpider(scrapy.Spider):
    name = 'iqiyiDir'
    allowed_domains = ['iqiyi.com']
    start_urls = ['http://list.iqiyi.com/www/4/----------------iqiyi--.html',
                  'http://list.iqiyi.com/www/2/----------------iqiyi--.html',
                  'http://list.iqiyi.com/www/1/----------------iqiyi--.html',
                  'http://list.iqiyi.com/www/6/----------------iqiyi--.html']

    def parse(self, response):
        # 对视频列表的解析
        post_nodes = response.css(".wrapper-piclist ul li")
        list_type = response.css(
            "div.mod_sear_menu div.mod_sear_list:nth-child(1) ul li.selected a::text").extract_first("")
        for post_node in post_nodes:
            image_url = parse.urljoin(response.url,
                                      post_node.css(".site-piclist_pic a img::attr(src)").extract_first(""))
            post_url = post_node.css(".site-piclist_pic a::attr(href)").extract_first("")
            video_name = post_node.css(".site-piclist_info .site-piclist_info_title a::text").extract_first("")
            video_actor = post_node.css(".site-piclist_info .role_info em a::text").extract()
            if 'so.iqiyi.com' in post_url or 'src=search' in post_url:
                continue
            if list_type == "电视剧":
                callback = self.parse_detail_1
            elif list_type == "电影":
                if not is_player(post_url):
                    continue
                callback = self.parse_detail_2
            elif list_type == "综艺":
                callback = self.parse_detail_3
            else:
                callback = self.parse_detail_4

            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": image_url,
                                "list_type": list_type,
                                "video_name": video_name,
                                "video_actor": video_actor},
                          callback=callback,
                          priority=10)
            SpiderStateMiddleware.crawling += 1

        # 提取下一页
        next_url = response.css(".mod-page a[data-key='down']::attr(href)").extract_first("")
        if len(next_url) != 0:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail_1(self, response):
        # 对电视剧细节的解析
        v_name = response.meta.get("video_name", "")
        print("正在爬取: %s" % v_name)
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        play_urls = {}
        album_items = response.css(".albumSubTab-wrap .piclist-wrapper ul li")
        des = "div.episodeIntro div.episodeIntro-brief[data-moreorless='lessinfo'] span::text"
        if len(album_items) == 0:
            # 针对架构不一样的电视剧
            album_items = response.css(".wrapper-piclist ul li")
            des = "div[data-moreorless='lessinfo'] .bigPic-b-jtxt::text"

        for album_item in album_items:
            if not album_item.css(".site-piclist_pic > a i.icon-yugao-new"):
                url = album_item.css(".site-piclist_pic > a::attr(href)").extract_first("")
                num = album_item.css(".site-piclist_info .site-piclist_info_title a::text") \
                    .extract_first("") \
                    .strip() \
                    .strip("\n") \
                    .strip("\r")
                play_urls[episode_format(num)] = url
            else:
                break

        tab_pills = response.css("#widget-tab-3 .selEpisodeTab-wrap ul li").extract()
        if len(tab_pills) == 0:
            tab_pills = response.css("#block-H .mod_album_lists > div:nth-child(1) .mod-album_tab_num a").extract()

        if len(tab_pills) > 1:
            # 处理分页问题
            for i, k in get_last_tv(response.url, os.path.abspath("tools/chromedriver")):
                play_urls[episode_format(i)] = k

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", des)
        item_loader.add_value("video_name", v_name)
        item_loader.add_value("spell_name", v_name)
        item_loader.add_css("video_addr", ".episodeIntro-area a::text")
        item_loader.add_css("video_type", ".episodeIntro-type a::text")
        item_loader.add_css("video_time", ".episodeIntro-lang[itemprop='datePublished'] a::text")
        item_loader.add_value("video_actor", response.meta.get("video_actor", ""))
        item_loader.add_value("video_origin", "爱奇艺")
        item_loader.add_css("video_director", ".episodeIntro-director a::text")
        item_loader.add_css("video_language", ".episodeIntro-lang[itemprop='inLanguage'] a::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        reason = None
        if play_urls == {}:
            reason = "没有播放路径"
        elif len(video_item) < 7:
            reason = "抓取的字段不足"
        else:
            yield video_item
        if reason:
            error_video(response.meta.get("list_type", ""),
                        response.url,
                        reason,
                        v_name)
        print("爬取完毕: %s" % v_name)
        SpiderStateMiddleware.crawled += 1


    def parse_detail_2(self, response):
        # 对电影细节的解析
        v_name = response.meta.get("video_name", "")
        print("正在爬取: %s" % v_name)
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", response.url)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", ".partDes::attr(data-description)")
        item_loader.add_value("video_name", v_name)
        item_loader.add_value("spell_name", v_name)
        item_loader.add_css("video_addr", ".vInfoSide_rSpan a[rseat='707181_region']::text")
        item_loader.add_css("video_type", ".vInfoSide_rSpan a[rseat='707181_genres']::text")
        item_loader.add_value("video_actor", response.meta.get("video_actor", ""))
        item_loader.add_value("video_origin", "爱奇艺")
        item_loader.add_css("video_director", ".vInfoSide_rName a::text")
        item_loader.add_css("video_language", ".vInfoSide_rSpan a[rseat='707181_region']::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        yield video_item
        print("爬取完毕: %s" % v_name)
        SpiderStateMiddleware.crawled += 1


    def parse_detail_3(self, response):
        # 对综艺细节的解析
        v_name = response.meta.get("video_name", "")
        print("正在爬取: %s" % v_name)
        play_urls = {}
        album_items = response.css("#albumpic-showall-wrap li")
        for album_item in album_items:
            url = album_item.css(".site-piclist_pic > a::attr(href)").extract_first("")
            num = album_item.css(".mod-listTitle_right::text").extract_first("")
            play_urls[episode_format(num)] = url

        tab_pills = response.css("#album_pic_paging[style='']")
        if len(tab_pills) > 0:
            # 处理分页问题
            for i, k in get_last_variety(response.url, os.path.abspath("tools/chromedriver")):
                play_urls[episode_format(i)] = k
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_css("video_des", ".episodeIntro-brief[data-moreorless='lessinfo'] .briefIntroTxt::text")
        item_loader.add_value("video_name", v_name)
        item_loader.add_value("spell_name", v_name)
        item_loader.add_css("video_addr", ".episodeIntro-area a::text")
        item_loader.add_css("video_type", ".episodeIntro-type a::text")
        item_loader.add_value("video_origin", "爱奇艺")
        item_loader.add_css("video_time", ".episodeIntro-lang[itemprop='datePublished'] a::text")
        item_loader.add_css("video_language", ".episodeIntro-lang[itemprop='inLanguage'] a::text")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        reason = None
        if play_urls == {}:
            reason = "没有播放路径"
        elif len(video_item) < 6:
            reason = "抓取的字段不足"
        else:
            yield video_item
        if reason:
            error_video(response.meta.get("list_type", ""),
                        response.url,
                        reason,
                        v_name)
        print("爬取完毕: %s" % v_name)
        SpiderStateMiddleware.crawled += 1

    def parse_detail_4(self, response):
        # 对动漫细节的解析
        v_name = response.meta.get("video_name", "")
        print("正在爬取: %s" % response.meta.get("video_name", ""))
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)
        play_urls = {}
        if not is_player(response.url):
            album_items = response.css(".piclist-wrapper[data-tab-body='widget-tab-3'] ul.site-piclist li")
            for album_item in album_items:
                if not album_item.css(".site-piclist_pic > a i.icon-yugao-new"):
                    url = album_item.css(".site-piclist_pic > a::attr(href)").extract_first("")
                    num = album_item.css(".site-piclist_info .site-piclist_info_title a::text") \
                        .extract_first("") \
                        .strip() \
                        .strip("\n") \
                        .strip("\r")
                    play_urls[episode_format(num)] = url
                else:
                    break

            tab_pills = response.css(".subTab-sel .selEpisodeTab-wrap .albumTabPills li").extract()
            if len(tab_pills) > 1:
                # 处理分页问题
                for i, k in get_last_anime(response.url, os.path.abspath("tools/chromedriver")):
                    play_urls[episode_format(i)] = k

            item_loader.add_css("video_des",
                                "*[data-moreorless='lessinfo'][itemprop='description'] span:not(.c-999)::text")
            item_loader.add_css("video_addr", "*[itemprop='contentLocation'] a::text")
            item_loader.add_css("video_type", "*[itemprop='genre'] a::text")
            item_loader.add_css("video_time", ".main_title span::text")
            item_loader.add_css("video_language", "*[itemprop='inLanguage'] a::text")
        else:
            play_urls = response.url
            item_loader.add_css("video_des", "#datainfo-tag-desc::text")
            item_loader.add_css("video_addr", "#thirdPartyTagList::text")
            item_loader.add_css("video_language", "#thirdPartyTagList::text")

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", response.meta.get("list_type", ""))
        item_loader.add_value("video_name", v_name)
        item_loader.add_value("spell_name", v_name)
        item_loader.add_value("video_origin", "爱奇艺")
        item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

        video_item = item_loader.load_item()
        reason = None
        if play_urls == {}:
            reason = "没有播放路径"
        elif len(video_item) < 6:
            reason = "抓取的字段不足"
        else:
            yield video_item
        if reason:
            error_video(response.meta.get("list_type", ""),
                        response.url,
                        reason,
                        v_name)
        print("爬取完毕: %s" % v_name)
        SpiderStateMiddleware.crawled += 1