# -*- coding: utf-8 -*-

"""
计算评论有用的概率
"""

import pickle
from os.path import exists

from tflearn import (input_data, fully_connected, regression,
                     DNN)

from analyze.dataprocess.usefulness import (TRAIN_POS_PATH, TRAIN_NEG_PATH,
                                            TEST_POS_PATH, TEST_NEG_PATH)
from utils.path import MODELS_DIR

CLASSIFIER_MODEL_PATH = MODELS_DIR + '/usefulness'


class UsefulnessModel:
    """
    输入用户信用等级、评论长度、是否有图片、是否有追评、评论数量差分，输出有用、没用的概率
    """

    def __init__(self):
        self.classifier = self._create_classifier()
        if exists(CLASSIFIER_MODEL_PATH + '.meta'):
            self.classifier.load(CLASSIFIER_MODEL_PATH)

    @staticmethod
    def _create_classifier():
        net = input_data([None, 5])
        net = fully_connected(net, 40, bias=True, activation='tanh')
        net = fully_connected(net, 2, activation='softmax')
        net = regression(net, optimizer='adam', learning_rate=0.001,
                         loss='categorical_crossentropy')
        return DNN(net)

    def _read_samples(self, pos_path, neg_path):
        """
        读样本文件，返回X为处理后的样本数组，Y为分类概率数组
        """

        with open(pos_path, 'rb') as file:
            x = pickle.load(file)
        y = [[1., 0.]] * len(x)

        with open(neg_path, 'rb') as file:
            x += pickle.load(file)
        y += [[0., 1.]] * (len(x) - len(y))

        x = list(map(self._preprocess, x))

        return x, y

    @staticmethod
    def _preprocess(sample):
        """
        预处理，使各维度幅度差不多
        """

        sample = sample.copy()
        sample[0] /= 800
        sample[1] /= 50
        sample[4] /= 10
        return sample

    def train(self):
        """
        训练分类器
        需要训练、测试样本
        """

        train_x, train_y = self._read_samples(TRAIN_POS_PATH, TRAIN_NEG_PATH)
        test_x, test_y = self._read_samples(TEST_POS_PATH, TEST_NEG_PATH)

        self.classifier.fit(train_x, train_y, validation_set=(test_x, test_y),
                            n_epoch=30, shuffle=True, show_metric=True,
                            snapshot_epoch=True)

        self.classifier.save(CLASSIFIER_MODEL_PATH)

    def predict(self, user_rank, content_len, has_photo, has_append, diff):
        """
        计算评论有用的概率，需要已训练好的分类器
        """

        x = [self._preprocess(
            [user_rank, content_len, has_photo, has_append, diff]
        )]
        return self.classifier.predict(x)[0][0]


if __name__ == '__main__':
    model = UsefulnessModel()
    model.train()
