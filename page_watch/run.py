# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-21 11:09:25
@LastEditors: iwenli
@LastEditTime: 2019-05-26 17:12:07
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
import txnotify
import operator
import txdecorator

log = txlog.TxLog()
# taskQueue = queue.Queue()  # 任务队列
repository = data.Repository()

today = datetime.datetime.now().strftime('%Y%m%d')  # 当前日期格式化 年月日
todayts = time.mktime(time.strptime(today, '%Y%m%d'))  # 当前日期时间戳

todayts_fix = str(todayts)[:3]
html_filter_regex = re.compile(
    r'\?nex=[0-9a-zA-Z\-&;=\|]*|%s[\d]{0,5}|%s[\d]{10}|%s[\d]{7}' %
    (today, todayts_fix, todayts_fix))

fileRootPath = os.path.dirname(__file__)
fileRootPath = os.path.join(fileRootPath, '_file')
if not os.path.isdir(fileRootPath):
    os.mkdir(fileRootPath)


def html_filter(html):
    '''
    过滤html
    '''
    soup = bs4.BeautifulSoup(html, "html.parser")
    [s.extract() for s in soup(["script", "meta", "style", "input"])]
    return re.sub(html_filter_regex, '', soup.prettify())  # str(soup)


@txdecorator.decorate_raise
def savaDiffHtml(item, path):
    '''
    对比html
    '''
    html1 = item['source_html_filter']
    fullfilename = os.path.join(path, '%s.%s' % (item['sources_hash'], 'html'))
    html2 = readHtml(fullfilename)  # 旧内容从文件中读取

    d = difflib.HtmlDiff()
    result = d.make_file(html1.splitlines(), html2.splitlines())
    seq = difflib.SequenceMatcher(None, html1, html2)
    item['change_rate'] = round(100 * (1 - seq.ratio()), 2)
    filename = '_' + item['_sources_hash']
    savehtml(path, filename, result)
    return result


@txdecorator.decorate_raise
def readHtml(fullfilename):
    '''
    读取文件
    '''
    with open(fullfilename, 'r', encoding='utf-8') as f:
        return f.read()


def savehtml(path, filename, content):
    '''
    保存文件
    '''
    if filename is None or len(filename) == 0:
        return
    fullfilename = os.path.join(path, '%s.%s' % (filename, 'html'))
    with open(fullfilename, 'w', encoding='utf-8') as f:
        f.write(content)


def save(item):
    '''
    执行项目保存操作
    包括 存储HTML JPG 差异HTML
    1. 如果hash[旧]为空 insert(生成文件，图片) & update(hash)
    2. 如果hash[旧] != hash[新] 则insert(生成文件，图片，差异文件) & update(hash,ischange) 【发出页面变更通知】
    '''
    # 文件基础路径
    filePath = os.path.join(fileRootPath, str(item['page_url_id']))
    if not os.path.isdir(filePath):
        os.mkdir(filePath)
    savehtml(filePath, item.get('_sources_hash'),
             item.get('source_html_filter'))  # 保存当前节点html
    # 保存当前节点jpg
    pass
    # 如果不是新任务 生成差异
    old_hash = item.get('sources_hash', '')
    if len(old_hash) > 0 and old_hash != item.get('_sources_hash'):
        savaDiffHtml(item, filePath)
        txnotify.send(
            item, **{
                'title':
                '页面监控通知',
                'content':
                '[%s]发生变更，变化率为%s' %
                (item.get('page_url'), item.get('change_rate'))
            })


def update(item):
    '''
    数据库相关更新操作
    '''
    url_id = item['page_url_id']
    sources_hash = item['_sources_hash']
    is_change = 0 if len(item['sources_hash']) == 0 else 1
    rate = item.get('change_rate', 0.0)
    include = item.get('include', 0)

    repository.updateItem(url_id, sources_hash, is_change)
    repository.insertRecord(url_id, sources_hash, include, rate)


def item_filer(items):
    '''
    item过滤  hash相同只保留一个
    '''
    result = [x for x in items if x.get('sources_hash') == '']
    # group = in
    l1 = [x for x in items if x.get('sources_hash') != '']
    l1.sort(key=operator.itemgetter('sources_hash'))

    group = itertools.groupby(l1, key=operator.itemgetter('sources_hash'))
    for i, g in group:
        if (g is not None):
            glist = list(g)
            result.append(glist[0])
            if len(glist) > 1:
                ids = [x.get('page_url_id') for x in glist[1:]]
                repository.updateAllItemStatus(0, ids)
    return result


def process(item):
    '''
    每个项单独处理
    '''
    old_hash = item.get('sources_hash', '')
    if len(old_hash) == 0:
        txnotify.send(
            item, **{
                'title': '收到新监控通知',
                'content': '[%s]开始监控' % item.get('page_url')
            })
    h = network.gethtml(item)
    item['source_html'] = h
    html = html_filter(h)
    item['source_html_filter'] = html
    if len(html) > 100:
        # 正常处理
        hash = hashlib.md5(html.encode('utf-8')).hexdigest()  # 新的hash值
        if len(old_hash) == 0 or old_hash != hash:  # 如果是首次监控 或者hash变更
            item['_sources_hash'] = hash
            save(item)
            update(item)  # 更新数据
        # return hash
        # task = dict(item=item, html=html, hash=hash)
        # taskQueue.put(task)
    else:
        pass
        #     log.error(item)  # 异常数据记录日志


if __name__ == "__main__":
    '''
    1、获取所有需要监控的页面
    2、遍历页面开始执行
        a. 如果hash[旧]为空 【发送收到监控通知】
        b. 请求页面内容
            i. 页面各状态监控通知【404通知 3xx通知】
            ii. 页面抓取异常 【通知开发者】
            iii. 页面解码不要忽略编码异常，通过捕获编码异常来重试其他编码 [***后期可优化***]
        c. 页面过滤策略过滤动态内容
        d. 过滤后的内容生成hash[新]
        e. 如果hash[旧]为空 insert(生成文件，图片) & update(hash)
        f. 如果hash[旧] != hash[新] 则insert(生成文件，图片，差异文件) & update(hash,ischange) 【发出页面变更通知】
    3、过滤status=1 并且hash一致的数据只保留一条，其他的更新为status=0

    ******实体说明******
    item:
    {
        "page_url_id": 2,
        "brand_id":1,
        "account_id":1,
        "page_url": "http://086868.cn",
        "status": 1,
        "is_change": false,
        "add_time": "",
        "source_html":"",
        "sources_hash": "",
        "source_html_filter":"",
        "_sources_hash": "新hash",
        "elements_hash": "",
        "change_rate": 0.52,
        "include_code": false,
    }
    '''
    items = repository.getItems()
    log.debug("[全局]拉取待处理数据%s条..." % len(items))
    items_filters = item_filer(items)
    log.debug("[全局]过滤后剩余待处理数据%s条..." % len(items_filters))
    index = 0
    # print(items[1])
    for item in items_filters:
        index += 1
        log.warning('总[%s]当前[%s]' % (len(items_filters), index))
        process(item)
        # _list = [
        #     dict.copy(item),
        #     dict.copy(item),
        #     dict.copy(item),
        #     dict.copy(item),
        #     dict.copy(item)
        # ]
        # h_list = [process(x) for x in _list]
        # if (len(list(set(h_list))) != 1):
        #     # diff_list = [diffhtml(_list[0], x) for x in _list[1:]]
        #     diffhtml(_list[0], _list[1])
        #     log.warning(item)
    log.debug("[全局]ok...")
