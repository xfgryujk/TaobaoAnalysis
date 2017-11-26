# -*- coding: utf-8 -*-

import codecs
from os.path import exists
from random import shuffle

from gensim import utils
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from snownlp import SnowNLP

from utils.database import session, Review, Rate
from utils.path import DATA_DIR

CORPUS_POS_PATH = DATA_DIR + '/corpus_pos.txt'
CORPUS_NEG_PATH = DATA_DIR + '/corpus_neg.txt'
DOC2VEC_MODEL_PATH = DATA_DIR + '/model.d2v'

TRAIN_NEW_MODEL = False


def create_corpus():
    if exists(CORPUS_POS_PATH) or exists(CORPUS_NEG_PATH):
        if input('确定要覆盖已有的语料库则输入y：') != 'y':
            return

    with codecs.open(CORPUS_POS_PATH, 'w', 'utf-8') as pos_file:
        with codecs.open(CORPUS_NEG_PATH, 'w', 'utf-8') as neg_file:
            count = 0
            for content, rate in Review.filter_default(
                    session.query(Review.content, Review.rate)
                    .filter(Review.content != '')
                    ):
                snow = SnowNLP(content)
                file = pos_file if rate == Rate.good else neg_file
                file.write(' '.join(snow.words))
                file.write('\n')

                count += 1
                if count % 100 == 0:
                    print(count)


class TaggedLineDocument:
    """
    来自多个文件的训练句子
    用法：
    sources = {'test-neg.txt':'TEST_NEG', 'test-pos.txt':'TEST_POS',
               'train-neg.txt':'TRAIN_NEG', 'train-pos.txt':'TRAIN_POS',
               'train-unsup.txt':'TRAIN_UNS'}
    sentences = LabeledLineSentence(sources)
    值（前缀）必须唯一
    """

    def __init__(self, sources):
        self.sources = sources
        self.sentences = []

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
                    yield TaggedDocument(utils.to_unicode(line).split(),
                                         [prefix + '_%s' % item_no])

    def to_array(self):
        self.sentences = []
        for source, prefix in self.sources.items():
            with utils.smart_open(source) as fin:
                for item_no, line in enumerate(fin):
                    self.sentences.append(TaggedDocument(
                        utils.to_unicode(line).split(),
                        [prefix + '_%s' % item_no])
                    )
        return self.sentences

    def sentences_perm(self):
        shuffle(self.sentences)
        return self.sentences


def main():
    # create_corpus()

    sources = {
        CORPUS_POS_PATH: 'POS',
        CORPUS_NEG_PATH: 'NEG',
    }
    sentences = TaggedLineDocument(sources)
    sentences.to_array()

    if TRAIN_NEW_MODEL:
        model = Doc2Vec(min_count=1, window=10, size=100, sample=1e-4,
                        negative=5, workers=8)
        model.build_vocab(sentences.sentences)
    else:
        model = Doc2Vec.load(DOC2VEC_MODEL_PATH)

    model.train(sentences.sentences_perm(), total_examples=model.corpus_count,
                epochs=10)

    model.save(DOC2VEC_MODEL_PATH)


if __name__ == '__main__':
    main()
