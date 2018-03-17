# -*- coding: utf-8 -*-

"""
计算评论有用的概率
"""

import pickle
from os.path import exists

from tensorflow import reset_default_graph
from tflearn import input_data, fully_connected, regression, DNN

from analyze.dataprocess.usefulness import (TRAIN_POS_PATH, TRAIN_NEG_PATH,
                                            TEST_POS_PATH, TEST_NEG_PATH, get_diffs)
from utils.path import MODELS_DIR

CLASSIFIER_MODEL_PATH = MODELS_DIR + '/usefulness'
# 隐藏层神经元数
N_HIDDEN_UNITS = 32


class UsefulnessModel:
    """
    输入用户信用等级、评论长度、是否有图片、是否有追评、评论数量差分，输出有用、没用的概率
    """

    def __init__(self):
        self._model = self._create_classifier()
        if exists(CLASSIFIER_MODEL_PATH + '.meta'):
            self._model.load(CLASSIFIER_MODEL_PATH, True)

    @staticmethod
    def _create_classifier():
        reset_default_graph()
        net = input_data([None, 5])
        net = fully_connected(net, N_HIDDEN_UNITS, bias=True, activation='tanh')
        net = fully_connected(net, 2, activation='softmax')
        net = regression(net, optimizer='adam', learning_rate=0.001,
                         loss='categorical_crossentropy')
        return DNN(net)

    @staticmethod
    def _preprocess(sample):
        """
        预处理，归一化
        """

        return [
            (sample[0] - 500) / 1000,
            (sample[1] - 20) / 50,
            1 if sample[2] else -1,
            1 if sample[3] else -1,
            sample[4] / 10
        ]

    def _read_train_samples(self, pos_path, neg_path):
        """
        读样本文件，返回X为处理后的样本数组，Y为分类概率数组
        """

        x, y = [], []
        for path, y_ in ((pos_path, [1., 0.]),
                         (neg_path, [0., 1.])):
            with open(path, 'rb') as file:
                x += pickle.load(file)
            y += [y_] * len(x)

        x = list(map(self._preprocess, x))

        return x, y

    def train(self):
        """
        训练分类器
        需要训练、测试样本
        """

        train_x, train_y = self._read_train_samples(TRAIN_POS_PATH, TRAIN_NEG_PATH)
        test_x, test_y = self._read_train_samples(TEST_POS_PATH, TEST_NEG_PATH)

        self._model.fit(train_x, train_y, validation_set=(test_x, test_y),
                        n_epoch=40, shuffle=True, show_metric=True,
                        snapshot_epoch=True)

        self._model.save(CLASSIFIER_MODEL_PATH)

    def predict(self, user_rank, content_len, has_photo, has_append, diff):
        """
        计算评论有用的概率，需要已训练好的分类器
        """

        x = [self._preprocess([
            user_rank, content_len, has_photo, has_append, diff
        ])]
        return self._model.predict(x)[0][0]

    def predict_reviews(self, reviews):
        """
        计算所有评论有用的概率，返回数组
        """

        if not reviews:
            return []

        diffs = get_diffs(reviews)
        x = [self._preprocess([
                review.user_rank,
                len(review.content) + len(review.appends),
                review.has_photo,
                bool(review.appends),
                diff
            ]) for review, diff in zip(reviews, diffs)
        ]
        return [y[0] for y in self._model.predict(x)]


if __name__ == '__main__':
    UsefulnessModel().train()
