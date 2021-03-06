# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


import sys
import re
import poetryutils2
import os


"""this is a utility for filtering unsorted tweets fomr a DBM file
into something appropriate for some of this poetry stuff."""


def dbm_iter(dbpath):
    try:
        import gdbm
    except ImportError:
        print('database manipulation requires gdbm')

    db = gdbm.open(dbpath)
    k = db.firstkey()
    if not k:
        print('failed to find first key', file=sys.stderr)
        raise StopIteration
    # ignore first key, which is metadata
    last_k = k
    k = db.nextkey(k)
    try:
        while k:
            if k == last_k:
                print('breaking on key loop for key %s' % k, file=sys.stderr)
                break
            last_k = k
            try:
                tweet = _tweet_from_dbm(db[k])
                if tweet:
                    yield tweet['tweet_text']
                k = db.nextkey(k)
            except KeyError:
                k = db.nextkey(k)
                continue
    finally:
        db.close()

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

    if total_count == 0:
        total_count = 1
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
    # poetryutils2.filters.url_filter,
    # poetryutils2.filters.line_length_filter("0-80"),
    # poetryutils2.filters.real_word_ratio_filter(0.8),
    # poetryutils2.filters.hashtag_filter,
    poetryutils2.filters.multi_line_filter,
    poetryutils2.filters.just_emoji_filter
    ]

    paths = list()
    if os.path.isdir(db_path):
        paths = [os.path.join(db_path, p) for p in os.listdir(db_path) if p.endswith(".db")]
    else:
        paths.append(db_path)

    for dbm_file in paths:
        print(dbm_file, file=sys.stderr)
        for tweet in clean_tweets(dbm_iter(dbm_file), filters):
            print(tweet.encode('utf8'))


if __name__ == "__main__":
    main()
