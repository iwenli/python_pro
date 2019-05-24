# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-23 11:39:09
@LastEditors: iwenli
@LastEditTime: 2019-05-23 15:50:18
@Description: 通知相关
'''
__author__ = 'iwenli'

import data
import datetime
import wechatpy
import threading

repository = data.Repository()
lock = threading.Lock()


class NotifyBase(object):
    '''通知基类 暂不启用'''

    def send_4(self, item):
        '''
        404状态发送通知
        '''
        raise NotImplementedError()

    def send_3(self, item):
        '''
        403状态发送通知
        '''
        raise NotImplementedError()

    def send(self, item):
        '''
        状态通知
        '''
        raise NotImplementedError()


class DingTalkNotify(NotifyBase):
    '''钉钉通知'''
    pass


class WxNotify(NotifyBase):
    '''微信通知'''
    __client_dick = dict()  # 账户wechatpy客户端字典 {10000000:(account,object))}

    __setting_update_time = datetime.datetime.now()  # 缓存更新时间
    __settings = repository.getNotifySettings()
    __users = repository.getNotifyUsers()

    def __get_client_lock(account_id):
        lock.acquire()
        try:
            _account = repository.getAccount(account_id)
            _client = wechatpy.WeChatClient(
                _account.get('app_id'),
                _account.get('app_secret'),
                access_token=_account.get('access_token'))
            _ac = (_account, _client)
            WxNotify.__client_dick[account_id] = _ac
        finally:
            lock.release()  # 释放

    def _get_client(account_id):
        '''
        获取wechatpy客户端对象  内部维护access_token
        '''
        ac = WxNotify.__client_dick.get(account_id)
        if ac is None:
            WxNotify.__get_client_lock(account_id)
        elif (datetime.datetime.now() - ac[0].get('access_token_time') >
              datetime.timedelta(seconds=7000)):
            # token超时
            WxNotify.__get_client_lock(account_id)
        return WxNotify.__client_dick.get(account_id)[1]

    def _get_settings(self, brand_id):
        return [
            x for x in self.__settings
            if x.get('wx_open') and x.get('brand_id') in [-1, brand_id]
        ]

    def _get_users(self, setting_id):
        return [
            x for x in self.__users
            if x.get('is_open') and x.get('setting_id') == setting_id
        ]

    def _get_template_date(self, **kw):
        return {
            'first': {
                'value': '[页面监控]' + kw.get('title', ''),
                'color': '#173177'
            },
            'keyword1': {
                'value': kw.get('service_name', '页面监控服务'),
                'color': '#173177'
            },
            'keyword2': {
                'value': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'color': '#173177'
            },
            'keyword3': {
                'value': kw.get('content', ''),
                'color': '#173177'
            },
            'remark': {
                'value': '\n点击查看当前页面',
                'color': '#173177'
            }
        }

    def send(self, item, **kw):
        '''
        通用通知
        '''
        bid = item.get('brand_id', 0)
        settings = self._get_settings(bid)
        for setting in settings:
            client = WxNotify._get_client(setting.get('wx_account_id'))
            users = self._get_users(setting.get('id'))
            for user in users:
                client.message.send_template(
                    user.get('wx_openid'),
                    template_id=setting.get('wx_template_id'),
                    url=item.get('page_url'),
                    data=self._get_template_date(**kw))

    def send_4(self, item):
        '''
        404状态发送通知
        '''
        d = {
            'title': '页面404通知',
            'content': '%s\n此页面无法正常访问，请尽快处理' % item.get('page_url')
        }
        self.send(item, **d)

    def send_3(self, item):
        '''
        403状态发送通知
        '''
        d = {
            'title': '页面重定向通知',
            'content': '%s\n此页面已重定向到其他路径，请尽快处理' % item.get('page_url')
        }
        self.send(item, **d)

    def send_error(self, item, error):
        '''
        异常通知
        '''
        users = [
            # 'oa2OAjmXfQAEAkn0f81RL6RsJEOU',
            'oa2OAjriOKl7kWu-rc4m5si77-9A'
        ]
        template_id = 'DVQvh9emcFE8qlQZzfN3TbTe0dSn-3ggn-V9HvDOb_s'
        d = {'title': '请求异常', 'content': error + item.get('page_url')}
        client = WxNotify._get_client(100000000)
        for user in users:
            client.message.send_template(user,
                                         template_id=template_id,
                                         url=item.get('page_url'),
                                         data=self._get_template_date(**d))


wxnotify = WxNotify()


def send_4(item):
    '''
    4xx状态发送通知
    '''
    wxnotify.send_4(item)


def send_3(item):
    '''
    3xx状态发送通知
    '''
    wxnotify.send_3(item)


def send_error(item, error):
    '''
    异常通知
    '''
    wxnotify.send_error(item, error)


def send(item, **kw):
    '''
    通用通知
    '''
    wxnotify.send(item, **kw)


if __name__ == '__main__':
    # a1 = WxNotify._get_client(100000000)
    # a2 = WxNotify._get_client(100000000)
    # print(a1)
    # print(a2)
    wxnotify.send({
        'brand_id': 500325,
        'url': 'http://www.baidu.com'
    }, **{
        'title': '页面重定向通知',
        'content': '这里是要发送的通知消息'
    })
