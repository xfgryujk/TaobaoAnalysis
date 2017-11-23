# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from utils.path import COMMENTS_DIR, PLOTS_DIR


def draw_rate_plot(file):
    # date -> rate -> 数量
    rates = {}

    for line in file:
        data = json.loads(line)
        for comment in data['comments']:
            # 日期
            try:
                date = datetime.strptime(comment['date'], '%Y年%m月%d日 %H:%M')
            except ValueError:
                # print('Unknown date:', comment['date'])  # ''
                continue
            date = date.date()
            # 评价，-1差评，0中评，1好评
            rate = comment['rate']

            if date not in rates:
                rates[date] = {'-1': 0, '0': 0, '1': 0}
            rates[date][rate] += 1

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
    # plt.ylim(-25, 25)
    # plt.show()


def main():
    import os

    for filename in os.listdir(COMMENTS_DIR):
        title, ext = os.path.splitext(filename)
        if not ext == '.txt':
            continue
        path = os.path.join(COMMENTS_DIR, filename)
        print(filename)

        plt.cla()
        with open(path) as f:
            draw_rate_plot(f)
        plt.savefig(os.path.join(PLOTS_DIR, title + '.png'))


if __name__ == '__main__':
    main()
