# -*- coding: utf-8 -*-

from datetime import timedelta

import matplotlib.pyplot as plt

from utils.database import session, Item
from utils.path import DATA_DIR, replace_illegal_chars

PLOTS_DIR = DATA_DIR + '/plots'


def draw_rate_plot(reviews):
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


def main():
    from os.path import exists

    for item in session.query(Item):
        print(item.id, item.title)

        filename = '{} {}.png'.format(item.id, item.title)
        filename = replace_illegal_chars(filename)
        path = PLOTS_DIR + '/' + filename
        if exists(path):
            continue

        plt.cla()
        draw_rate_plot(item.reviews)
        plt.savefig(path)


if __name__ == '__main__':
    main()
