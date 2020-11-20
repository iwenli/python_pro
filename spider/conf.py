#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-20 12:38:05
LastEditors: iwenli
LastEditTime: 2020-11-20 13:02:47
Description: 配置项
'''
__author__ = 'iwenli'

import os

db_conf = None
if(db_conf is None or len(db_conf) <= 1):
    db_conf = os.getenv('ebook_db_conf')
if(db_conf is None or len(db_conf) <= 1):
    raise Exception('请配置数据库连接串')
