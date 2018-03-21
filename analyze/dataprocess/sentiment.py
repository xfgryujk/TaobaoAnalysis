# -*- coding: utf-8 -*-

"""
创建训练情感模型用的数据集
"""

import codecs
from random import choices

from hanziconv import HanziConv
from jieba import cut

from utils.database import session, Review, Rate
from utils.path import TRAIN_DIR

TRAIN_POS_PATH = TRAIN_DIR + '/sentiment_train_pos.txt'
TRAIN_NEG_PATH = TRAIN_DIR + '/sentiment_train_neg.txt'
TEST_POS_PATH = TRAIN_DIR + '/sentiment_test_pos.txt'
TEST_NEG_PATH = TRAIN_DIR + '/sentiment_test_neg.txt'


def chinese_tokenizer(documents):
    """
    把中文文本转为词序列
    繁体转简体、英文转小写
    """

    for document in documents:
        text = HanziConv.toSimplified(document)
        text = text.lower()
        yield list(cut(text))


def create_train_test(train_pos_path=TRAIN_POS_PATH, train_neg_path=TRAIN_NEG_PATH,
                      test_pos_path=TEST_POS_PATH, test_neg_path=TEST_NEG_PATH):
    """
    用数据库中所有非默认评论创建训练和测试样本，保证正负样本数一样
    """

    pos, neg = [], []
    for content, rate in Review.filter_default(
        session.query(Review.content, Review.rate)
        .filter(Review.content != '')
    ):
        if Rate(rate).is_good:
            pos.append(content)
        else:
            neg.append(content)

    size = min(len(pos), len(neg))
    size_train = int(size * 0.8)
    pos = choices(pos, k=size)
    neg = choices(neg, k=size)

    for data, path in ((pos[:size_train], train_pos_path),
                       (neg[:size_train], train_neg_path),
                       (pos[size_train:], test_pos_path),
                       (neg[size_train:], test_neg_path)):
        with codecs.open(path, 'w', 'utf-8') as file:
            file.writelines(data)


if __name__ == '__main__':
    create_train_test()
