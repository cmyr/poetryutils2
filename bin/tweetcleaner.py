# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


import sys
import re
import poetryutils2


"""this is a utility for filtering unsorted tweets fomr a DBM file
into something appropriate for some of this poetry stuff."""


def dbm_iter(dbpath):
    try:
        import gdbm
    except ImportError:
        print('database manipulation requires gdbm')

    db = gdbm.open(dbpath)
    k = db.firstkey()
    # ignore first key, which is metadata
    k = db.nextkey(k)
    try:
        while k:
            tweet = _tweet_from_dbm(db[k])
            if tweet:
                yield tweet['tweet_text']
            k = db.nextkey(k)
    finally:
        # print('finally called', file=sys.stderr)
        db.close()

    # print('finished yielding tweets')
    raise StopIteration



def _tweet_from_dbm(dbm_tweet):
    
    try:
        tweet_values = re.split(unichr(0017), dbm_tweet.decode('utf-8'))
        t = dict()
        t['tweet_id'] = int(tweet_values[0])
        t['tweet_hash'] = tweet_values[1]
        t['tweet_text'] = tweet_values[2]
        return t
    except ValueError:
        return None

def clean_tweets(tweet_iter, filters):
    total_count = 0
    filtered_count = 0

    for line in tweet_iter:
        total_count += 1
        if poetryutils2.filter_line(line, filters):
            filtered_count += 1
            yield line

    pass_percent = float(filtered_count)/float(total_count)
    print("%d of %d tweets passed filters (%0.2f%%)" %
            (filtered_count, total_count, pass_percent), file=sys.stderr)
    raise StopIteration


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dbpath', type=str, help="path for db to filter")

    args = parser.parse_args()

    db_path = args.dbpath

    filters = [
    poetryutils2.filters.url_filter,
    poetryutils2.filters.line_length_filter("0-80"),
    poetryutils2.filters.real_word_ratio_filter(0.8),
    poetryutils2.filters.hashtag_filter,
    poetryutils2.filters.multi_line_filter
    ]

    for tweet in clean_tweets(dbm_iter(db_path), filters):
        print(tweet.encode('utf8'))






if __name__ == "__main__":
    main()