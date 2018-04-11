# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from pypinyin import lazy_pinyin
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Identity


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
        output_processor=Join(" ")
    )
    video_director = scrapy.Field()
    video_language = scrapy.Field()
    front_image_url = scrapy.Field()
    video_update_time = scrapy.Field(
        input_processor = MapCompose()
    )
    pass