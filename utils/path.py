# -*- coding: utf-8 -*-

DATA_DIR = 'data'
DATABASE_PATH = DATA_DIR + '/database.db'
PLOTS_DIR = DATA_DIR + '/plots'

PHANTOM_JS_PATH = r'F:\WebDriver\phantomjs-2.1.1-windows\bin\phantomjs.exe'


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
