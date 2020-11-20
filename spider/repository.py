#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-19 10:31:41
LastEditors: iwenli
LastEditTime: 2020-11-20 16:59:21
Description: ...
'''
__author__ = 'iwenli'

# ! https://docs.sqlalchemy.org/en/13/orm/tutorial.html#create-an-instance-of-the-mapped-class
# import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from conf import db_conf

ebook_engine = create_engine(
    db_conf,
    echo=True,  # 当设置为True时会将orm语句转化为sql语句打印，一般debug的时候可用
    pool_size=8,  # 连接池的大小，默认为5个，设置为0时表示连接无限制
    pool_recycle=60 * 30)  # 设置时间以限制数据库多久没连接自动断开

EntityBase = declarative_base()
EBookSession = sessionmaker(bind=ebook_engine)


class Book(EntityBase):
    """
    书籍
    """
    __tablename__ = "Book"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Name = Column(String(200), nullable=True)
    Author = Column(String(50), nullable=True)
    Desc = Column(String(3000), nullable=True)
    CategoryId = Column(Integer, nullable=True)
    SubCategoryId = Column(Integer, nullable=True)
    Rate = Column(Integer, nullable=True)
    Cover = Column(String(100), nullable=True)
    Status = Column(Integer, nullable=True)
    WordNums = Column(BigInteger, nullable=True)
    AddTime = Column(DateTime, nullable=True)

    def __init__(self, name, author, desc, id, subId, rate, cover, status, wordNums):
        '''
        status 状态    0未知    1连载    2完本    3暂停
        '''
        self.Name = name
        self.Author = author
        self.Desc = desc
        self.CategoryId = id
        self.SubCategoryId = subId
        self.Rate = rate
        self.Cover = cover

        if('连载' in status):
            self.Status = 1
        elif('完本' in status):
            self.Status = 2
        elif('暂停' in status):
            self.Status = 3
        else:
            self.Status = 0

        self.AddTime = datetime.datetime.now()

        if('万字' in wordNums):
            self.WordNums = float(wordNums.replace('万字', '')) * 10000
        elif('字' in wordNums):
            self.WordNums = int(wordNums.replace('字', ''))
        else:
            self.WordNums = int(wordNums)

    def __repr__(self):
        return f'<Book {self.Name},{self.Author},{self.Status},{self.WordNums}>'

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.Name == other.Name


class Category(EntityBase):
    """
    分类
    """
    __tablename__ = "Category"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    ParentId = Column(Integer, nullable=True)
    Name = Column(String(50), nullable=True)
    Url = Column(String(200), nullable=True)
    Sex = Column(Integer, nullable=True)
    AddTime = Column(DateTime, nullable=True)

    def __init__(self, sex, name, url, parentId=0):
        self.ParentId = parentId
        self.Name = name
        self.Url = url
        self.Sex = sex
        self.AddTime = datetime.datetime.now()

    def __repr__(self):
        return f'<Category {self.Name},{self.Url}>'

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.Name == other.Name and self.Sex == other.Sex


class Chapter(EntityBase):
    """
    章节
    """
    __tablename__ = "Chapter"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    BookId = Column(BigInteger, nullable=True)
    SerialNums = Column(Integer, nullable=True)
    Name = Column(String(200), nullable=True)
    WordNums = Column(BigInteger, nullable=True)
    Url = Column(String(200), nullable=False)
    Status = Column(BigInteger, nullable=False)
    AddTime = Column(DateTime, nullable=True)

    def __init__(self, bookId, serialNums, name, url):
        self.BookId = bookId
        self.SerialNums = serialNums
        self.Name = name
        self.AddTime = datetime.datetime.now()
        self.Url = url
        self.Status = 0
        self.WordNums = 0

    def __repr__(self):
        return f'<Chapter [{self.Status}]{self.Name},{self.BookId},{self.SerialNums},{self.Url}>'

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.BookId == other.BookId and self.SerialNums == other.SerialNums


class User(EntityBase):
    """
    用户 测试
    """
    __tablename__ = "User"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Name = Column(String(20), nullable=True)
    Sex = Column(String(1), nullable=True)
    AddTime = Column(DateTime, nullable=True)

    def __init__(self, name, sex):
        self.Name = name
        self.Sex = sex
        self.AddTime = datetime.datetime.now()

    def __repr__(self):
        return f'<User {self.Id},{self.Name},{self.Sex}>'


class Db(object):
    """
    数据交互
    """
    __ebook_sesson = None

    def create_table():
        EntityBase.metadata.create_all(ebook_engine)

    def __init__(self):
        self.__ebook_sesson = EBookSession()

    def insert(self, entity):
        self.__ebook_sesson.add(entity)
        self.__ebook_sesson.commit()

    def insert_all(self, list):
        self.__ebook_sesson.add_all(list)
        self.__ebook_sesson.commit()

    def get_books_cache(self):
        '''
        获取书籍缓存[书籍部分信息]
        '''
        res = self.__ebook_sesson.query(Book.Id, Book.AddTime,
                                        Book.Name, Book.CategoryId, Book.SubCategoryId, Book.Author).all()
        return res

    def get_categories(self):
        res = self.__ebook_sesson.query(Category).all()
        return res

    def get_chapters(self):
        res = self.__ebook_sesson.query(Chapter).all()
        return res

    def get_users(self):
        res = self.__ebook_sesson.query(User).all()
        return res


if __name__ == "__main__":
    # db1 = Db()
    # users = [User('张三', '男'), User('李四', '男'), User('王五', '男')]
    # db1.insert_all(users)

    # db_users = Db().get_users()
    # user1 = User('赵六', '男')

    # db_users.append(user1)
    # db1.insert(user1)

    # for item in db_users:
    #     print(item)

    db = Db()
    session = EBookSession()
    books = session.query(Book.Id, Book.AddTime,
                          Book.Name, Book.Author).offset(1).limit(10).all()
    book = Book('我在玄幻世界冒充天机神算', '残剑', '', 0, 0, 0, '', '完本', '1015字')
    for item in books:
        if(item == book):
            print(item)
