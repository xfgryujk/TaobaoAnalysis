# -*- coding: utf-8 -*-

"""
使用RNN模型计算句子情感值
"""

import codecs
from os.path import exists

from tensorflow import reset_default_graph
from tflearn import input_data, embedding, lstm, fully_connected, regression, DNN
from tflearn.data_utils import VocabularyProcessor

from analyze.dataprocess.sentiment import (TRAIN_POS_PATH, TRAIN_NEG_PATH,
                                           TEST_POS_PATH, TEST_NEG_PATH,
                                           chinese_tokenizer)
from utils.path import MODELS_DIR

MODEL_PATH = MODELS_DIR + '/sentiment'
VOCABULARY_PATH = MODEL_PATH + '.vocab.pickle'
# 句子中最多词数
SEQUENCE_LEN = 64
# 词向量特征数
WORD_FEATURE_DIM = 128
# 文本特征数
DOC_FEATURE_DIM = 128


class SentimentModel:
    """
    输入句子 -> 分词 -> 词ID -> 词向量 -> LSTM层 -> 全连接层 -> 输出正面、负面概率
    取正面概率为情感值
    """

    def __init__(self):
        if not exists(VOCABULARY_PATH):
            self._vocab = self._create_vocab()
            self._vocab.save(VOCABULARY_PATH)
        else:
            self._vocab = VocabularyProcessor.restore(VOCABULARY_PATH)

        self._model = self._create_model()
        if exists(MODEL_PATH + '.meta'):
            self._model.load(MODEL_PATH, True)

    @staticmethod
    def _create_vocab(min_count=3):
        """
        创建词汇表
        需要训练样本
        """

        def gen_documents():
            for path in (TRAIN_POS_PATH, TRAIN_NEG_PATH):
                with codecs.open(path, 'r', 'utf-8') as file:
                    for line in file:
                        yield line[:-1]

        vocab = VocabularyProcessor(SEQUENCE_LEN, min_count - 1,
                                    tokenizer_fn=chinese_tokenizer)
        vocab.fit(gen_documents())
        return vocab

    def _create_model(self):
        reset_default_graph()
        net = input_data([None, SEQUENCE_LEN])
        net = embedding(net, input_dim=len(self._vocab.vocabulary_),
                        output_dim=WORD_FEATURE_DIM)
        net = lstm(net, DOC_FEATURE_DIM, dropout=0.8)
        net = fully_connected(net, 2, activation='softmax')
        net = regression(net, optimizer='adam', learning_rate=0.001,
                         loss='categorical_crossentropy')
        return DNN(net)

    def _read_train_samples(self, pos_path, neg_path):
        """
        读样本文件，返回X为词ID序列数组（已填充长度到SEQUENCE_LEN），Y为分类概率数组
        """

        x, y = [], []
        for path, y_ in ((pos_path, [1., 0.]),
                         (neg_path, [0., 1.])):
            with codecs.open(path, 'r', 'utf-8') as file:
                for line in file:
                    x.append(line[:-1])
            y += [y_] * (len(x) - len(y))
        x = list(self._vocab.transform(x))

        return x, y

    def train(self):
        """
        训练分类器
        需要训练、测试样本
        """

        train_x, train_y = self._read_train_samples(TRAIN_POS_PATH, TRAIN_NEG_PATH)
        test_x, test_y = self._read_train_samples(TEST_POS_PATH, TEST_NEG_PATH)

        self._model.fit(train_x, train_y, validation_set=(test_x, test_y),
                        n_epoch=20, shuffle=True, show_metric=True,
                        snapshot_epoch=True)

        self._model.save(MODEL_PATH)

    def predict(self, text):
        """
        计算文本情感值，需要已训练好的分类器
        """

        x = list(self._vocab.transform([text]))
        return self._model.predict(x)[0][0]

    def predict_reviews(self, reviews):
        """
        计算所有评论的文本情感值，返回数组
        """

        if not reviews:
            return []

        x = [
            review.content if not review.appends
            else review.content + '\n' + review.appends
            for review in reviews
        ]
        x = list(self._vocab.transform(x))

        # 分批计算，防止内存不够
        y = []
        for index in range(0, len(x), 64):
            batch_x = x[index: min(index + 64, len(x))]
            y += [y_[0] for y_ in self._model.predict(batch_x)]

        return y


if __name__ == '__main__':
    SentimentModel().train()
