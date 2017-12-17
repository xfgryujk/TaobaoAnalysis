# -*- coding: utf-8 -*-

"""
画各种统计图
"""

from datetime import timedelta
from os.path import exists

import matplotlib.pyplot as plt

from analyze.models.sentiment import SentimentModel
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


def draw_rate_time_plot(reviews):
    """
    画评价数量-时间曲线
    """

    # date -> rate -> 数量
    rates = {}

    for review in reviews:
        if review.is_default():  # 忽略默认评论
            continue
        if review.date is None:  # 未知日期
            continue
        date = review.date.date()
        rate = review.rate

        if date not in rates:
            rates[date] = {'-1': 0, '0': 0, '1': 0}
        rates[date][rate] += 1

    if not rates:
        return

    # X
    min_date = min(rates.keys())
    max_date = max(rates.keys())
    dates = [min_date + timedelta(days=day_offset)
             for day_offset in range((max_date - min_date).days + 1)]
    # Y
    good_count = []
    bad_count = []
    for date in dates:
        rank = rates.get(date, {'-1': 0, '0': 0, '1': 0})
        good_count.append(rank['1'])
        bad_count.append(-(rank['-1'] + rank['0']))

    # 画图
    plt.bar(dates, good_count)
    plt.bar(dates, bad_count)
    # plt.ylim(-10, 40)


def draw_rate_histogram(reviews):
    """
    画情感直方图
    """

    global sentiment_model
    if sentiment_model is None:
        sentiment_model = SentimentModel()

    sentiments = [sentiment_model.predict(review.content)
                  for review in reviews]

    plt.hist(sentiments, bins=100, range=(0, 1), normed=1)


if __name__ == '__main__':
    draw_plot_per_item(draw_rate_histogram)
