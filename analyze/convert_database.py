# -*- coding: utf-8 -*-

import codecs
import json
from datetime import datetime

from utils.database import session, Item, Review
from utils.path import COMMENTS_DIR


def parse_comment(comment):
    date = (datetime.strptime(comment['date'], '%Y年%m月%d日 %H:%M')
            if comment['date'] else None)
    appends = [i['content'] for i in comment['appendList']]
    appends = '\n'.join(appends)
    review = Review(  # id=comment['rateId'],  # 有冲突？
                    raw=json.dumps(comment),
                    rate=comment['rate'],
                    content=comment['content'],
                    date=date,
                    appends=appends,
                    user_rank=comment['user']['rank'] if comment['user'] else None
                    )
    return review
    
    
def main():
    import os

    for filename in os.listdir(COMMENTS_DIR):
        path = os.path.join(COMMENTS_DIR, filename)
        if not os.path.isfile(path) or not filename.endswith('.txt'):
            continue
        split = filename.split(' ', maxsplit=1)
        item_id = int(split[0])
        title = split[1][:-8]

        print('Parsing', filename)

        # 商品
        item = Item(id=item_id,
                    title=title
                    )
        session.add(item)
        session.commit()

        # 评论
        with codecs.open(path, 'r', 'utf-8') as file:
            reviews = []
            for line in file:
                data = json.loads(line)
                for comment in data['comments']:
                    review = parse_comment(comment)
                    review.item_id = item_id
                    reviews.append(review)
            session.add_all(reviews)
            session.commit()


if __name__ == '__main__':
    main()
