# -*- coding: utf-8 -*-

"""
测试模型计算情感值正确率
"""

from analyze.models.sentiment import SentimentModel

from utils.database import session, Rate, Review

model = SentimentModel()
total_contents = 0
total_correct = 0


def eval_classify(content, rate):
    if not content:
        return
    rate = Rate.GOOD if Rate(rate).is_good else Rate.BAD

    sentiments = model.predict(content)
    _rate = Rate.GOOD if sentiments > 0.5 else Rate.BAD
    
    global total_contents, total_correct
    total_contents += 1
    if _rate == rate:
        total_correct += 1
    else:
        print(sentiments, rate.name, content)
    
    
def main():
    for index, review in enumerate(Review.filter_default(session.query(Review))):
        eval_classify(review.content, review.rate)
        for content in review.appends.split('\n'):
            eval_classify(content, review.rate)

        if index % 100 == 99:
            print('total_contents =', total_contents)
            print('total_correct =', total_correct)
            print('correct_rate =', total_correct / total_contents)
            # 大约84.4%正确率


if __name__ == '__main__':
    main()
