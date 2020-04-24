# -*- coding: utf-8 -*-
import scrapy, json
from urllib import parse
from scrapy.http import Request
from videoSpider.items import *
from tools.common import episode_format, error_video, request_url
from videoSpider.middlewares import SpiderStateMiddleware


class TencedirSpider(scrapy.Spider):
    name = 'tenceDir'
    allowed_domains = ['v.qq.com']
    start_urls = ['http://v.qq.com/x/list/movie',
                  'http://v.qq.com/x/list/tv',
                  'http://v.qq.com/x/list/cartoon',
                  'http://v.qq.com/x/list/variety']

    def parse(self, response):
        # 对视频列表的解析
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)
        item_loader.add_css('list_type', '.filter_list a.current::text')
        list_type = item_loader.get_collected_values('list_type')[0]
        post_nodes = response.css("li.list_item")

        for post_node in post_nodes:
            item_loader.add_css('video_name', '.figure_title a::text')
            if list_type == "电影" or list_type == "电视剧":
                item_loader.add_css('video_actor', '.figure_desc a::text')

            v_state = post_node.css(".figure .mark_v img::attr(alt)").get("")
            image_url = parse.urljoin(response.url, post_node.css(".figure img::attr(r-lazyload)").get(""))
            if "预告" not in v_state and image_url != response.url:
                item_loader.add_value('front_image_url', image_url)
                post_url = post_node.css(".figure::attr(href)").get("")

                yield response.follow(post_url, meta={'item_loader': item_loader}, callback=self.parse_director, priority=9)

        # 提取下一页
        next_url = response.css(".mod_pages .page_next::attr(href)").get("")
        if next_url != "javascript:;":
            yield response.follow(next_url, callback=self.parse)

    def parse_director(self, response):
        # 解析导演
        item_loader = response.meta.get('item_loader')
        item_loader.add_value('play_url', response.url)
        if item_loader.get_collected_values('list_type')[0] == "综艺":
            item_loader.add_css('video_type', '.video_tags a[href*="search"]::text')
        else:
            item_loader.add_css('video_director', '.director a::text')
            item_loader.add_css('video_time', '.video_tags a[href*="year"]::text')
            if item_loader.get_collected_values('video_time') == []:
                item_loader.add_css('video_time', '.video_tags span::text')

        item_loader.add_css('video_addr', '.video_tags a::text')
        detail_url = response.css(".player_title a::attr(href)").get("")
        
        yield response.follow(detail_url,
                              meta={'item_loader': item_loader},
                              callback=self.parse_details,
                              priority=10)
        SpiderStateMiddleware.crawling += 1

    def parse_details(self, response):
        # 对视频细节的解析
        item_loader = response.meta.get('item_loader')
        v_name = item_loader.get_collected_values('video_name')[0]
        print("正在爬取: %s" % v_name)
        list_type = item_loader.get_collected_values('list_type')[0]
        if item_loader.get_collected_values('video_type') == []:
            item_loader.add_css('video_type', '.video_tag .tag_list a::text')
        # 获取id
        rurl = response.url
        v_id = rurl[rurl.rfind("/") + 1:rurl.find(".html")]

        # 解析视频语言字段
        lang = None
        for type in  response.css(".type_item"):
            if type.css(".type_tit::text").get("") == "语　言:":
                lang = type.css(".type_txt::text").get("")
            if list_type == "综艺" and type.css(".type_tit::text").get("") == "首播时间:":
                v_time = type.css(".type_txt::text").get("")
                v_time = v_time[:v_time.find("-")]
                item_loader.add_value('video_time', v_time)

        # 处理分页问题
        if list_type != "电影":
            item_loader.add_value('play_url', self.parse_episode(response, v_id))

        item_loader.add_value('v_id', v_id)
        item_loader.add_css("video_des", ".video_desc .desc_txt span::text")
        item_loader.add_value("spell_name", v_name)
        item_loader.add_value("video_origin", "腾讯")
        item_loader.add_value("video_language", lang)

        video_item = item_loader.load_item()
        reason = None
        if not video_item.get('play_url'):
            reason = "没有播放路径"
        elif len(video_item.values()) < 6:
            reason = "抓取的字段不足"
        elif not video_item.get("v_id"):
            reason = "抓取id失败"
        else:
            yield video_item
        if reason:
            error_video(list_type,
                        response.url,
                        reason,
                        v_name)
        print("爬取完毕: %s" % v_name)
        SpiderStateMiddleware.crawled += 1

    def parse_episode(self, response, v_id):
        #　解析播放路径
        play_urls = {}

        detail_url = "https://s.video.qq.com/get_playsource?id=%s&plat=2&type=4&data_type=%s&video_type=%s&range=%s&plname=qq&otype=json&num_mod_cnt=20"

        # 获取类型
        type = response.css(".video_title_cn .type::text").get("")
        d_type = 2
        if type == "电视剧":
            v_type = 2
        elif type == "动漫":
            v_type = 3
        else:
            v_type = 10
            d_type = 3

        res = request_url(detail_url % (v_id, d_type, v_type, "1-9999"))
        text = res.text[res.text.find("=") + 1: -1]
        all_json = json.loads(text)
        try:
            plists = all_json["PlaylistItem"]["videoPlayList"]
        except:
            return response.css(".btn_primary::attr(href)").get("")
        prev = 0
        for plist in plists:
            flag = True
            if plist["markLabelList"] != []:
                if "预告" in plist["markLabelList"][0]["primeText"]:
                    flag = False

            if flag:
                en = plist["episode_number"]
                url = plist["playUrl"]
                if type != "综艺":
                    if int(en) <= prev:
                        en = prev = prev + 1
                    else:
                        prev = int(en)

                play_urls[episode_format(en)] = url

        return play_urls