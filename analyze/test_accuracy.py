# -*- coding: utf-8 -*-

from snownlp import SnowNLP

from utils.database import session, Rate, Review

total_contents = 0
total_correct = 0


def eval_classify(content, rate):
    if not content:
        return

    snow = SnowNLP(content)
    sentiments = snow.sentiments
    _rate = Rate.bad if sentiments < 0.4 else Rate.good if sentiments > 0.6 else Rate.middle
    
    global total_contents, total_correct
    total_contents += 1
    if _rate == rate:
        total_correct += 1
    
    
def main():
    for review in Review.filter_default(session.query(Review)):
        print(review.id)

        eval_classify(review.content, review.rate)
        for content in review.appends.split('\n'):
            eval_classify(content, review.rate)

    print('total_contents =', total_contents)
    print('total_correct =', total_correct)
    print('correct_rate =', total_correct / total_contents)
    # 大约73.3%正确率，运算超慢


if __name__ == '__main__':
    main()
