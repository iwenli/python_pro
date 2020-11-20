#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-20 11:26:02
LastEditors: iwenli
LastEditTime: 2020-11-20 13:16:38
Description: ...
'''
__author__ = 'iwenli'

from ebook_qd import crawl_book
from utils import http

if __name__ == "__main__":
    # crawl_book()
    url = 'http://baidu.com'
    rep = http.get(url)
    print(rep)
