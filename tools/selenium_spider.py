# encoding: utf-8

"""
File: selenium_spider.py
Author: Rock Johnson
"""
import os, time
from selenium import webdriver

# 电视剧的分页处理
def get_last_tv(url, ex_path):
    browser = webdriver.PhantomJS(executable_path=ex_path)
    browser.get(url)
    i = 2
    while True:
        try:
            buttons = browser.find_element_by_css_selector(".albumTabPills:nth-child(1) li:nth-child(" + str(i) + ")")
        except:
            break
        buttons.click()
        time.sleep(1)
        j = 1
        while True:
            try:
                urls = browser.find_element_by_css_selector(".piclist-wrapper[data-tab-body='widget-tab-3'] "
                                                            ".site-piclist li:nth-child(" + str(j) + ") "
                                                            ".site-piclist_info_title a")
            except:
                break
            if "预告" not in urls.text:
                yield urls.text, urls.get_attribute("href")
                j += 1
            else:
                break
        i += 1
    browser.quit()

# 综艺的分页处理
def get_last_variety(url, ex_path):
    browser = webdriver.PhantomJS(executable_path=ex_path)
    browser.get(url)
    while True:
        try:
            no_page = browser.find_element_by_css_selector("#album_pic_paging .noPage")
            if no_page.text == "下一页":
                break
            else:
                browser.find_element_by_css_selector("#album_pic_paging a[data-key='down']").click()
        except:
            browser.find_element_by_css_selector("#album_pic_paging a[data-key='down']").click()

        i = 1
        while True:
            try:
                time = browser.find_element_by_css_selector("#albumpic-showall-wrap "
                                                            "li:nth-child(" + str(i) + ") "
                                                            ".wrapper-listTitle span")
                urls = browser.find_element_by_css_selector("#albumpic-showall-wrap "
                                                            "li:nth-child(" + str(i) + ") "
                                                            ".site-piclist_pic_link")
            except:
                break
            yield time.text, urls.get_attribute("href")
            i += 1
    browser.quit()

# 动漫的分页处理
def get_last_anime(url, ex_path):
    browser = webdriver.PhantomJS(executable_path=ex_path)
    browser.get(url)

    select_page = browser.find_element_by_css_selector("#block-H .mod-album_tab_num a.selected")
    i = 2 if select_page.get_attribute("data-avlist-page") == "1" else int(select_page.get_attribute("data-avlist-page")) - 1
    step = 1 if select_page.get_attribute("data-avlist-page") == "1" else -1
    while True:
        try:
            buttons = browser.find_element_by_css_selector("#block-H .mod-album_tab_num a:nth-child(" + str(i) + ")")
        except:
            break
        buttons.click()
        time.sleep(1)
        j = 1
        while True:
            try:
                urls = browser.find_element_by_css_selector(".wrapper-piclist ul "
                                                            "li:nth-child(" + str(j) + ") "
                                                            ".site-piclist_info "
                                                            ".site-piclist_info_title a")
            except:
                break
            yield urls.text, urls.get_attribute("href")
            j += 1
        i += step
    browser.quit()

# 优酷电视剧的分页处理
def get_youku_tv(url, ex_path):
    browser = webdriver.PhantomJS(executable_path=ex_path)
    browser.get(url)

    i = 1
    while True:
        j = 1
        try:
            button = browser.find_element_by_css_selector("#showInfo .p-tab-pills li:nth-child(" + str(i) + ")")
        except:
            break
        button.click()
        time.sleep(1)

        while True:
            try:
                episode_node = browser.find_element_by_css_selector(".p-panel:nth-child(" + str(i) + ") ul li:nth-child(" + str(j) + ") a")
                try:
                    browser.find_element_by_css_selector(".p-panel:nth-child(" + str(i) + ") ul li:nth-child(" + str(j) + ") i.p-icon-preview")
                    break
                except:
                    yield episode_node.text, episode_node.get_attribute("href")
            except:
                break
            j += 1
        i += 1
    browser.quit()