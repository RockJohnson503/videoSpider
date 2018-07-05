# encoding: utf-8

"""
File: con_sql.py
Author: Rock Johnson
"""
import pymysql
from videoSpider import settings

# 连接mysql数据库
class conn_sql:
    def __init__(self, db=None):
        dbparms = dict(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME if db == None else db,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWORD,
            charset='utf8',
            use_unicode=True,
        )
        self.conn = pymysql.connect(**dbparms)
        self.cursor = self.conn.cursor()

    def excute(self, sql, params=None):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()