# -*- coding: utf-8 -*-

"""
创建训练有用概率模型用的数据集
"""

import msvcrt
from threading import Thread

import matplotlib.pyplot as plt

from analyze.draw_plot import draw_rate_time_plot
from utils.database import Session, Rate, Item, Review


def get_char():
    """
    等待键盘按下，Windows版
    """

    ch = msvcrt.getch()
    if ch == b'\0' or ch == b'\xE0':
        ch = msvcrt.getch()
    return chr(ord(ch))


def annotate_data_thread():
    """
    标注数据的线程
    """

    session = Session()
    for item in (session.query(Item)
                 .filter(Item.reviews.any(Review.is_useful.is_(None)))
                 ):
        # 画评价数量-时间图
        dates, _, _, good_bars, bad_bars = draw_rate_time_plot(item.reviews)

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
                                if review.rate in (Rate.GOOD, Rate.DEFAULT)
                                else bad_bars[index])
                original_color = cur_date_bar.get_facecolor()
                cur_date_bar.set_color('r')
            else:
                print('时间： 未知')
            print('')

            # 输入是否有用
            ch = ''
            while ch not in ('y', 'n'):
                ch = get_char().lower()
            review.is_useful = ch == 'y'
            session.commit()

            if cur_date_bar is not None:
                cur_date_bar.set_color(original_color)

        plt.cla()


def annotate_data():
    """
    手动标注数据，只能从Windows控制台运行，不能从IDE运行
    """

    print('认为有用则按Y，认为没用则按N：\n')

    # 防止matplotlib阻塞
    plt.ion()

    canvas = plt.gcf().canvas
    canvas.mpl_connect('close_event', lambda event: canvas.stop_event_loop())

    # 其他线程标注数据，主线程消息循环
    Thread(target=annotate_data_thread, daemon=True).start()
    canvas.start_event_loop()


if __name__ == '__main__':
    annotate_data()
