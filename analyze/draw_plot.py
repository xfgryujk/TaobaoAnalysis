# -*- coding: utf-8 -*-

"""
画各种统计图
"""

from datetime import timedelta
from os.path import exists

import matplotlib.pyplot as plt

from utils.database import session, Item
from utils.path import DATA_DIR, replace_illegal_chars

PLOTS_DIR = DATA_DIR + '/plots'


def do_draw_rate_time_plot(reviews):
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


def draw_rate_time_plot():
    """
    画所有商品的评价数量-时间曲线，保存到文件
    """

    for item in session.query(Item):
        print(item.id, item.title)

        filename = '{} {}.png'.format(item.id, item.title)
        filename = replace_illegal_chars(filename)
        path = PLOTS_DIR + '/' + filename
        if exists(path):
            continue

        plt.cla()
        do_draw_rate_time_plot(item.reviews)
        plt.savefig(path)


if __name__ == '__main__':
    draw_rate_time_plot()
