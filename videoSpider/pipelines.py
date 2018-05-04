# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi
from tools.common import error_grammer


class VideospiderPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        # 获取setting里的数据库参数并调用连接池
        dparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = "utf8",
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常并存入数据库
        error_grammer(failure.value.args[1], item["video_name"])

    def do_insert(self, cursor, item):
        # 执行具体插入
        # 根据不同的item构建不同的插入语句
        insert_sql, params = item.get_insert_sql()
        for i in range(len(insert_sql)):
            cursor.execute(insert_sql[i], params[i])