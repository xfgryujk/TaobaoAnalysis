# -*- coding: utf-8 -*-

from hanziconv import HanziConv


def clean_text(text):
    """
    繁体转简体、英文转小写
    """

    text = HanziConv.toSimplified(text)
    text = text.lower()
    return text
