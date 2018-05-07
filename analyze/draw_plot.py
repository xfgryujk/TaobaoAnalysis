# -*- coding: utf-8 -*-

"""
画各种统计图
"""

from datetime import timedelta
from os.path import exists

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import NullFormatter
from scipy import stats

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
    :param draw_func: 画图函数，参数：items
    :param plots_dir: 保存图像的文件夹
    """

    for item in session.query(Item):
        print(item.id, item.title)

        filename = '{} {}.png'.format(item.id, item.title)
        filename = replace_illegal_chars(filename)
        path = plots_dir + '/' + filename
        if exists(path):
            continue

        draw_func([item])
        plt.savefig(path)
        plt.cla()


def draw_rate_time_plot(items, ignore_default=False, fix_y_limit=True):
    """
    画评价数量-时间图
    """

    reviews = sum((item.reviews for item in items), [])
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


def draw_sentiment_histogram(items):
    """
    画情感直方图
    """

    global sentiment_model
    if sentiment_model is None:
        from analyze.models.sentiment import SentimentModel
        sentiment_model = SentimentModel()

    sentiments = sum((sentiment_model.predict_reviews(item.reviews)
                     for item in items), [])
    plt.title('情感直方图')
    plt.xlabel('情感')
    plt.ylabel('密度')
    plt.hist(sentiments, bins=100, range=(0, 1), density=True)


def draw_usefulness_histogram(items):
    """
    画有用直方图
    """

    global usefulness_model
    if usefulness_model is None:
        from analyze.models.usefulness import UsefulnessModel
        usefulness_model = UsefulnessModel()

    usefulness_ = sum((usefulness_model.predict_reviews(item.reviews)
                       for item in items), [])
    plt.title('有用概率直方图')
    plt.xlabel('有用概率')
    plt.ylabel('密度')
    plt.hist(usefulness_, bins=100, range=(0, 1), density=True)


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


def init_scatter_hist(x_limit, y_limit):
    """
    :return: ax_histx, ax_histy, ax_scatter
    """

    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = bottom + height + 0.02
    left_h = left + width + 0.02

    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]
    rect_scatter = [left, bottom, width, height]

    ax_histx = plt.axes(rect_histx)
    ax_histy = plt.axes(rect_histy)
    ax_scatter = plt.axes(rect_scatter)

    nullfmt = NullFormatter()
    ax_histx.xaxis.set_major_formatter(nullfmt)
    ax_histy.yaxis.set_major_formatter(nullfmt)

    ax_scatter.set_xlim(x_limit)
    ax_scatter.set_ylim(y_limit)
    ax_histx.set_xlim(x_limit)
    ax_histy.set_ylim(y_limit)

    return ax_histx, ax_histy, ax_scatter


def draw_sold_quality_plot(items):
    """
    画销量-质量图
    """

    from analyze.quality import get_item_quality

    items = list(filter(lambda item: len(item.reviews) >= 20, items))
    qualities = [get_item_quality(item) for item in items]
    sold_counts = [item.sold_count for item in items]

    x_limit = (0.55, 0.95)
    y_limit = (0, 1000)
    ax_histx, ax_histy, ax_scatter = init_scatter_hist(x_limit, y_limit)
    plt.xlabel('质量')
    plt.ylabel('销量')

    # 画图
    ax_histx.hist(qualities, bins=100, range=x_limit)
    ax_histy.hist(sold_counts, bins=100, range=y_limit, orientation='horizontal')
    ax_scatter.scatter(qualities, sold_counts)


def draw_sold_reviews_plot(items):
    """
    画销量-评论图
    """

    from analyze.quality import get_item_quality

    items = list(items)
    items.sort(key=get_item_quality)
    review_counts = [len(item.reviews) for item in items]
    sold_counts = [item.sold_count for item in items]

    x_limit = y_limit = (0, 1000)
    ax_histx, ax_histy, ax_scatter = init_scatter_hist(x_limit, y_limit)
    plt.xlabel('评论数')
    plt.ylabel('销量')

    # 画图
    ax_histx.hist(review_counts, bins=100, range=x_limit)
    ax_histy.hist(sold_counts, bins=100, range=y_limit, orientation='horizontal')
    ax_scatter.scatter(review_counts, sold_counts)
    # 最好和最差5个分别用绿色和红色表示
    ax_scatter.scatter(review_counts[-5:], sold_counts[-5:], c='#00FF00')
    ax_scatter.scatter(review_counts[:5], sold_counts[:5], c='r')


def main():
    # draw_plot_per_item(draw_sentiment_histogram)

    items = list(Item.with_reviews_more_than(20))

    # plt.figure(1)
    # draw_quality_histogram(items)
    #
    # plt.figure(2)
    # draw_usefulness_histogram(items)
    #
    # plt.figure(3)
    # draw_sentiment_histogram(items)
    #
    # plt.figure(4)
    # draw_sold_quality_plot(items)
    #
    plt.figure(5)
    draw_sold_reviews_plot(items)

    # 最好和最差的5个商品情感直方图
    # items = list(Item.with_reviews_more_than(20).order_by(Item.quality))
    # best_items = items[-5:]
    # worst_items = items[:5]
    # plt.figure(1)
    # draw_sentiment_histogram(best_items)
    # plt.figure(2)
    # draw_sentiment_histogram(worst_items)
    # plt.figure(3)
    # draw_usefulness_histogram(best_items)
    # plt.figure(4)
    # draw_usefulness_histogram(worst_items)

    plt.show()


if __name__ == '__main__':
    main()
