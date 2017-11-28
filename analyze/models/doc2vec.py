# -*- coding: utf-8 -*-

import codecs
from os.path import exists

from gensim import utils
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from jieba import cut

from utils.path import DATA_DIR
from utils.train import (CORPUS_POS_PATH, CORPUS_NEG_PATH, TRAIN_POS_PATH,
                         TRAIN_NEG_PATH, TEST_POS_PATH, TEST_NEG_PATH)

from tflearn import input_data, fully_connected, regression, DNN

DOC2VEC_MODEL_PATH = DATA_DIR + '/model.d2v'
CLASSIFIER_MODEL_PATH = DATA_DIR + '/d2v_classifier'
FEATURE_DIM = 128


class TaggedLineDocument:
    """
    来自多个文件的训练句子
    用法：
    sources = {'test-neg.txt':'TEST_NEG', 'test-pos.txt':'TEST_POS',
               'models-neg.txt':'TRAIN_NEG', 'models-pos.txt':'TRAIN_POS',
               'models-unsup.txt':'TRAIN_UNS'}
    sentences = LabeledLineSentence(sources)
    值（前缀）必须唯一
    """

    def __init__(self, sources):
        self.sources = sources

        flipped = {}

        # make sure that keys are unique
        for key, value in sources.items():
            if value not in flipped:
                flipped[value] = [key]
            else:
                raise Exception('Non-unique prefix encountered')

    def __iter__(self):
        for source, prefix in self.sources.items():
            with utils.smart_open(source) as fin:
                for item_no, line in enumerate(fin):
                    yield TaggedDocument(utils.to_unicode(line[:-1]).split(' '),
                                         [prefix + '_' + str(item_no)])


class Model:
    """
    目前效果很差，预测结果全在0.7左右
    """

    def __init__(self):
        if exists(DOC2VEC_MODEL_PATH):
            self.d2v = Doc2Vec.load(DOC2VEC_MODEL_PATH)
        else:
            self.d2v = Doc2Vec(min_count=3, window=10, size=FEATURE_DIM,
                               sample=1e-4, negative=5, workers=8)

        self.classifier = self._create_classifier()
        if exists(CLASSIFIER_MODEL_PATH + '.meta'):
            self.classifier.load(CLASSIFIER_MODEL_PATH)

    def train_doc2vec(self):
        """
        训练Doc2Vec模型
        需要语料库
        """

        sources = {CORPUS_POS_PATH: 'POS', CORPUS_NEG_PATH: 'NEG'}
        sentences = TaggedLineDocument(sources)
        self.d2v.build_vocab(sentences)

        self.d2v.train(sentences, total_examples=self.d2v.corpus_count,
                       epochs=20)

        self.d2v.save(DOC2VEC_MODEL_PATH)

    @staticmethod
    def _create_classifier():
        net = input_data([None, FEATURE_DIM])
        net = fully_connected(net, 128, activation='tanh')
        net = fully_connected(net, 2, activation='softmax')
        net = regression(net, optimizer='adam', learning_rate=0.001,
                         loss='categorical_crossentropy')
        return DNN(net)

    def _read_samples(self, pos_path, neg_path):
        """
        读样本文件，返回X为文档向量数组，Y为分类概率数组
        需要已训练好的Doc2Vec模型
        """

        x = []
        with codecs.open(pos_path, 'r', 'utf-8') as file:
            for line in file:
                x.append(self.d2v.infer_vector(line[:-1].split(' ')))
        y = [[1., 0.]] * len(x)

        with codecs.open(neg_path, 'r', 'utf-8') as file:
            for line in file:
                x.append(self.d2v.infer_vector(line[:-1].split(' ')))
        y += [[0., 1.]] * (len(x) - len(y))

        return x, y

    def train_classifier(self):
        """
        训练DNN分类器
        需要训练、测试样本和已训练好的Doc2Vec模型
        """

        train_x, train_y = self._read_samples(TRAIN_POS_PATH, TRAIN_NEG_PATH)
        test_x, test_y = self._read_samples(TEST_POS_PATH, TEST_NEG_PATH)

        self.classifier.fit(train_x, train_y, validation_set=(test_x, test_y),
                            n_epoch=20, shuffle=True, show_metric=True,
                            snapshot_epoch=True)

        self.classifier.save(CLASSIFIER_MODEL_PATH)

    def predict(self, text):
        """
        计算文本情感值，需要已训练好的Doc2Vec模型和DNN分类器
        """

        x = [self.d2v.infer_vector(cut(text))]
        return self.classifier.predict(x)[0][0]


if __name__ == '__main__':
    model = Model()
    # model.train_doc2vec()
    model.train_classifier()
