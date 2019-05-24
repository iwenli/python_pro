# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-22 09:46:16
@LastEditors: iwenli
@LastEditTime: 2019-05-22 17:34:20
@Description: 数据库
'''

__author__ = 'iwenli'

import pymssql
import DBUtils.PooledDB  # import PooledDB, SharedDBConnection
import DBUtils.PersistentDB  # import PersistentDB, PersistentDBError, NotSupportedError


class TxDataHelper(object):
    __pool = None  # 连接池对象
    _conn = None
    _cursor = None
    _conf = None

    def __init__(self, is_mult_thread, **conf):
        self._conf = conf
        self._conn = TxDataHelper.__get_conn(is_mult_thread, **conf)
        as_dict = True
        if conf.get('as_dict') is not None:
            as_dict = conf.get('as_dict')
        self._cursor = self._conn.cursor(as_dict=as_dict)

    def __get_pool(is_mult_thread, **conf):
        if is_mult_thread:
            poolDB = DBUtils.PooledDB.PooledDB(
                # 指定数据库连接驱动
                creator=pymssql,
                # 连接池允许的最大连接数,0和None表示没有限制
                maxconnections=3,
                # 初始化时,连接池至少创建的空闲连接,0表示不创建
                mincached=2,
                # 连接池中空闲的最多连接数,0和None表示没有限制
                maxcached=5,
                # 连接池中最多共享的连接数量,0和None表示全部共享(其实没什么卵用)
                maxshared=3,
                # 连接池中如果没有可用共享连接后,是否阻塞等待,True表示等等,
                # False表示不等待然后报错
                blocking=True,
                # 开始会话前执行的命令列表
                setsession=[],
                # ping Mysql服务器检查服务是否可用
                ping=0,
                **conf)
        else:
            poolDB = DBUtils.PersistentDB.PersistentDB(
                # 指定数据库连接驱动
                creator=pymssql,
                # 一个连接最大复用次数,0或者None表示没有限制,默认为0
                maxusage=1000,
                **conf)
        return poolDB

    def __get_conn(is_mult_thread, **conf):
        '''
        静态方法，从连接池中取出连接
        '''
        if TxDataHelper.__pool is None:
            __pool = TxDataHelper.__get_pool(is_mult_thread, **conf)
        TxDataHelper.__log('开启数据库%s' % conf['database'])
        return __pool.connection()

    def __close(self):
        '''
        释放连接池资源
        '''
        if self._cursor is not None:
            self._cursor.close()
        if self._conn is not None:
            self._conn.close()
        TxDataHelper.__log('关闭数据库%s' % self._conf['database'])

    def __log(msg):
        '''
        日志
        '''
        print(msg)

    def begin(self):
        '''
        开启事务
        '''
        self._conn.autocommit(0)

    def end(self, option='commit'):
        '''
        结束事务
        '''
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        '''
        释放连接池资源
        '''
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self.__close()

    def sql_execute(self, sql, args=()):
        '''
        执行带参数的sql语句， 返回受影响的行数
        一般执行 insert update delete
        '''
        self._cursor = None
        self._cursor = self._conn.cursor(False)
        if isinstance(args, list):
            self._cursor.executemany(sql, args)
        else:
            self._cursor.execute(sql, args)
        self.end()
        return self._cursor.rowcount

    def sql_getdate(self, sql, as_dict=True, args=()):
        '''
        执行带参数的sql语句， 返回数据
        一般执行 select
        '''
        self._cursor = None
        self._cursor = self._conn.cursor(as_dict)
        self._cursor.execute(sql, args)
        return self._cursor.fetchall()

    def sql_scalar(self, sql, args=()):
        '''
        执行语句，返回结果第一行  第一列
        '''
        self._cursor = None
        self._cursor = self._conn.cursor(False)
        self._cursor.execute(sql, args)
        result = self._cursor.fetchone()
        return result[0] if result is not None else None

    def sp_get_return_value(self, sp_name, args=()):
        '''
        执行存储过程，获得返回值
        '''
        pass

    def sp_getdate(self, sp_name, as_dict=True, args=()):
        '''
        执行存储过程，获得数据集  as_dict = True时select 列必须指定列名
        '''
        result = []
        self._cursor = None
        self._cursor = self._conn.cursor(as_dict)
        self._cursor.callproc(sp_name, args)
        for row in self._cursor._cursor:
            result.append(row)
        return result

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.__close()


# if __name__ == '__main__':
#     import os
#     db_connect_str = os.getenv('PY_BD_MSSQL_PW')  # 环境变量中提取数据库配置字符串
#     if db_connect_str is None:
#         db_connect_str = ''
#     db_connect_params = db_connect_str.split(';')
#     config = {
#         'host': db_connect_params[0],
#         'port': 1433,  # 1433 3306
#         'database': db_connect_params[1],
#         'user': db_connect_params[2],
#         'password': db_connect_params[3]
#     }
#     with TxDataHelper(False, **config) as helper:
#         # select
#         d = helper.sql_getdate(
#             'select id,name,salesrep from persons where id = %s', args=(1, ))
#         print(d)

#         # delete
#         d0 = helper.sql_execute('Delete from persons where id > 99')
#         print(d0)

#         # insert
#         d1 = helper.sql_execute(
#             'insert into persons(id,name,salesrep) values(%s,%s,%s)',
#             [(100, 'wangwu', '99'), (101, 'zhangliu', '99')])
#         print(d1)

#         #  update
#         d2 = helper.sql_execute(
#             'update persons set salesrep=\'\' where id > 99')
#         print(d2)

#         # count
#         d3 = helper.sql_scalar('select count(*) from persons')
#         print(d3)

#         # sp get date
#         d4 = helper.sp_getdate('SP_V1_Wawtch_ZYL_Test', False, args=(1, ))
#         print(d4)
