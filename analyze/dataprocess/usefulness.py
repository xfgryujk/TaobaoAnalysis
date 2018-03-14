# -*- coding: utf-8 -*-

"""
创建训练有用概率模型用的数据集
"""

import datetime
import pickle
from random import choices

import matplotlib.pyplot as plt

from analyze import draw_plot
from utils.database import session, Rate, Item, Review
from utils.path import TRAIN_DIR

TRAIN_POS_PATH = TRAIN_DIR + '/usefulness_train_pos.pickle'
TRAIN_NEG_PATH = TRAIN_DIR + '/usefulness_train_neg.pickle'
TEST_POS_PATH = TRAIN_DIR + '/usefulness_test_pos.pickle'
TEST_NEG_PATH = TRAIN_DIR + '/usefulness_test_neg.pickle'


class AnnotateData:
    """
    手动标注数据
    """

    def __init__(self):
        self._figure = plt.gcf()
        self._canvas = self._figure.canvas
        self._canvas.mpl_connect('close_event', self._on_figure_close)
        self._canvas.mpl_connect('key_press_event', self._on_key_press)

        self.stop = False
        self._pressed_key = ''

    def _on_figure_close(self, event):
        self.stop = True
        self._canvas.stop_event_loop()

    def _on_key_press(self, event):
        self._pressed_key = event.key
        self._canvas.stop_event_loop()

    def start(self):
        print('认为有用则按Y，认为没用则按N：\n')
        # 防止matplotlib阻塞
        plt.ion()

        for item in (session.query(Item)
                     .filter(Item.reviews.any(Review.is_useful.is_(None)))
                     ):
            # 画评价数量-时间图
            dates, good_bars, bad_bars = draw_plot.draw_rate_time_plot(item.reviews)

            for review in item.reviews:
                if review.is_useful is not None:
                    continue
                # if review.is_default():
                #     review.is_useful = False
                #     session.commit()
                #     continue

                # 显示评论
                print('用户信用等级：', review.user_rank)
                try:
                    print('评价：', Rate(review.rate).name)
                except ValueError:
                    print('评价： 未知({})'.format(review.rate))
                print('内容：', review.content)
                if review.appends:
                    print('追评：', review.appends)
                print('有图片' if review.has_photo else '无图片')
                cur_date_bar = original_color = None
                if review.date is not None:
                    print('时间：', review.date.isoformat())
                    index = (review.date.date() - dates[0]).days
                    cur_date_bar = (good_bars[index]
                                    if review.is_good
                                    else bad_bars[index])
                    original_color = cur_date_bar.get_facecolor()
                    cur_date_bar.set_color('r')
                else:
                    print('时间： 未知')
                plt.show()

                # 输入是否有用
                self._pressed_key = ''
                while self._pressed_key not in ('y', 'n'):
                    self._canvas.start_event_loop()
                    if self.stop:
                        return
                print(self._pressed_key)
                print('')
                review.is_useful = self._pressed_key == 'y'
                session.commit()

                if cur_date_bar is not None:
                    cur_date_bar.set_color(original_color)

            plt.cla()


def get_n_rates_and_time(reviews, ignore_default=False):
    """
    获取每天好评、差评数量数组和最小日期
    """

    # date -> rate -> 数量
    rates = {}

    for review in reviews:
        if (ignore_default and review.is_default  # 忽略默认评论
            or review.date is None  # 未知日期
        ):
            continue
        date = review.date.date()
        rate = review.rate

        rates.setdefault(date, {rate: 0 for rate in Rate})
        rates[date][rate] += 1

    if not rates:
        return [], [], datetime.date.min

    min_date = min(rates.keys())
    max_date = max(rates.keys())
    dates = (min_date + datetime.timedelta(days=day_offset)
             for day_offset in range((max_date - min_date).days + 1))
    good_counts = []
    bad_counts = []
    for date in dates:
        n_rates = rates.get(date, {rate: 0 for rate in Rate})
        good_counts.append(n_rates[Rate.GOOD] + n_rates[Rate.DEFAULT])
        bad_counts.append(n_rates[Rate.BAD] + n_rates[Rate.MIDDLE])

    return good_counts, bad_counts, min_date


def create_train_test(train_pos_path=TRAIN_POS_PATH, train_neg_path=TRAIN_NEG_PATH,
                      test_pos_path=TEST_POS_PATH, test_neg_path=TEST_NEG_PATH):
    """
    创建训练和测试样本，保证正负样本数一样
    """

    pos = []
    neg = []
    for item in (session.query(Item)
                 .filter(Item.reviews.any(Review.is_useful.isnot(None)))
                 ):
        good_counts, bad_counts, min_date = get_n_rates_and_time(item.reviews)
        if not good_counts:
            continue

        for review in item.reviews:
            if (review.is_useful is None  # 未标注
                or review.date is None  # 未知日期
            ):
                continue

            # 计算评论数量差分
            date = review.date.date()
            index = (date - min_date).days
            diff = (0 if index == 0
                    else (good_counts[index] - good_counts[index - 1]
                          if review.is_good
                          else bad_counts[index] - bad_counts[index - 1])
                    )

            sample = [
                review.user_rank,                           # 用户信用等级
                len(review.content) + len(review.appends),  # 评论长度
                1 if review.has_photo else 0,               # 是否有图片
                1 if review.appends else 0,                 # 是否有追评
                diff,                                       # 评论数量差分
            ]

            if review.is_useful:
                pos.append(sample)
            else:
                neg.append(sample)

    size = min(len(pos), len(neg))
    size_train = int(size * 0.8)
    pos = choices(pos, k=size)
    neg = choices(neg, k=size)

    for data, path in ((pos[:size_train], train_pos_path),
                       (neg[:size_train], train_neg_path),
                       (pos[size_train:], test_pos_path),
                       (neg[size_train:], test_neg_path)):
        with open(path, 'wb') as file:
            pickle.dump(data, file)


if __name__ == '__main__':
    # AnnotateData().start()
    create_train_test()
