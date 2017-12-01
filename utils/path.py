# -*- coding: utf-8 -*-

"""
定义多个模块要用的路径、辅助函数
"""

DATA_DIR = 'data'
CRAWLER_DATA_DIR = DATA_DIR + '/crawler'
TRAIN_DIR = DATA_DIR + '/train'
MODELS_DIR = DATA_DIR + '/models'


def replace_illegal_chars(filename):
    """
    把非法文件名字符替换为合法字符
    """

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
