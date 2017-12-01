# -*- coding: utf-8 -*-

DATA_DIR = 'data'
CRAWLER_DATA_DIR = DATA_DIR + '/crawler'
TRAIN_DIR = DATA_DIR + '/train'
MODELS_DIR = DATA_DIR + '/models'


def replace_illegal_chars(filename):
    params = (
        ('\\', '＼'),
        ('/', '／'),
        (',', '：'),
        ('*', '＊'),
        ('?', '？'),
        ('"', "'"),
        ('<', '＜'),
        ('>', '＞'),
        ('|', '｜')
    )
    for param in params:
        filename = filename.replace(*param)
    return filename
