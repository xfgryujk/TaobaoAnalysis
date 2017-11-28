# -*- coding: utf-8 -*-

DATA_DIR = 'data'

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
