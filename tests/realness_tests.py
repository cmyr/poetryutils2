# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import re

import poetryutils2
# this is all for use within ipython


def sample_words():
    lines = poetryutils2.utils.debug_lines()
    words = list()
    for l in lines:
        words.extend(w.lower() for w in l.split())


# maybe we want to clean words up more? let's just do that I think

    # words = [w[:-1] for w in words if w[-1] in {'.',',','!','?'}]
    # tofix = [w for w in words if w[-1] in {'.',',','!','?'}]
    # words = [w for w in words if w[-1] not in {'.',',','!','?'}]

    # words.extend([w[:-1] for w in tofix])
    words = [re.sub(r'[^a-zA-Z\']', '', w) for w in words]

    return [w for w in words if len(w)]


def realness(sample):
    fails = [w for w in sample if not poetryutils2.utils.is_real_word(w)]
    return fails

def main():
    # print(len(sample_words()))
    sample = sample_words()
    print(len(sample))

    fails = realness(sample)
    # for f in fails:
    #     print(f)

    from collections import Counter
    counter = Counter(fails)

    for word, count in counter.most_common():
        if count > 1:
            print(word, count)
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()

"""
okay so what we're having trouble with:
-est
-ies
-py

"""

if __name__ == "__main__":
    main()