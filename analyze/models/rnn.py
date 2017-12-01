# -*- coding: utf-8 -*-

import codecs
from os.path import exists

from jieba import cut
from tflearn import (input_data, embedding, lstm, fully_connected, regression,
                     DNN)
from tflearn.data_utils import pad_sequences

from utils.path import MODELS_DIR
from utils.train import (TRAIN_POS_PATH, TRAIN_NEG_PATH,
                         TEST_POS_PATH, TEST_NEG_PATH)

CLASSIFIER_MODEL_PATH = MODELS_DIR + '/rnn_classifier'
VOCABULARY_PATH = CLASSIFIER_MODEL_PATH + '.vocab.txt'
FEATURE_DIM = 128
SEQUENCE_LEN = 100


class Model:

    def __init__(self):
        if not exists(VOCABULARY_PATH):
            self._build_vocab()
        else:
            with codecs.open(VOCABULARY_PATH, 'r', 'utf-8') as file:
                self.vocab = [line[:-1] for line in file]
            self.word_id = {word: index for index, word in enumerate(self.vocab)}

        self.classifier = self._create_classifier()
        if exists(CLASSIFIER_MODEL_PATH + '.meta'):
            self.classifier.load(CLASSIFIER_MODEL_PATH)

    def _build_vocab(self, min_freq=3):
        """
        创建词汇表
        需要训练样本
        """

        freq = {}
        for path in (TRAIN_POS_PATH, TRAIN_NEG_PATH):
            with codecs.open(path, 'r', 'utf-8') as file:
                for line in file:
                    for word in line[:-1].split(' '):
                        freq[word] = freq.get(word, 0) + 1

        for del_word in ('', '\n'):
            if del_word in freq:
                del freq[del_word]
        # 保证''ID为0
        self.vocab = [''] + [word for word, count in freq.items() if count >= min_freq]

        with codecs.open(VOCABULARY_PATH, 'w', 'utf-8') as file:
            for word in self.vocab:
                file.write(word)
                file.write('\n')
        self.word_id = {word: index for index, word in enumerate(self.vocab)}

    def _create_classifier(self):
        net = input_data([None, SEQUENCE_LEN])
        net = embedding(net, input_dim=len(self.vocab), output_dim=FEATURE_DIM)
        net = lstm(net, 128, dropout=0.8)
        net = fully_connected(net, 2, activation='softmax')
        net = regression(net, optimizer='adam', learning_rate=0.001,
                         loss='categorical_crossentropy')
        return DNN(net)

    def _read_samples(self, pos_path, neg_path):
        """
        读样本文件，返回X为词ID序列数组，Y为分类概率数组
        """

        x = []
        with codecs.open(pos_path, 'r', 'utf-8') as file:
            for line in file:
                x.append([self.word_id.get(word, 0) for word in line[:-1].split(' ')])
        y = [[1., 0.]] * len(x)

        with codecs.open(neg_path, 'r', 'utf-8') as file:
            for line in file:
                x.append([self.word_id.get(word, 0) for word in line[:-1].split(' ')])
        y += [[0., 1.]] * (len(x) - len(y))

        x = pad_sequences(x, maxlen=SEQUENCE_LEN, value=0.)

        return x, y

    def train(self):
        """
        训练分类器
        需要训练、测试样本
        """

        train_x, train_y = self._read_samples(TRAIN_POS_PATH, TRAIN_NEG_PATH)
        test_x, test_y = self._read_samples(TEST_POS_PATH, TEST_NEG_PATH)

        self.classifier.fit(train_x, train_y, validation_set=(test_x, test_y),
                            n_epoch=20, shuffle=True, show_metric=True,
                            snapshot_epoch=True)

        self.classifier.save(CLASSIFIER_MODEL_PATH)

    def predict(self, text):
        """
        计算文本情感值，需要已训练好的分类器
        """

        x = [[self.word_id.get(word, 0) for word in cut(text)]]
        x = pad_sequences(x, maxlen=SEQUENCE_LEN, value=0.)
        return self.classifier.predict(x)[0][0]


if __name__ == '__main__':
    model = Model()
    model.train()
