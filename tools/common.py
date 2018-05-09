# encoding: utf-8

"""
File: common.py
Author: Rock Johnson
"""
import hashlib, re, pymysql
from videoSpider import settings


# 将路径加密为长度固定的字符
def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

# 格式化电视剧 动漫和综艺的集数
def episode_format(episode):
    try:
        episode = int(episode)
        return episode
    except:
        return int(re.sub("\D", "", episode))

# 判断动漫是否为电影版或剧场版
def is_anime(url):
    pat = re.compile(r'.*www.iqiyi.com/a_.*')
    res = pat.match(url)
    return res

# 连接mysql数据库
def conn_sql(sql, params):
    dbparms = dict(
        host=settings.MYSQL_HOST,
        db=settings.MYSQL_DBNAME,
        user=settings.MYSQL_USER,
        passwd=settings.MYSQL_PASSWORD,
        charset='utf8',
        use_unicode=True,
    )
    conn = pymysql.connect(**dbparms)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

# 将报错的综艺添加到数据库
def error_video(list_type, url, name):
    insert_sql = """
        insert into errvideos(list_type, video_url, video_name)
        values(%s, %s, %s)
    """
    conn_sql(insert_sql, (list_type, url, name))

# 将报错的语法添加到数据库
def error_grammer(grammer, sql, param, video_name):
    insert_sql = """
        insert into errgrammer(grammer, insert_sql, param, video_name)
        values(%s, %s, %s, %s)
    """
    conn_sql(insert_sql, (grammer, sql, param, video_name))