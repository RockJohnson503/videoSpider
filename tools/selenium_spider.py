# encoding: utf-8

"""
File: selenium_spider.py
Author: Rock Johnson
"""
import os, time
from selenium import webdriver

# 启动selenium的装饰器
def start_sel(fun):
    options = webdriver.ChromeOptions()
    # options.add_argument('user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit'
    #                      '/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.set_headless()
    def inner(*args):
        browser = webdriver.Chrome(executable_path=args[1], chrome_options=options)
        browser.get(args[0])
        time.sleep(1)
        return fun(args[0], args[1], browser)
    return inner

# 爱奇艺电视剧的分页处理
@start_sel
def get_last_tv(url, ex_path, browser=None):
    i = 2
    while True:
        try:
            buttons = browser.find_element_by_css_selector(".albumTabPills:nth-child(1) li:nth-child(%s)" % i)
        except:
            try:
                buttons = browser.find_element_by_css_selector(".mod-album_tab_num.fl[data-widget='album-jujiPagelist']"
                                                               " a:nth-child(%s)" % i)
            except:
                break
        buttons.click()
        time.sleep(1)

        j = 1
        while True:
            try:
                urls = browser.find_element_by_css_selector(".piclist-wrapper[data-tab-body='widget-tab-3'] "
                                                            ".site-piclist li:nth-child(%s) "
                                                            ".site-piclist_info_title a" % j)
            except:
                try:
                    urls = browser.find_element_by_css_selector(".wrapper-piclist ul li:nth-child(%s) "
                                                            ".site-piclist_info_title a" % j)
                except:
                    break
            if "预告" not in urls.text:
                yield urls.text, urls.get_attribute("href")
                j += 1
            else:
                break
        i += 1
    browser.quit()

# 爱奇艺综艺的分页处理
@start_sel
def get_last_variety(url, ex_path, browser=None):
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
                                                            "li:nth-child(%s) "
                                                            ".wrapper-listTitle span" % i)
                urls = browser.find_element_by_css_selector("#albumpic-showall-wrap "
                                                            "li:nth-child(%s) "
                                                            ".site-piclist_pic_link" % i)
            except:
                break
            yield time.text, urls.get_attribute("href")
            i += 1
    browser.quit()

# 爱奇艺动漫的分页处理
@start_sel
def get_last_anime(url, ex_path, browser=None):
    try:
        select_page = browser.find_element_by_css_selector(".subTab-sel .selEpisodeTab-wrap .albumTabPills li.selected")
    except:
        select_page = browser.find_element_by_css_selector(".subTab-sel .selEpisodeTab-wrap .albumAllset-li li.selected")
    i = 2 if select_page.get_attribute("data-avlist-page") == "1" else int(select_page.get_attribute("data-avlist-page")) - 1
    step = 1 if select_page.get_attribute("data-avlist-page") == "1" else -1
    while True:
        j = 1
        try:
            browser.find_element_by_css_selector(".subTab-sel .selEpisodeTab-wrap .albumTabPills li[data-avlist-page='%s']" % i).click()
        except:
            try:
                if not browser.find_element_by_css_selector(".albumAllset-tank").is_displayed():
                    browser.find_element_by_css_selector(".albumAllset-btn").click()
                browser.find_element_by_css_selector(
                    ".subTab-sel .selEpisodeTab-wrap .albumAllset-li li[data-avlist-page='%s']" % i).click()
            except:
                break
        time.sleep(1)

        while True:
            try:
                urls = browser.find_element_by_css_selector(".piclist-wrapper[data-tab-body='widget-tab-3'] ul.site-piclist "
                                                            "li:nth-child(%s) "
                                                            ".site-piclist_info "
                                                            ".site-piclist_info_title a" % j)
            except:
                break
            if "预告" not in urls.text:
                yield urls.text, urls.get_attribute("href")
                j += 1
        i += step
    browser.quit()


# 优酷电视剧的分页处理
@start_sel
def get_youku_tv(url, ex_path, browser=None):
    i = 1
    while True:
        j = 1
        try:
            button = browser.find_element_by_css_selector("#showInfo .p-tab-pills li:nth-child(%s)" % i)
        except:
            while True:
                try:
                    episode_node = browser.find_element_by_css_selector(
                        ".p-panel:nth-child(%s) ul li:nth-child(%s) a" % (i, j))
                    try:
                        browser.find_element_by_css_selector(
                            ".p-panel:nth-child(%s) ul li:nth-child(%s) i.p-icon-preview" % (i, j))
                        break
                    except:
                        yield episode_node.text, episode_node.get_attribute("href")
                except:
                    break
                j += 1
            break
        button.click()
        time.sleep(1)

        while True:
            try:
                episode_node = browser.find_element_by_css_selector(".p-panel:nth-child(%s) ul li:nth-child(%s) a" % (i, j))
                try:
                    browser.find_element_by_css_selector(".p-panel:nth-child(%s) ul li:nth-child(%s) i.p-icon-preview" % (i, j))
                    break
                except:
                    yield episode_node.text, episode_node.get_attribute("href")
            except:
                break
            j += 1
        i += 1
    browser.quit()

# 优酷动漫的分页处理
@start_sel
def get_youku_anime(url, ex_path, browser=None):
    i = 1
    while True:
        j = 1
        try:
            buttons = browser.find_element_by_css_selector("#showInfo ul.p-tab-pills li:nth-child(%s)" % i)
        except:
            if i == 1:
                while True:
                    try:
                        ep = browser.find_element_by_css_selector(".p-panel:not(.hide) li:nth-child(%s) div" % j)
                        href = browser.find_element_by_css_selector(".p-panel:not(.hide) li:nth-child(%s) div a" % j)
                    except:
                        break
                    else:
                        yield ep.text.replace(href.text, ""), href.get_attribute("href")
                        j += 1
            break
        buttons.click()
        time.sleep(1)

        while True:
            try:
                ep = browser.find_element_by_css_selector(".p-panel:not(.hide) li:nth-child(%s) div" % j)
                href = browser.find_element_by_css_selector(".p-panel:not(.hide) li:nth-child(%s) div a" % j)
            except:
                break
            else:
                yield ep.text.replace(href.text, ""), href.get_attribute("href")
                j += 1
        i += 1
    browser.quit()

# 优酷综艺的分页处理
@start_sel
def get_youku_variety(url, ex_path, browser=None):
    i = 1
    while True:
        j = 1
        try:
            buttons = browser.find_element_by_css_selector("#showInfo ul.p-tab-pills li:nth-child(%s)" % i)
        except:
            if i == 1:
                while True:
                    try:
                        ep = browser.find_element_by_css_selector(".p-panel:not(.hide) li:nth-child(%s) dt" % j)
                        href = browser.find_element_by_css_selector(".p-panel:not(.hide) li:nth-child(%s) dt a" % j)
                    except:
                        break
                    else:
                        yield ep.text.replace(href.text, ""), href.get_attribute("href")
                        j += 1
            break
        buttons.click()
        time.sleep(1)

        while True:
            try:
                ep = browser.find_element_by_css_selector(".p-panel:not(.hide) li:nth-child(%s) dt" % j)
                href = browser.find_element_by_css_selector(".p-panel:not(.hide) li:nth-child(%s) dt a" % j)
            except:
                break
            else:
                yield ep.text.replace(href.text, ""), href.get_attribute("href")
                j += 1
        i += 1
    browser.quit()