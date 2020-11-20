#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-19 16:31:51
LastEditors: iwenli
LastEditTime: 2020-11-20 16:46:45
Description: 爬虫上下文
'''
__author__ = 'iwenli'

from repository import Db  # , Book, Category, Chapter


class Context(object):
    """
    爬虫上下文
    """
    books = Db().get_books_cache()
    categories = Db().get_categories()
    users = Db().get_users()

    def __init__(self):
        pass

    def filter_exists_book(self, book):
        """
        是否存在书籍
        """
        try:
            for item in self.books:
                if(item == book):
                    book.Id = item.Id
                    book.AddTime = item.AddTime
                    print('存在书籍' + str(item))
                    return True
        except Exception as ex:
            print(ex)
        return False

    def insert_book(self, book):
        if(self.filter_exists_book(book) is False):
            try:
                Db().insert(book)
                self.books.append(book)
            except Exception as ex:
                print(ex)
        else:
            pass

    def filter_exists_category(self, category):
        """
        是否存在分类
        """
        try:
            for item in self.categories:
                if(item == category):
                    category.Id = item.Id
                    category.AddTime = item.AddTime
                    print('存在分类' + str(item))
                    return True
        except Exception as ex:
            print(ex)
        return False

    def insert_category(self, category):
        if(self.filter_exists_category(category) is False):
            try:
                Db().insert(category)
                self.categories.append(category)
            except Exception as ex:
                print(ex)
        else:
            pass

    def insert_chapters(self, chapters):
        try:
            Db().insert_all(chapters)
        except Exception as ex:
            print(ex)


# 全局上下文
context = Context()

if __name__ == "__main__":
    context = Context()
    context1 = Context()
    # for item in Context.users:
    #     print(item)

    for item in context.users:
        print(item)
