# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-21 14:27:45
@LastEditors: iwenli
@LastEditTime: 2019-05-26 08:45:37
@Description: http请求
'''
__author__ = 'iwenli'

import urllib3
import txlog
import txdecorator
import txnotify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 取消ssl验证
timeout = 5  # 超时时间  5 秒
httpPool = urllib3.PoolManager(timeout=timeout,
                               num_pools=5,
                               headers={'User-Agent': 'txooo/page_watch'})
log = txlog.TxLog()
txlog.TxLog()


@txdecorator.cast_count('http')
def gethtml(item):
    url = item['page_url']
    resp = None
    html = ''
    try:
        resp = httpPool.request('GET', url, redirect=False,
                                retries=10)  # 允许重定向 请求失败重试10次
        if (resp.status == 200):
            # log.info('[请求完成] %s' % url)
            html = resp.data.decode('utf-8-sig')
        elif (resp.status == 404):
            # pass
            txnotify.send_4(item)
            # 404通知
        elif (resp.status >= 300 and resp.status < 400):  # 3xx
            # pass
            txnotify.send_3(item)
            # 3xx重定向严重通知
        else:
            txnotify.send_error(item, '[请求失败] [状态:%s]' % (resp.status))
            log.critical('[请求失败] [状态:%s]-%s' % (resp.status, url))
    except UnicodeDecodeError:
        html = resp.data.decode('gb2312')
    except urllib3.exceptions.MaxRetryError as ex:
        log.error('[重试10次依旧无法请求到结果] %s  \n %s' % (url, str(ex)))
        txnotify.send_error(item, '[重试10次依旧无法请求到结果] %s' % str(ex))
    except Exception as ex:
        log.error('[请求异常] %s  \n %s' % (url, str(ex)))
        txnotify.send_error(item, '[请求异常] %s' % (str(ex), ))
    finally:
        return html


if __name__ == "__main__":
    url = 'https://sjh.baidu.com/site/282848.cn/c1340db8-aa0c-4263-aff0-390c4b4e3591'
    resp = None
    html = None
    try:
        resp = httpPool.request('GET', url, redirect=False,
                                retries=10)  # 允许重定向 请求失败重试10次
        if (resp.status == 200):
            # log.info('[请求完成] %s' % url)
            html = resp.data.decode('utf-8-sig')
        elif (resp.status == 404):
            pass
            # txnotify.send_4(item)
            # 404通知
        elif (resp.status >= 300 and resp.status < 400):  # 3xx
            pass
            # txnotify.send_3(item)
            # 3xx重定向严重通知
        else:
            log.critical('[请求失败] [状态:%s]-%s' % (resp.status, url))
    except UnicodeDecodeError:
        html = resp.data.decode('gb2312')
    except Exception as ex:
        log.error('[请求异常] %s  \n %s' % (url, str(ex)))
    finally:
        print(html)
