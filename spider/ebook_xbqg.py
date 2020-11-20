#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-20 12:38:05
LastEditors: iwenli
LastEditTime: 2020-11-20 17:52:06
Description: 新笔趣阁 --  下载章节
'''
__author__ = 'iwenli'

from utils import http, convert, file
from context import context
from repository import Chapter


def init_chapter(book_name, book_id):
    """
    通过书籍信息 下载 章节
    """
    url = 'http://www.xbiquge.la/modules/article/waps.php?searchkey=' + book_name

    # 搜索书籍
    sp = http.get_beautifulsoup(url)
    tag_a = sp.find('a', text=book_name)
    if(tag_a is None):
        return

    # 解析章节
    book_url = tag_a.get('href')
    book_sp = http.get_beautifulsoup(book_url)
    tag_dds = book_sp.find_all('dd')

    chapters = []
    for index, tag in enumerate(tag_dds):
        a = tag.find('a')
        chapter = Chapter(book_id, index + 1, a.string,
                          'http://www.xbiquge.la' + a.get('href'))
        chapters.append(chapter)

    # if(len(chapters) > 0):
    #     context.insert_chapters(chapters)

    return chapters


def downloads(chapters):
    if(chapters is None):
        return
    for chapter in chapters:
        if(chapter.Status == 0):
            # 开始缓存文字
            sp = http.get_beautifulsoup(chapter.Url)
            content = sp.find(id='content')
            if(content is None):
                continue

            ebook_txts = content.text.replace('\xa0\xa0\xa0\xa0', '')
            chapter.WordNums = len(content.text)

            # 写入文件
            file.write_book(
                chapter.BookId, chapter.SerialNums, ebook_txts)


if __name__ == "__main__":
    chapters = init_chapter('斗罗大陆4终极斗罗', 61)
    downloads(chapters)
