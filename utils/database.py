# -*- coding: utf-8 -*-

from sqlalchemy import (create_engine, Column, ForeignKey, Integer, String,
                        DateTime)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from enum import Enum

from .path import DATABASE_PATH

Base = declarative_base()


class Seller(Base):

    __tablename__ = 'sellers'

    id    = Column(Integer, primary_key=True)
    age   = Column(String)      # 店龄，应该都是整数
    shops = relationship('Shop', back_populates='seller')  # 商店


class Shop(Base):

    __tablename__ = 'shops'

    id        = Column(Integer, primary_key=True)
    url       = Column(String)      # 商店URL
    seller_id = Column(Integer, ForeignKey('sellers.id'))       # 卖家ID
    seller    = relationship('Seller', back_populates='shops')  # 卖家
    items     = relationship('Item', back_populates='shop')     # 商品


class Item(Base):

    __tablename__ = 'items'

    id      = Column(Integer, primary_key=True)
    title   = Column(String)      # 商品标题
    shop_id = Column(Integer, ForeignKey('shops.id'))        # 商店ID
    shop    = relationship('Shop', back_populates='items')   # 商店
    reviews = relationship('Review', back_populates='item')  # 评论


class Rate(str, Enum):
    default = '-2'      # 15天内买家未作出评价
    bad     = '-1'      # 差评
    middle  = '0'       # 中评
    good    = '1'       # 好评


class Review(Base):

    __tablename__ = 'reviews'

    id        = Column(Integer, primary_key=True)
    raw       = Column(String)       # 原始JSON数据
    item_id   = Column(Integer, ForeignKey('items.id'))         # 商品ID
    item      = relationship('Item', back_populates='reviews')  # 商品
    rate      = Column(String)       # 评价，取值见Rate
    content   = Column(String)       # 评论内容
    date      = Column(DateTime)     # 评论时间，精确到分，可能为空
    appends   = Column(String)       # 追加评论，每行一条
    user_rank = Column(Integer)      # 用户信用等级，250分以内的积分用红心来表示...，可能为空

    DEFAULT_CONTENTS = (
        '此用户没有填写评价。',
        '15天内买家未作出评价',
        '评价方未及时做出评价,系统默认好评!',
        '系统默认评论',
    )

    def is_default(self):
        return self.content in self.DEFAULT_CONTENTS

    @classmethod
    def filter_default(cls, query):
        for default in cls.DEFAULT_CONTENTS:
            query = query.filter(cls.content != default)
        return query


engine = create_engine('sqlite:///' + DATABASE_PATH)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
