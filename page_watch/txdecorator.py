# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-21 16:06:53
@LastEditors: iwenli
@LastEditTime: 2019-05-21 16:34:47
@Description: 装饰器
'''
__author__ = 'iwenli'

import functools
import time
import txlog

log = txlog.TxLog()


def cast_count(text):
    def decorator(func):
        @functools.wraps(func)  # 防止函数now1.__name__ == wrapper
        def wrapper(*args, **kw):
            s = time.time()
            r = func(*args, **kw)
            log.info('[%s]-[%s()] 耗时: %s 秒' %
                     (text, func.__name__, time.time() - s))
            return r

        return wrapper

    return decorator
