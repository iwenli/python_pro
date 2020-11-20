#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 txooo.com Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-18 14:29:28
LastEditors: iwenli
LastEditTime: 2020-11-20 16:45:27
Description: 起点 获取分类&&书籍信息
'''
__author__ = 'iwenli'


from repository import Book, Category  # , Chapter
from context import context
import json
from urllib import parse
from utils import http


def init_categories():
    base = 'https://m.qidian.com'  # 主域
    raw_urls = [(1, 'https://m.qidian.com/category/male'),
                (2, 'https://m.qidian.com/category/female')]
    for url_item in raw_urls:
        sex = url_item[0]
        url = url_item[1]

        sp = http.get_beautifulsoup(url)
        categoryTags = sp.select('.sort-li')
        for tag in categoryTags:
            href = tag.select('.sort-li-header')[0].get('href')
            val = tag.select('.module-title')[0].string
            category = Category(sex, val, base + href, 0)
            context.insert_category(category)

            subCategoryTag = tag.find(class_='sort-li-detail').find_all('a')
            for subTag in subCategoryTag:
                subEntity = Category(sex, subTag.string,
                                     base + subTag.get('href'), category.Id)
                context.insert_category(subEntity)


def get_books_by_category(category):
    """
    根据分类 获取 book
    """
    # 转换分类
    id = category.Id
    subId = 0
    if(category.ParentId > 0):
        id = category.ParentId
        subId = category.Id

    url = category.Url
    category_base = 'https://m.qidian.com/majax/category/list'
    csrfToken = http.get_cookie(url, '_csrfToken')

    query = parse.urlsplit(url).query
    # ! https://m.qidian.com/majax/category/list?_csrfToken=5vqRK0lpRXFzdGzvzUXzw310CmQuv9N9Z7Z9KMC6&gender=male&pageNum=2&catId=4&subCatId=6
    for i in range(5):
        page_num = i + 1
        page_url = f'{category_base}?_csrfToken={csrfToken}&{query}&pageNum={page_num}'

        resp = http.get_text(page_url)
        books_json = json.loads(resp).get('data').get('records')
        for book in books_json:
            # name, author, desc, id, subId, rate, cover, status, wordNums
            bid = book.get('bid')
            entity = Book(book.get('bName'), book.get('bAuth'), book.get('desc'), id, subId,
                          0, f'https://bookcover.yuewen.com/qdbimg/349573/{bid}/150',
                          book.get('state'), book.get('cnt'))
            context.insert_book(entity)


def crawl_book():
    categories = context.categories
    for item in categories[::-1]:
        get_books_by_category(item)


if __name__ == "__main__":
    # init_categories()
    crawl_book()
