# encoding: utf-8

"""
File: selenium_spider.py
Author: Rock Johnson
"""
import os
from selenium import webdriver


def get_last(url, size):
    browser = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))
    browser.get(url)
    for i in range(1, size):
        buttons = browser.find_element_by_css_selector(".albumTabPills:nth-child(1) li:nth-child(" + str(i + 1) + ")")
        buttons.click()
        for i in range(1, episode(buttons.text) + 2):
            urls = browser.find_element_by_css_selector(".albumSubTab-wrap .piclist-wrapper ul li:nth-child(" + str(i) + ") .site-piclist_info_title a")
            if "预告" not in urls.text:
                yield urls.text, urls.get_attribute("href")
            else:
                break


def episode(str):
    first_num = int(str[str.index("-") + 1:])
    last_num = int(str[:str.index("-")])
    return abs(first_num - last_num)