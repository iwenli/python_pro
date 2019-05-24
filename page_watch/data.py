# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-21 11:11:16
@LastEditors: iwenli
@LastEditTime: 2019-05-24 11:30:49
@Description: 数据仓储操作
'''
__author__ = 'iwenli'

import os
import txdb
import txdecorator
import json

conf_str = os.getenv("PY_PW_CONF")  # 环境变量中提取配置字符串
if conf_str is None:
    conf_str = ''
_conf = json.loads(conf_str)


class Repository(object):
    @txdecorator.cast_count('db.mssql')
    def __init__(self):
        db_conf = _conf.get('db_mssql')
        if (db_conf is None):
            raise Exception('sql配置为空')
        self._db_pagewatch = db_conf.get('TxoooSEMPageWatch')
        self._db_mobile = db_conf.get('TxoooMobile')
        self._db_nex = db_conf.get('TxoooNEx')

    @txdecorator.cast_count('db.mssql')
    def getItems(self):
        '''
        获取待检测项
        '''
        with txdb.TxDataHelper(False, **self._db_pagewatch) as helper:
            # select
            result = helper.sql_getdate(
                'select * from watch_item where status = 1')
            return result

    @txdecorator.cast_count('db.mssql')
    def getAccount(self, accountid):
        '''
        获取账户信息
        内部不维修brandtoken
        当前每次冲数据库中获取

        时间差计算
        dt = datetime.datetime.strptime('2019-05-23 10:37:00', '%Y-%m-%d %H:%M:%S')
        delta = datetime.datetime.now() - dt
        print(delta > datetime.timedelta(seconds=7000))
        '''
        with txdb.TxDataHelper(False, **self._db_mobile) as helper:
            sql = '''
                SELECT account_id,app_id,app_secret,access_token
                ,access_token_time
                FROM TxoooMobile.dbo.Platform_Account WHERE account_id = %s
            '''
            result = helper.sql_getdate(sql, args=(accountid, ))
            return result[0] if result is not None and len(
                result) == 1 else None

    def getNotifySettings(self):
        '''
        获取所有通知配置项
        '''
        with txdb.TxDataHelper(False, **self._db_nex) as helper:
            sql = '''
                SELECT id,brand_id,wx_account_id,wx_template_id,wx_open
                FROM dbo.brand_notify_setting WHERE business = 2
            '''
            result = helper.sql_getdate(sql)
            return result

    def getNotifyUsers(self):
        '''
        获取所有通知配置项
        '''
        with txdb.TxDataHelper(False, **self._db_nex) as helper:
            sql = '''
                SELECT * FROM dbo.brand_notify_user WHERE setting_id IN (
                    SELECT id FROM dbo.brand_notify_setting
                    WHERE business = 2
                )
            '''
            result = helper.sql_getdate(sql)
            return result


if __name__ == "__main__":
    repository = Repository()
    account = repository.getAccount(100000000)
    print(account)
    settings = repository.getNotifySettings()
    print(settings)
    users = repository.getNotifyUsers()
    print(users)
