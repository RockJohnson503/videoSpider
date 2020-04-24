# encoding: utf-8

"""
File: xici_ip.py
Author: Rock Johnson
"""
import requests, time
from .con_sql import conn_sql
from scrapy.selector import Selector


def crawl_ip():
    # 爬取西刺的ip代理
    conn = conn_sql()

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"}
    size = requests.get("http://www.xicidaili.com/nn", headers=headers)
    size = Selector(text=size.text).css(".pagination a:nth-child(13)::text").extract_first("")
    for i in range(1, int(size) + 1):
        time.sleep(3)
        re = requests.get("http://www.xicidaili.com/nn/%s" % i, headers=headers)
        select = Selector(text=re.text)
        all_trs = select.css("#ip_list tr ")

        ip_list = []
        for tr in all_trs[1:]:
            speed = tr.css(".bar::attr(title)").extract()[0]
            if speed:
                speed = float(speed.split("秒")[0])
            all_texts = tr.css("td::text").extract()

            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]

            ip_list.append((ip, port, proxy_type, speed))

        for ip in ip_list:
            conn.excute("insert into ips(ip, port, proxy_type, speed) values(%s, %s, %s, %s)", ip)

    conn.close()


class get_ip:
    def __init__(self):
        # 连接mysql数据库
        self.conn = conn_sql()

    def close(self):
        # 关闭数据库连接
        self.conn.close()

    def get_random_ip(self):
        # 随机获取ip代理
        res = self.conn.excute("select ip, port, proxy_type from ips where proxy_type = 'HTTP' order by rand() limit 1")
        for ip, port, proxy_type in res:
            judge_re = self.judge_ip(ip, port, proxy_type)
            if judge_re:
                return "%s://%s:%s" % (proxy_type, ip, port)
            else:
                return self.get_random_ip()

    def judge_ip(self, ip, port, proxy_type):
        http_url = "https://www.baidu.com"
        proxy_url = "%s://%s:%s" % (proxy_type, ip, port)

        try:
            proxy_dict = {
                proxy_type: proxy_url
            }
            res = requests.get(http_url, proxies=proxy_dict)
        except:
            print("invalid proxy %s://%s:%s" % (proxy_type, ip, port))
            self.delete_ip(ip)
            return False
        else:
            code = res.status_code
            if code >= 200 and code < 300:
                return True
            else:
                print("invalid proxy %s://%s:%s" % (proxy_type, ip, port))
                self.delete_ip(ip)
                return False

    def delete_ip(self, ip):
        # 删除错误的ip
        self.conn.excute("delete from ips where ip = (%s)", ip)