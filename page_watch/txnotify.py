# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-05-23 11:39:09
@LastEditors: iwenli
@LastEditTime: 2019-05-28 16:28:26
@Description: 通知相关
'''
__author__ = 'iwenli'

import data
import datetime
import wechatpy
import threading
import txlog
import network
import json

repository = data.Repository()
lock = threading.Lock()
log = txlog.TxLog()
dingtalk_agentId = '266367788'  # 微应用 agentid


class NotifyConfig(object):
    '''
    @description: 通知配置类
    @param {type} 
    @return: 
    '''
    __setting_update_time = None  # 缓存更新时间
    __settings = None
    __users = None

    def __init__(self):
        NotifyConfig.__setting_update_time = datetime.datetime.now(
        ) - datetime.timedelta(hours=1)  # 前一小时
        NotifyConfig.__get_notify_date_lock()

    def __get_notify_date_lock():
        '''
        @description: 加锁更新数据 30分钟有效
        '''
        if datetime.datetime.now(
        ) - NotifyConfig.__setting_update_time > datetime.timedelta(
                seconds=60 * 30):
            lock.acquire()
            try:
                log.warning('开始更新Notify配置数据')
                NotifyConfig.__settings = repository.getNotifySettings()
                NotifyConfig.__users = repository.getNotifyUsers()
                NotifyConfig.__setting_update_time = datetime.datetime.now()
                log.warning('Notify配置数据更新完成')
            finally:
                lock.release()

    def _get_settings(self, brand_id):
        NotifyConfig.__get_notify_date_lock()
        return [
            x for x in self.__settings
            if x.get('wx_open') and x.get('brand_id') in [-1, brand_id]
        ]

    def _get_users(self, setting_id, type=1):
        '''
        @description:获取配置下数据
        @param {type} 1：微信 2：钉钉
        @return: 
        '''
        NotifyConfig.__get_notify_date_lock()
        return [
            x for x in self.__users if x.get('is_open')
            and x.get('setting_id') == setting_id and x.get('type') == type
        ]


class NotifyBase(object):
    '''通知基类'''
    __config = NotifyConfig()  # 通知配置

    def __init__(self, *args, **kwargs):
        if NotifyBase.__config is None:
            NotifyBase.__config = NotifyConfig()

    def _get_settings(self, brand_id):
        return NotifyBase.__config._get_settings(brand_id)

    def _get_users(self, setting_id, type=1):
        return NotifyBase.__config._get_users(setting_id, type)

    def send(self, item, **d):
        '''
        通用通知
        '''
        raise NotImplementedError()

    def send_error(self, item, error):
        '''
        异常通知
        '''
        raise NotImplementedError()


class DingTalkNotify(NotifyBase):
    '''钉钉通知'''
    __access_token = None

    def __get_access_token_lock():
        lock.acquire()
        try:
            log.warning('开始更新钉钉access_token')
            access_token_str = network.dingtalk_access_token(dingtalk_agentId)
            log.warning(access_token_str)
            if access_token_str is None:
                log.warning('钉钉access_token更新失败 %s' % access_token_str)
            else:
                access_token = json.loads(access_token_str)
                access_token['access_token_time'] = datetime.datetime.now()
                DingTalkNotify.__access_token = access_token
                log.warning('钉钉access_token更新完成')
        finally:
            lock.release()  # 释放

    def _get_access_token():
        '''
        获取钉钉access_token
        '''
        if DingTalkNotify.__access_token is None:
            DingTalkNotify.__get_access_token_lock()
        elif (datetime.datetime.now() -
              DingTalkNotify.__access_token.get('access_token_time') >
              datetime.timedelta(seconds=7000)):
            # token超时
            DingTalkNotify.__get_access_token_lock()
        return DingTalkNotify.__access_token.get('access_token')

    def _get_template_date(self, item, type=1, **kw):
        '''
        获取消息模板
        type = 1 link消息
        '''
        return {
            "msgtype": "link",
            "link": {
                "messageUrl":
                'http://pagewatch.txooo.com/detail.html?id=%s' %
                item.get('page_url_id', ''),
                "picUrl":
                "http://58.83.148.50/2019/05/27/8c3b710e2ed209e240b3d50211f841cf.png",
                "title":
                '[页面监控]' + kw.get('title', ''),
                "text":
                kw.get('content', '')
            }
        }

    def send(self, item, **kw):
        '''
        通用通知
        '''
        access_token = DingTalkNotify._get_access_token()
        bid = item.get('brand_id', 0)
        settings = self._get_settings(bid)
        for setting in settings:
            userid_list = [
                x.get('wx_openid')
                for x in self._get_users(setting.get('id'), 2)
            ]
            msg = self._get_template_date(item, 1, **kw)
            result = network.dingtalk_msg_sendasync(access_token,
                                                    dingtalk_agentId, msg,
                                                    userid_list, [], False)
            log.debug(result)

    def send_error(self, item, error):
        '''
        异常通知
        '''
        userid_list = ['022925500024360016', '122808586039813770']
        kw = {
            'title': '请求异常',
            'content': '[%s]%s' % (error, item.get('page_url'))
        }
        access_token = DingTalkNotify._get_access_token()
        msg = self._get_template_date(item, 1, **kw)
        return network.dingtalk_msg_sendasync(access_token, dingtalk_agentId,
                                              msg, userid_list, [], False)


class WechatNotify(NotifyBase):
    '''微信通知'''
    __client_dick = dict()  # 账户wechatpy客户端字典 {10000000:(account,object))}

    def __get_client_lock(account_id):
        lock.acquire()
        try:
            log.warning('开始更新[%s]账户数据' % account_id)
            _account = repository.getAccount(account_id)
            _client = wechatpy.WeChatClient(
                _account.get('app_id'),
                _account.get('app_secret'),
                access_token=_account.get('access_token'))
            _ac = (_account, _client)
            WechatNotify.__client_dick[account_id] = _ac
            log.warning('[%s]账户数据更新完成' % account_id)
        finally:
            lock.release()  # 释放

    def _get_client(account_id):
        '''
        获取wechatpy客户端对象  内部维护access_token
        '''
        ac = WechatNotify.__client_dick.get(account_id)
        if ac is None:
            WechatNotify.__get_client_lock(account_id)
        elif (datetime.datetime.now() - ac[0].get('access_token_time') >
              datetime.timedelta(seconds=7000)):
            # token超时
            WechatNotify.__get_client_lock(account_id)
        return WechatNotify.__client_dick.get(account_id)[1]

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
            client = WechatNotify._get_client(setting.get('wx_account_id'))
            users = self._get_users(setting.get('id'))
            for user in users:
                client.message.send_template(
                    user.get('wx_openid'),
                    template_id=setting.get('wx_template_id'),
                    url=item.get('page_url'),
                    data=self._get_template_date(**kw))

    def send_error(self, item, error):
        '''
        异常通知
        '''
        users = [
            'oa2OAjmXfQAEAkn0f81RL6RsJEOU', 'oa2OAjriOKl7kWu-rc4m5si77-9A'
        ]
        template_id = 'DVQvh9emcFE8qlQZzfN3TbTe0dSn-3ggn-V9HvDOb_s'
        d = {
            'title': '请求异常',
            'content': '[%s]%s' % (error, item.get('page_url'))
        }
        client = WechatNotify._get_client(100000000)
        for user in users:
            client.message.send_template(user,
                                         template_id=template_id,
                                         url=item.get('page_url'),
                                         data=self._get_template_date(**d))


wechatNotify = WechatNotify()
dingTalkNotify = DingTalkNotify()


def send_4(item):
    '''
    404状态发送通知
    '''
    d = {
        'title': '页面404通知',
        'content': '%s\n此页面无法正常访问，请尽快处理' % item.get('page_url')
    }
    wechatNotify.send(item, **d)
    dingTalkNotify.send(item, **d)


def send_3(item):
    '''
    3xx状态发送通知
    '''
    d = {
        'title': '页面重定向通知',
        'content': '%s\n此页面已重定向到其他路径，请尽快处理' % item.get('page_url')
    }
    wechatNotify.send(item, **d)
    dingTalkNotify.send(item, **d)


def send_error(item, error):
    '''
    异常通知
    '''
    wechatNotify.send_error(item, error)
    dingTalkNotify.send_error(item, error)


def send(item, **kw):
    '''
    通用通知
    '''
    wechatNotify.send(item, **kw)
    dingTalkNotify.send(item, **kw)


if __name__ == '__main__':
    # a1 = WechatNotify._get_client(100000000)
    # a2 = WechatNotify._get_client(100000000)
    # print(a1)
    # print(a2)
    # WechatNotify.send({
    #     'brand_id': 500325,
    #     'url': 'http://www.baidu.com'
    # }, **{
    #     'title': '页面重定向通知',
    #     'content': '这里是要发送的通知消息'
    # })
    # dingtalk_client = DingTalkNotify()
    # print(
    #     dingtalk_client.send(
    #         {
    #             'brand_id': 1,
    #             'page_url': 'http://www.baidu.com'
    #         }, **{
    #             'title': '页面重定向通知',
    #             'content': '这里是要发送的通知消息'
    #         }))
    # send_error({'brand_id': 1, 'page_url': 'https://www.txooo.com'}, 'AOP异常')
    send_4({
        'page_url_id': 1,
        'brand_id': 1,
        'page_url': 'http://www.txooo.com'
    })
