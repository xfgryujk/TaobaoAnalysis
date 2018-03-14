# -*- coding: utf-8 -*-

"""
画各种统计图
"""

from datetime import timedelta
from os.path import exists

import matplotlib.pyplot as plt

from analyze.dataprocess import usefulness
from utils.database import session, Item
from utils.path import DATA_DIR, replace_illegal_chars

PLOTS_DIR = DATA_DIR + '/plots'

sentiment_model = None


def draw_plot_per_item(draw_func, plots_dir=PLOTS_DIR):
    """
    每个商品画一个图，保存到文件
    :param draw_func: 画图函数，参数：reviews
    :param plots_dir: 保存图像的文件夹
    """

    for item in session.query(Item):
        print(item.id, item.title)

        filename = '{} {}.png'.format(item.id, item.title)
        filename = replace_illegal_chars(filename)
        path = plots_dir + '/' + filename
        if exists(path):
            continue

        draw_func(item.reviews)
        plt.savefig(path)
        plt.cla()


def draw_rate_time_plot(reviews, ignore_default=False, fix_y_limit=True):
    """
    画评价数量-时间图
    """

    good_counts, bad_counts, min_date = usefulness.get_n_rates_and_time(reviews, ignore_default)
    if not good_counts:
        return [], [], []
    bad_counts = list(map(int.__neg__, bad_counts))
    dates = [min_date + timedelta(days=day_offset)
             for day_offset in range(len(good_counts))]

    # 画图
    good_bars = plt.bar(dates, good_counts)
    bad_bars = plt.bar(dates, bad_counts)
    if fix_y_limit:
        plt.ylim(-10, 40)

    return dates, good_bars, bad_bars


def draw_rate_histogram(reviews):
    """
    画情感直方图
    """

    global sentiment_model
    if sentiment_model is None:
        from analyze.models.sentiment import SentimentModel
        sentiment_model = SentimentModel()

    sentiments = [sentiment_model.predict(review.content)
                  for review in reviews]

    plt.hist(sentiments, bins=100, range=(0, 1), normed=1)


if __name__ == '__main__':
    draw_plot_per_item(draw_rate_time_plot)
