# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-21 16:06:53
@LastEditors: iwenli
@LastEditTime: 2019-05-25 14:29:11
@Description: 装饰器
'''
__author__ = 'iwenli'

import functools
import time
import txlog

log = txlog.TxLog()


def decorate_raise(func):
    '''
    异常统计装饰器
    '''

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.error(str(e))
            return None

    return wrap


def cast_count(text):
    '''
    执行耗时装饰器
    '''

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
