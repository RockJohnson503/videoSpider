# -*- coding: utf-8 -*-
import scrapy, requests, json
from urllib import parse
from scrapy.http import Request
from videoSpider.items import *
from tools.xici_ip import get_ip
from fake_useragent import UserAgent
from tools.common import episode_format, error_video
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
        post_nodes = response.css("li.list_item")
        list_type = response.css(".filter_list a.current::text").extract_first("")
        for post_node in post_nodes:
            image_url = parse.urljoin(response.url, post_node.css(".figure img::attr(r-lazyload)").extract_first(""))
            post_url = post_node.css(".figure::attr(href)").extract_first("")
            video_name = post_node.css(".figure_title a::text").extract_first("")
            video_actor = None
            if list_type == "电影" or list_type == "电视剧":
                video_actor = post_node.css(".figure_desc a::text").extract()

            v_state = post_node.css(".figure .mark_v img::attr(alt)").extract_first("")
            if "预告" not in v_state and image_url != response.url:
                yield Request(url=parse.urljoin(response.url, post_url),
                              meta={"front_image_url": image_url,
                                    "list_type": list_type,
                                    "video_name": video_name,
                                    "video_actor": video_actor},
                              callback=self.parse_director,
                              priority=9)

        # 提取下一页
        next_url = response.css(".mod_pages .page_next::attr(href)").extract_first("")
        if len(next_url) != "javascript:;":
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_director(self, response):
        # 解析导演
        v_type = director = v_time = None
        if response.meta.get("list_type", "") == "综艺":
            v_type = response.css(".video_tags a[href*='search']::text").extract()
        else:
            director = response.css(".director a::text").extract_first("")
            v_time = response.css(".video_tags a[href*='year']::text").extract_first("")
            if v_time == "":
                v_time = response.css(".video_tags span::text").extract_first("")

        detail_url = response.css(".player_title a::attr(href)").extract_first("")
        addr = response.css(".video_tags a::text").extract_first("")

        yield Request(url=parse.urljoin(response.url, detail_url),
                      meta={"front_image_url": response.meta.get("front_image_url", ""),
                            "list_type": response.meta.get("list_type", ""),
                            "video_name": response.meta.get("video_name", ""),
                            "video_actor": response.meta.get("video_actor", ""),
                            "play_url": response.url,
                            "addr": addr,
                            "v_time": v_time,
                            "v_type": v_type,
                            "director": director},
                      callback=self.parse_details,
                      priority=10)
        SpiderStateMiddleware.crawling += 1

    def parse_details(self, response):
        # 对视频细节的解析
        v_name = response.meta.get("video_name", "")
        print("正在爬取: %s" % v_name)
        play_urls = {}
        list_type = response.meta.get("list_type", "")
        v_type = response.meta.get("v_type", "")
        v_type = response.css(".video_tag .tag_list a::text").extract() if v_type == "" else v_type
        v_time = response.meta.get("v_time", "")

        # 解析视频语言字段
        lang = None
        for type in  response.css(".type_item"):
            if type.css(".type_tit::text").extract_first("") == "语　言:":
                lang = type.css(".type_txt::text").extract_first("")
            if list_type == "综艺" and type.css(".type_tit::text").extract_first("") == "首播时间:":
                v_time = type.css(".type_txt::text").extract_first("")
                v_time = v_time[:v_time.find("-")]

        # 处理分页问题
        if list_type == "电影":
            play_urls = response.meta.get("play_url", "")
        else:
            play_urls = self.parse_episode(response)

        # 将解析后的数据添加如Item
        item_loader = VideoItemLoader(item=VideospiderItem(), response=response)

        item_loader.add_value("play_url", play_urls)
        item_loader.add_value("list_type", list_type)
        item_loader.add_css("video_des", ".video_desc .desc_txt span::text")
        item_loader.add_value("video_name", v_name)
        item_loader.add_value("spell_name", v_name)
        item_loader.add_value("video_addr", response.meta.get("addr", ""))
        item_loader.add_value("video_type", v_type)
        item_loader.add_value("video_time", v_time)
        item_loader.add_value("video_actor", response.meta.get("video_actor", ""))
        item_loader.add_value("video_origin", "腾讯")
        item_loader.add_value("video_director", response.meta.get("director", ""))
        item_loader.add_value("video_language", lang)
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

    def parse_episode(self, response):
        #　解析播放路径
        play_urls = {}
        if not response.css(".mod_episode .item_all") and not response.css(".mod_episode_tabs"):
            for item in response.css(".mod_episode .item"):
                if "预告" not in item.css(".mark_v img::attr(alt)").extract_first(""):
                    en = item.css("a span::text").extract_first("")
                    url = item.css("a::attr(href)").extract_first("")
                    play_urls[episode_format(en)] = url
        else:
            detail_url = "https://s.video.qq.com/get_playsource?id=%s&plat=2&type=4&data_type=%s&video_type=%s&range=%s&plname=qq&otype=json&num_mod_cnt=20"

            # 获取id
            rurl = response.url
            id = rurl[rurl.rfind("/") + 1:rurl.find(".html")]

            # 获取类型
            type = response.css(".video_title_cn .type::text").extract_first("")
            d_type = 2
            if type == "电视剧":
                v_type = 2
            elif type == "动漫":
                v_type = 3
            else:
                v_type = 10
                d_type = 3

            get = get_ip()
            p_url = get.get_random_ip()
            get.close()
            proxy_dict = {
                "http": p_url
            }
            headers = {"User-Agent": getattr(UserAgent(), "random")}
            res = requests.get(parse.urljoin(response.url, detail_url % (id, d_type, v_type, "1-9999")),
                               proxies=proxy_dict, headers=headers)
            text = res.text[res.text.find("=") + 1: -1]
            all_json = json.loads(text)
            try:
                plists = all_json["PlaylistItem"]["videoPlayList"]
            except:
                return response.css(".btn_primary::attr(href)").extract_first("")
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