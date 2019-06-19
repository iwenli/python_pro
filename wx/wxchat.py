# !/usr/bin/python
# -*-coding: UTF-8 -*-
'''
@Author: iwenli
@License: Copyright © 2019 txooo.com Inc. All rights reserved.
@Github: https://github.com/iwenli
@Date: 2019-06-19 12:28:15
@LastEditors: iwenli
@LastEditTime: 2019-06-19 14:12:51
@Description: ...
'''

__author__ = 'iwenli'

import itchat
import csv
import os
import datetime


def getDir(path, root=None):
    if (root is None):
        root = os.path.dirname(__file__)
    dir = os.path.join(root, path)
    if not os.path.isdir(dir):
        os.mkdir(dir)
    return dir


def getroom_message(n):
    # 获取群的username，对群成员进行分析需要用到
    itchat.dump_login_status()  # 显示所有的群聊信息，默认是返回保存到通讯录中的群聊
    list = itchat.search_chatrooms(name=n)
    if list is not None:
        return list[0]['UserName']


def getchatrooms():
    # 获取群聊列表
    list = itchat.get_chatrooms()
    # print('列表',roomslist)
    return [room['NickName'] for room in list]


def getChatFriends(chatName):
    chatRoom = itchat.update_chatroom(getroom_message(chatName),
                                      detailedMember=True)
    list = chatRoom['MemberList']
    print('群[%s]下载好友：%d 个' % (chatName, len(list)))
    return [(chatName, item['NickName'], item['RemarkName'], item['Province'],
             item['HeadImgUrl']) for item in list]


def getFriends():
    # 获取好友列表
    list = itchat.get_friends()
    # print('列表',roomslist)
    return [(room['NickName'], room['RemarkName'], room['City'],
             room['HeadImgUrl']) for room in list]


if __name__ == "__main__":
    dir = getDir("_file")

    itchat.auto_login()
    # tchat.auto_login(hotReload=True)
    print("程序开始：", datetime.datetime.now())
    mine = itchat.search_friends()
    dir = getDir(mine['NickName'], dir)
    print('当前输出目录：' + dir)

    friendslist = getFriends()
    print('好友总数：%d' % len(friendslist))
    filePath = os.path.join(dir, '好友列表.csv')
    with open(filePath, 'w', encoding='utf-8') as f:
        firedsCsv = csv.writer(f)
        firedsCsv.writerow(['昵称', '备注', '城市', '头像'])
        firedsCsv.writerows(friendslist)

    roomslist = getchatrooms()
    print('群总数：%d' % len(roomslist))

    filePath1 = os.path.join(dir, '群友列表.csv')
    with open(filePath1, 'w', encoding='utf-8') as f:
        firedsCsv = csv.writer(f)
        firedsCsv.writerow(['群', '昵称', '备注', '城市', '头像'])
        for item in roomslist:
            # roomFriendsList += getChatFriends(item)
            firedsCsv.writerows(getChatFriends(item))

    print("程序结束：", datetime.datetime.now())
