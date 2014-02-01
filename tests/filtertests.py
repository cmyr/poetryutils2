from __future__ import print_function
from __future__ import unicode_literals
import poet.filters as filters
import functools
import nltk


def test_tricky_chars(tests):
    for t in tests:
        r = filters.tricky_characters(t, True)
        if r:
            print(t, r)

def test_hashtags(tests):
    print(filter(filters.contains_hashtag, tests))

def test_contains_url(tests):
    print(filter(filters.contains_url, tests))




    # all_fails = set()
    # for x in range(12):
    #     cutoff = (float(x)*0.1)
    #     print('\n\n', str(cutoff).center(40))
    #     fails = set([y for y,z in grades if z < cutoff])
    #     fails = fails.difference(all_fails)
    #     all_fails = all_fails.union(fails)

    #     for f in fails:
    #         print(f)

def test_low_letter_ratio(tests):

    all_fails = set()
    for i in range(1, 12):
        cutoff = float(i) * 0.1
        func = functools.partial(filters.low_letter_ratio, **{'cutoff':cutoff})

        fails = set(filter(func, tests))
        fails.difference_update(all_fails)
        all_fails.update(fails)
        print('\n\n', '%s / %d' % (str(cutoff).center(40), len(fails)))
        for f in fails:
            print(f)

        print('total fails:', len(all_fails))



def test_range_parsing():
    t1 = "1,2,3,4,5-9,21-26"
    a1 = (1,2,3,4,5,6,7,8,9,21,22,23,24,25,26)

    t1 = filters._parse_range_string(t1)
    assert t1 == a1, print(t1)

    t2 = "12-15, 16?"
    try:
        filters._parse_range_string(t2)
        assert(False)
    except ValueError as err:
        print(err)


def test_emoticons(tests):
    for t in tests:
        tt = filters.emoticons(t)
        if tt:
            print(tt)







def main():
    tests = lines_from_file('2ktst.txt')
    test_tricky_chars(tests)
    test_hashtags(tests)
    test_contains_url(tests)
    test_low_letter_ratio(tests)
    test_range_parsing()
    test_emoticons(tests)


if __name__ == "__main__":
    main()