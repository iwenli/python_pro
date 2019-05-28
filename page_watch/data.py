# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-21 11:11:16
@LastEditors: iwenli
@LastEditTime: 2019-05-28 16:49:19
@Description: 数据仓储操作
'''
__author__ = 'iwenli'

import os
import txdb
import txdecorator
import json
import txlog

log = txlog.TxLog()
conf_str = os.getenv("PY_PW_CONF")  # 环境变量中提取配置字符串
_conf = json.loads(conf_str)


class Repository(object):
    @txdecorator.cast_count('db.mssql')
    def __init__(self):
        db_conf = _conf.get('db_mssql')
        if (db_conf is None):
            log.error('sql配置为空')
            return None
            # raise Exception('sql配置为空')
        self._db_pagewatch = db_conf.get('TxoooSEMPageWatch')
        self._db_mobile = db_conf.get('TxoooMobile')
        self._db_nex = db_conf.get('TxoooNEx')

    @txdecorator.cast_count('db.mssql')
    @txdecorator.decorate_raise
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

    @txdecorator.decorate_raise
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

    @txdecorator.decorate_raise
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

    @txdecorator.decorate_raise
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

    @txdecorator.decorate_raise
    def updateAllItemStatus(self, status, itemids):
        '''
        批量更新item状态
        status: 1监控 0关闭
        '''
        sql = '''
        UPDATE dbo.watch_item SET status = %s WHERE page_url_id IN (%s)
        ''' % (status, ','.join([str(x) for x in itemids]))
        with txdb.TxDataHelper(False, **self._db_pagewatch) as helper:
            result = helper.sql_execute(sql)
            return result == len(itemids)

    @txdecorator.decorate_raise
    def updateItem(self, id, sources_hash, is_change=0):
        '''
        更新状态和hash
        '''
        with txdb.TxDataHelper(False, **self._db_pagewatch) as helper:
            sql = '''
                UPDATE dbo.watch_item SET is_change = %s,sources_hash = %s
                WHERE page_url_id = %s
            '''
            result = helper.sql_execute(sql, (is_change, sources_hash, id))
            return result == 1

    @txdecorator.decorate_raise
    def insertRecord(self, urlid, hashcode, include, rate):
        '''
        添加日志
        '''
        with txdb.TxDataHelper(False, **self._db_pagewatch) as helper:
            sql = '''
                INSERT INTO dbo.watch_record(page_url_id,watch_type,hash_code,watch_time,include_code,change_rate)
                VALUES(%s,1,%s,GETDATE(),%s,%s)
            '''
            result = helper.sql_execute(sql, (urlid, hashcode, include, rate))
            return result == 1


if __name__ == "__main__":
    repository = Repository()
    # account = repository.getAccount(100000000)
    # print(account)
    # settings = repository.getNotifySettings()
    # print(settings)
    # users = repository.getNotifyUsers()
    # print(users)
    # ids = list(range(1, 1000))
    # statusresult = repository.updateAllItemStatus(1, ids)
    # print(statusresult)
    # print(repository.updateItem(1, '', 0))
    # print(repository.insertRecord(1, 'absdsdfsdfsdf', 0, 0.5))
