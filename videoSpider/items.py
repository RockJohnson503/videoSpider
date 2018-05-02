# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy, datetime
from pypinyin import lazy_pinyin
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class VideoItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class VideospiderItem(scrapy.Item):
    # define the fields for your item here like:
    play_url = scrapy.Field()
    list_type = scrapy.Field()
    video_des = scrapy.Field()
    video_name = scrapy.Field()
    spell_name = scrapy.Field(
        input_processor = MapCompose(lambda x: "".join(lazy_pinyin(x)))
    )
    video_addr = scrapy.Field()
    video_type = scrapy.Field(
        output_processor = Join(" ")
    )
    video_time = scrapy.Field()
    video_actor = scrapy.Field(
        input_processor = MapCompose(lambda x: x.strip().strip("\n").strip("\r").strip("\t")),
        output_processor = Join(" ")
    )
    video_origin = scrapy.Field()
    video_director = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip().strip("\n").strip("\r").strip("\t"))
    )
    video_language = scrapy.Field()
    front_image_url = scrapy.Field()

    def get_insert_sql(self):
        # 执行插入数据库的sql语句
        insert_sql = ["""
            insert into videos(video_origin, list_type, video_des, video_name,
            spell_name, video_addr, video_type, video_time,
            video_actor, video_director, video_language,
            front_image_url, crawl_time, crawl_update_time) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on DUPLICATE key update crawl_update_time = values(crawl_update_time)
        """]

        params = [[
            self["video_origin"],
            self["list_type"],
            self["video_des"] if "video_des" in self.keys() else None,
            self["video_name"],
            self["spell_name"],
            self["video_addr"] if "video_addr" in self.keys() else "内地",
            self["video_type"] if "video_type" in self.keys() else None,
            self["video_time"] if "video_time" in self.keys() else "2018",
            self["video_actor"] if "video_actor" in self.keys() else None,
            self["video_director"] if "video_director" in self.keys() else None,
            self["video_language"] if "video_language" in self.keys() else "国语",
            self["front_image_url"],
            datetime.datetime.now(),
            datetime.datetime.now()
        ]]

        if self["list_type"] != "电影":
            for items in self["play_url"]:
                insert_sql.append("""
                insert into episodes(video_id, episode, video_url)
                values(%s, %s, %s)
                """)
                params.append((
                    self["front_image_url"],
                    items,
                    self["play_url"].get(items)
                ))
        else:
            insert_sql.append("""
            insert into episodes(video_id, video_url)
            values(%s, %s)
            """)
            params.append((
                self["front_image_url"],
                self["play_url"]
            ))

        return insert_sql, params