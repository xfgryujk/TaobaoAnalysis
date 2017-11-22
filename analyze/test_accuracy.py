# -*- coding: utf-8 -*-

import codecs
import json

from snownlp import SnowNLP

from utils.path import *

total_contents = 0
total_correct = 0


def eval_classify(content, rate):
    snow = SnowNLP(content)
    sentiments = snow.sentiments
    _rate = -1 if sentiments < 0.4 else 1 if sentiments > 0.6 else 0
    
    global total_contents, total_correct
    total_contents += 1
    if _rate == rate:
        total_correct += 1
    

def parse_comment(comment):
    # -1差评，0中评，1好评
    rate = int(comment['rate'])
    
    for append in comment['appendList']:
        if append['content']:
            eval_classify(append['content'], rate)
    if comment['content']:
        eval_classify(comment['content'], rate)
    
    
def main():
    for filename in os.listdir(COMMENTS_DIR):
        path = os.path.join(COMMENTS_DIR, filename)
        if not os.path.isfile(path):
            continue
        print('Parsing', filename)
        
        with codecs.open(path, 'r', 'utf-8') as file:
            for line in file:
                data = json.loads(line)
                for comment in data['comments']:
                    parse_comment(comment)

    print('total_contents =', total_contents)
    print('total_correct =', total_correct)
    print('correct_rate =', total_correct / total_contents)
    # 68%正确率，运算超慢


if __name__ == '__main__':
    main()
