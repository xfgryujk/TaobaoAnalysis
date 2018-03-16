# -*- coding: utf-8 -*-

"""
使用RNN模型计算句子情感值
"""

import codecs
from os.path import exists

from jieba import cut
from tflearn import input_data, embedding, lstm, fully_connected, regression, DNN
from tflearn.data_utils import pad_sequences

from analyze.dataprocess.sentiment import (TRAIN_POS_PATH, TRAIN_NEG_PATH,
                                           TEST_POS_PATH, TEST_NEG_PATH, clean_text)
from utils.path import MODELS_DIR

CLASSIFIER_MODEL_PATH = MODELS_DIR + '/sentiment'
VOCABULARY_PATH = CLASSIFIER_MODEL_PATH + '.vocab.txt'
# 词向量特征数
FEATURE_DIM = 128
# 句子中最多词数
SEQUENCE_LEN = 64


class SentimentModel:
    """
    输入句子 -> 分词 -> 词ID -> 词向量 -> LSTM层 -> 全连接层 -> 输出正面、负面概率
    取正面概率为情感值
    """

    def __init__(self):
        if not exists(VOCABULARY_PATH):
            self._create_vocab()
            self._save_vocab()
        else:
            self._load_vocab()

        self._classifier = self._create_classifier()
        if exists(CLASSIFIER_MODEL_PATH + '.meta'):
            self._classifier.load(CLASSIFIER_MODEL_PATH)

    def _create_vocab(self, min_count=3):
        """
        创建词汇表
        需要训练样本
        """

        freq = {}
        for path in (TRAIN_POS_PATH, TRAIN_NEG_PATH):
            with codecs.open(path, 'r', 'utf-8') as file:
                for line in file:
                    for word in line[:-1].split('　'):
                        freq[word] = freq.get(word, 0) + 1

        for del_word in ('', '\n'):
            if del_word in freq:
                del freq[del_word]

        # ID为0表示填充用，无意义
        self._vocab = [''] + [word for word, count in freq.items() if count >= min_count]
        self._word_id = {word: index for index, word in enumerate(self._vocab)}

    def _save_vocab(self, path=VOCABULARY_PATH):
        with codecs.open(path, 'w', 'utf-8') as file:
            for word in self._vocab:
                file.write(word)
                file.write('\n')

    def _load_vocab(self, path=VOCABULARY_PATH):
        with codecs.open(path, 'r', 'utf-8') as file:
            self._vocab = [line[:-1] for line in file]
        self._word_id = {word: index for index, word in enumerate(self._vocab)}

    def _create_classifier(self):
        net = input_data([None, SEQUENCE_LEN])
        net = embedding(net, input_dim=len(self._vocab), output_dim=FEATURE_DIM)
        net = lstm(net, FEATURE_DIM, dropout=0.8)
        net = fully_connected(net, 2, activation='softmax')
        net = regression(net, optimizer='adam', learning_rate=0.001,
                         loss='categorical_crossentropy')
        return DNN(net)

    def _preprocess(self, text_or_words):
        """
        预处理，把原始文本或词序列数组转为词ID序列数组（已填充长度到SEQUENCE_LEN）
        """

        words = (cut(clean_text(text_or_words)) if isinstance(text_or_words, str)
                 else text_or_words)
        x = [self._word_id.get(word, 0) for word in words]
        x = pad_sequences([x], maxlen=SEQUENCE_LEN, value=0)[0]
        return x

    def _read_train_sample(self, path, y):
        """
        读一个样本文件，返回X为词ID序列数组（已填充长度到SEQUENCE_LEN），Y为分类概率数组
        """

        x = []
        with codecs.open(path, 'r', 'utf-8') as file:
            for line in file:
                x.append(self._preprocess(line[:-1].split('　')))
        y = [y] * len(x)

        return x, y

    def _read_train_samples(self, pos_path, neg_path):
        """
        读样本文件，返回X为词ID序列数组（已填充长度到SEQUENCE_LEN），Y为分类概率数组
        """

        x, y = [], []
        for path, y_ in ((pos_path, [1., 0.]),
                         (neg_path, [0., 1.])):
            x_, y_ = self._read_train_sample(path, y_)
            x += x_
            y += y_

        return x, y

    def train(self):
        """
        训练分类器
        需要训练、测试样本
        """

        train_x, train_y = self._read_train_samples(TRAIN_POS_PATH, TRAIN_NEG_PATH)
        test_x, test_y = self._read_train_samples(TEST_POS_PATH, TEST_NEG_PATH)

        self._classifier.fit(train_x, train_y, validation_set=(test_x, test_y),
                             n_epoch=20, shuffle=True, show_metric=True,
                             snapshot_epoch=True)

        self._classifier.save(CLASSIFIER_MODEL_PATH)

    def predict(self, text):
        """
        计算文本情感值，需要已训练好的分类器
        """

        x = [self._preprocess(text)]
        return self._classifier.predict(x)[0][0]


if __name__ == '__main__':
    SentimentModel().train()
