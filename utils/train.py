# -*- coding: utf-8 -*-

import codecs
from os.path import exists
from random import choices

from jieba import cut

from utils.database import session, Review, Rate
from utils.path import DATA_DIR

CORPUS_POS_PATH = DATA_DIR + '/corpus_pos.txt'
CORPUS_NEG_PATH = DATA_DIR + '/corpus_neg.txt'
TRAIN_POS_PATH = DATA_DIR + '/train_pos.txt'
TRAIN_NEG_PATH = DATA_DIR + '/train_neg.txt'
TEST_POS_PATH = DATA_DIR + '/test_pos.txt'
TEST_NEG_PATH = DATA_DIR + '/test_neg.txt'


def create_corpus(pos_path=CORPUS_POS_PATH, neg_path=CORPUS_NEG_PATH):
    """
    用数据库中所有非默认评论创建语料库
    每行一条评论，分词以空格分割
    """

    # 防止手贱
    if exists(pos_path) or exists(neg_path):
        if input('确定要覆盖已有的语料库则输入y：') != 'y':
            return

    with codecs.open(pos_path, 'w', 'utf-8') as pos_file:
        with codecs.open(neg_path, 'w', 'utf-8') as neg_file:
            for index, result in enumerate(Review.filter_default(
                    session.query(Review.content, Review.rate)
                    .filter(Review.content != '')
                    )):
                content, rate = result
                file = pos_file if rate == Rate.good else neg_file
                file.write(' '.join(cut(content)))
                file.write('\n')

                if index % 100 == 0:
                    print(index)


def create_train_test(pos_path=CORPUS_POS_PATH, neg_path=CORPUS_NEG_PATH,
                      train_pos_path=TRAIN_POS_PATH, train_neg_path=TRAIN_NEG_PATH,
                      test_pos_path=TEST_POS_PATH, test_neg_path=TEST_NEG_PATH):
    """
    用语料库创建训练和测试样本，保证正负样本数一样
    """

    with codecs.open(pos_path, 'r', 'utf-8') as file:
        pos = file.readlines()
    with codecs.open(neg_path, 'r', 'utf-8') as file:
        neg = file.readlines()
    size = min(len(pos), len(neg))
    size_train = int(size * 0.8)
    pos = choices(pos, k=size)
    neg = choices(neg, k=size)

    with codecs.open(train_pos_path, 'w', 'utf-8') as file:
        file.writelines(pos[:size_train])
    with codecs.open(train_neg_path, 'w', 'utf-8') as file:
        file.writelines(neg[:size_train])
    with codecs.open(test_pos_path, 'w', 'utf-8') as file:
        file.writelines(pos[size_train:])
    with codecs.open(test_neg_path, 'w', 'utf-8') as file:
        file.writelines(neg[size_train:])


if __name__ == '__main__':
    create_corpus()
    create_train_test()
