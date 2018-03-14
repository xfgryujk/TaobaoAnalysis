# -*- coding: utf-8 -*-

"""
创建训练有用概率模型用的数据集
"""

import matplotlib.pyplot as plt

from analyze.draw_plot import draw_rate_time_plot
from utils.database import session, Rate, Item, Review


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


if __name__ == '__main__':
    AnnotateData().start()
