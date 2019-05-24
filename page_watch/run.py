# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-21 11:09:25
@LastEditors: iwenli
@LastEditTime: 2019-05-24 09:59:15
@Description: 页面监控入口
'''
__author__ = 'iwenli'

import data
import network
import txlog
import queue
import hashlib
import bs4
import itertools
import difflib
import os
import datetime
import time
import re

log = txlog.TxLog()
taskQueue = queue.Queue()  # 任务队列

today = datetime.datetime.now().strftime('%Y%m%d')  # 当前日期格式化 年月日
todayts = time.mktime(time.strptime(today, '%Y%m%d'))  # 当前日期时间戳

todayts_fix = str(todayts)[:3]
html_filter_regex = re.compile(
    r'\?nex=[0-9a-zA-Z\-&;=\|]*|%s[\d]{0,5}|%s[\d]{10}|%s[\d]{7}' %
    (today, todayts_fix, todayts_fix))

dir = os.path.dirname(__file__)
dir = os.path.join(dir, '_file')
if not os.path.isdir(dir):
    os.mkdir(dir)


def savehtml(filename, txt):
    '''
    保存文件
    '''
    filepath = os.path.join(dir, filename + '.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(txt)


def html_filter(html):
    '''
    过滤html
    '''
    soup = bs4.BeautifulSoup(html, "html.parser")
    [s.extract() for s in soup(["script", "meta", "style", "input"])]
    return re.sub(html_filter_regex, '', soup.prettify())  # str(soup)


def diffhtml(item1, item2):
    '''
    对比html
    '''
    d = difflib.HtmlDiff()
    html1 = item1['source_html_filter']
    html2 = item2['source_html_filter']
    result = d.make_file(html1.splitlines(), html2.splitlines())
    seq = difflib.SequenceMatcher(None, html1, html2)
    ratio = 1 - seq.ratio()
    savehtml(item2['sources_hash'] + '_' + str(ratio), result)
    return result


def process(item):
    h = network.gethtml(item)
    item['source_html'] = h
    html = html_filter(h)
    item['source_html_filter'] = html
    if len(html) > 100:
        # 正常处理
        hash = hashlib.md5(html.encode('utf-8')).hexdigest()
        item['sources_hash'] = hash
        return hash
        # task = dict(item=item, html=html, hash=hash)
        # taskQueue.put(task)
    else:
        pass
        #     log.error(item)  # 异常数据记录日志


if __name__ == "__main__":
    '''
    1、获取所有需要监控的页面
    2、遍历页面开始抓取
    3、根据抓取结果执行具体业务
        a.如果hash为空  直接insert & update
        b.如果hash不为空，判断跟上一次是否一致，如果不一致，则insert & update
    
        **** 每个insert & update 任务需要抓图并记录html
    4、过滤status=1 并且hash一致的数据只保留一条，其他的更新为status=0
    '''

    repository = data.Repository()
    items = repository.getItems()
    log.debug("[全局]拉取待处理数据%s条..." % len(items))
    index = 0
    for item in items:
        index += 1
        log.warning('总[%s]当前[%s]' % (len(items), index))
        _list = [
            dict.copy(item),
            dict.copy(item),
            dict.copy(item),
            dict.copy(item),
            dict.copy(item)
        ]
        h_list = [process(x) for x in _list]
        if (len(list(set(h_list))) != 1):
            # diff_list = [diffhtml(_list[0], x) for x in _list[1:]]
            diffhtml(_list[0], _list[1])
            log.warning(item)
    log.debug("[全局]ok...")
