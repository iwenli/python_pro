#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-20 13:11:13
LastEditors: iwenli
LastEditTime: 2020-11-20 18:04:22
Description: 工具
'''
__author__ = 'iwenli'

import requests
from retrying import retry
from bs4 import BeautifulSoup
import re
import os


class Convert(object):

    CN_NUM = {
        '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '零': 0,
        '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '貮': 2, '两': 2,
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
    }

    CN_UNIT = {
        '十': 10,
        '拾': 10,
        '百': 100,
        '佰': 100,
        '千': 1000,
        '仟': 1000,
        '万': 10000,
        '萬': 10000,
        '亿': 100000000,
        '億': 100000000,
        '兆': 1000000000000,
    }

    def chinese_to_arabic(self, cn):
        unit = 0   # current
        ldig = []  # digest
        for cndig in reversed(cn):
            if cndig in self.CN_UNIT:
                unit = self.CN_UNIT.get(cndig)
                if unit == 10000 or unit == 100000000:
                    ldig.append(unit)
                    unit = 1
            else:
                dig = self.CN_NUM.get(cndig)
                if unit:
                    dig *= unit
                    unit = 0
                ldig.append(dig)
        if unit == 10:
            ldig.append(10)
        val, tmp = 0, 0
        for x in reversed(ldig):
            if x == 10000 or x == 100000000:
                val += tmp * x
                tmp = 0
            else:
                tmp += x
        val += tmp
        return val

    def to_chapter(self, chapter_title):
        '''
        规范的章节 转为 (index,name)
        [第五十三章 ...]
        '''
        r = re.findall("(第(.*?)章)", chapter_title)
        if(r is None or len(r) != 1 or len(r[0]) != 2):
            return
        return (self.chinese_to_arabic(r[0][1]), str.strip(chapter_title.replace(r[0][0], '')))


class Http(object):
    """
    一个发送网络请求的简单封装
    """
    headers = {}

    @retry(stop_max_attempt_number=3)  # 最大重试3次，3次全部报错，才会报错
    def get_internal(url):
        '''
        get请求的出口
        '''
        response = requests.get(
            url, headers=Http.headers, timeout=3)  # 超时的时候回报错并重试

        if(response.status_code != 200):
            print(f'{url}请求状态{response.status_code}，马上重试')

        assert response.status_code == 200  # 状态码不是200，也会报错并充实
        return response

    def get(self, url):
        return Http.get_internal(url)

    def get_text(self, url, encoding='utf-8'):
        resp = Http.get_internal(url)
        resp.encoding = encoding
        return resp.text

    def get_cookie(self, url, cookie_name):
        response = Http.get_internal(url)
        cookies = requests.utils.dict_from_cookiejar(response.cookies)
        cookie = cookies.get(cookie_name)
        return cookie

    def get_beautifulsoup(self, url):
        text = self.get_text(url)
        return BeautifulSoup(text, 'html.parser')


class File(object):
    """
    文件辅助操作
    """
    root_path = os.path.dirname(__file__)
    download_path = os.path.join(root_path, '_download')
    if not os.path.isdir(download_path):
        os.mkdir(download_path)

    def write_book(self, book_id, serial_nums, txt):
        book_path = os.path.join(self.download_path, str(book_id))
        if not os.path.isdir(book_path):
            os.mkdir(book_path)

        file_name = str(serial_nums) + '.txt'
        file_path = os.path.join(book_path, file_name)

        with open(file_path, 'w+', encoding='utf-8') as f:
            f.write(txt)


http = Http()
convert = Convert()
file = File()

# num = convert.chinese_to_arabic('五百二十3')
# print(num)

# r = convert.to_chapter('第一千四百一十三章 合体！')
# print(r)