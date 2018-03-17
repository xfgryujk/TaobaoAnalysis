# -*- coding: utf-8 -*-

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


if __name__ == '__main__':
    for item in session.query(Item):
        print(get_item_quality(item), item.title)
