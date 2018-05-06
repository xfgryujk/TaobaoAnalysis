# -*- coding: utf-8 -*-

"""
计算商品质量
"""

import numpy as np

from utils.database import session, Item

sentiment_model = usefulness_model = None


def get_item_quality(item):
    """
    取商品质量，取值范围(0, 1)，无评论则返回None
    """

    if item.quality is not None:
        return item.quality

    global sentiment_model, usefulness_model
    if sentiment_model is None or usefulness_model is None:
        from analyze.models.sentiment import SentimentModel
        from analyze.models.usefulness import UsefulnessModel
        sentiment_model = SentimentModel()
        usefulness_model = UsefulnessModel()

    sentiments = sentiment_model.predict_reviews(item.reviews)
    usefulness = usefulness_model.predict_reviews(item.reviews)
    if not usefulness:  # 无评论
        return None
    # 情感值用有用概率加权平均
    item.quality = (sum(s * u for s, u in zip(sentiments, usefulness))
                    / sum(usefulness))
    session.commit()

    return item.quality


def get_abnormal_items(items):
    """
    取质量异常的商品，质量不在2σ之内则认为是异常的
    """

    items = [item for item in items if len(item.reviews) >= 20]
    qualities = list(map(get_item_quality, items))
    mean, std = np.mean(qualities), np.std(qualities)
    lower_bound, upper_bound = mean - 2 * std, mean + 2 * std

    return [item for item, quality in zip(items, qualities)
            if quality < lower_bound or quality > upper_bound]


if __name__ == '__main__':
    items = get_abnormal_items(Item.with_reviews_more_than(20))
    items.sort(key=lambda item: item.quality)
    for item in items:
        print(get_item_quality(item), item.shop.seller_id, item.id, item.title, sep=',')
