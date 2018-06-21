# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy, datetime
from tools.common import get_md5
from pypinyin import lazy_pinyin
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class VideoItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class VideospiderItem(scrapy.Item):
    # define the fields for your item here like:
    play_url = scrapy.Field()
    list_type = scrapy.Field()
    video_des = scrapy.Field(
        input_processor = MapCompose(lambda x: x[3:] if "简介：" in x else x)
    )
    video_name = scrapy.Field()
    spell_name = scrapy.Field(
        input_processor = MapCompose(lambda x: "".join(lazy_pinyin(x)))
    )
    video_addr = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip().strip("\n").strip("\r").strip("\t"))
    )
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
        video_id = get_md5(self["front_image_url"])
        insert_sql = ["""
            insert into videos(video_id, video_origin, list_type, video_des, video_name,
            spell_name, video_addr, video_type, video_time,
            video_actor, video_director, video_language,
            front_image_url, crawl_time, crawl_update_time) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update video_des = values(video_des),
            video_name = values(video_name), spell_name = values(spell_name),
            video_addr = values(video_addr), video_type = values(video_type),
            video_time = values(video_time), video_actor = values(video_actor),
            video_director = values(video_director), video_language = values(video_language),
            crawl_update_time = values(crawl_update_time)
        """]

        params = [[
            video_id,
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

        flag = self["play_url"] if isinstance(self["play_url"], dict) else range(1, 2)
        for items in flag:
            insert_sql.append("""
                insert into episodes(video_id, episode, video_url) values(%s, %s, %s)
                on duplicate key update v_id_pre = if(video_id != values(video_id), 
                video_id, null), video_id = values(video_id)
            """)

            params.append((
                video_id,
                items,
                self["play_url"].get(items) if isinstance(self["play_url"], dict) else self["play_url"]
            ))

        return insert_sql, params