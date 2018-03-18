# -*- coding: utf-8 -*-

"""
画各种统计图
"""

from datetime import timedelta
from os.path import exists

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from sqlalchemy import func

from analyze.dataprocess import usefulness
from utils.database import session, Item
from utils.path import DATA_DIR, replace_illegal_chars

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


PLOTS_DIR = DATA_DIR + '/plots'

sentiment_model = usefulness_model = None


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
    plt.title('评价数量-时间图')
    plt.xlabel('时间')
    plt.ylabel('评价数量')
    good_bars = plt.bar(dates, good_counts)
    bad_bars = plt.bar(dates, bad_counts)
    if fix_y_limit:
        plt.ylim(-10, 40)

    return dates, good_bars, bad_bars


def draw_sentiment_histogram(reviews):
    """
    画情感直方图
    """

    global sentiment_model
    if sentiment_model is None:
        from analyze.models.sentiment import SentimentModel
        sentiment_model = SentimentModel()

    sentiments = sentiment_model.predict_reviews(reviews)
    plt.title('情感直方图')
    plt.xlabel('情感')
    plt.ylabel('数量')
    plt.hist(sentiments, bins=100, range=(0, 1))


def draw_usefulness_histogram(reviews):
    """
    画有用直方图
    """

    global usefulness_model
    if usefulness_model is None:
        from analyze.models.usefulness import UsefulnessModel
        usefulness_model = UsefulnessModel()

    usefulness_ = usefulness_model.predict_reviews(reviews)
    plt.title('有用概率直方图')
    plt.xlabel('有用概率')
    plt.ylabel('数量')
    plt.hist(usefulness_, bins=100, range=(0, 1))


def draw_quality_histogram(items):
    """
    画质量直方图
    """

    from analyze.quality import get_item_quality

    qualities = [get_item_quality(item) for item in items
                 if len(item.reviews) >= 20]
    plt.title('质量直方图')
    plt.xlabel('质量')
    plt.ylabel('分布密度')
    plt.hist(qualities, bins=100, range=(0, 1), density=True)

    # 拟合正态分布
    mean = np.mean(qualities)
    std = np.std(qualities)
    x = np.arange(0, 1, 0.01)
    y = stats.norm.pdf(x, loc=mean, scale=std)
    plt.plot(x, y)
    plt.text(0, 5, r'$N={},\mu={:.3f},\sigma={:.3f}$'
                   .format(len(qualities), mean, std))



if __name__ == '__main__':
    # draw_plot_per_item(draw_sentiment_histogram)
    draw_quality_histogram(session.query(Item)
                           .join(Item.reviews)
                           .group_by(Item.id)
                           .having(func.count(Item.reviews)) >= 20)
    plt.show()
