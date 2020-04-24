# encoding: utf-8

"""
File: common.py
Author: Rock Johnson
"""
import hashlib, re, datetime, requests
from tools.xici_ip import get_ip
from tools.con_sql import conn_sql

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
        if episode == "番外":
            return -1
        return int(re.sub("\D", "", episode))

# 请求播放路径
def request_url(url, proxies=True, header=True):
    if proxies:
        get = get_ip()
        p_url = get.get_random_ip()
        get.close()
    proxy_dict = {
        "http": p_url
    } if proxies else None
    res = requests.get(url, proxies=proxy_dict)
    return res

# 判断是否为播放页面
def is_player(url):
    pat = re.compile(r'.*www.iqiyi.com/v_.*')
    res = pat.match(url)
    return res

# 将报错的综艺添加到数据库
def error_video(list_type, url, reason, name):
    insert_sql = """
        insert into errvideos(list_type, video_url, reason, video_name, r_time)
        values(%s, %s, %s, %s, %s) on duplicate key update r_time = values(r_time)
    """
    conn = conn_sql("errors")
    conn.excute(insert_sql, (list_type, url, reason, name, datetime.datetime.now()))
    conn.close()

# 将报错的语法添加到数据库
def error_grammer(grammer, sql, param, video_name):
    insert_sql = """
        insert into errgrammers(err_time, grammer, insert_sql, param, video_name)
        values(%s, %s, %s, %s, %s)
    """
    conn = conn_sql("errors")
    conn.excute(insert_sql, (datetime.datetime.now(), grammer, sql, param, video_name))
    conn.close()

# 记录爬取的信息
def crawl_info(c_name, s_time, e_time, sd_time, ing, ed, err):
    insert_sql = """
            insert into info(crawl_name, start_time, end_time, spend_time, crawling, crawled, crawlerr)
            values(%s, %s, %s, %s, %s, %s, %s)
        """
    conn = conn_sql("crawlinfo")
    conn.excute(insert_sql, (c_name, s_time, e_time, sd_time, ing, ed, err))
    conn.close()