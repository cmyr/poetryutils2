# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import poetryutils2



end_tests = """
matttt mat
lolllllll loll
#WhyLiveee live
meleeee melee
suxxxx69 sux
"""
end_tests = [t.split() for t in end_tests.splitlines() if len(t)]
print(end_tests)
def test_end_words():
    for t in end_tests:
        r = poetryutils2.rhyme.get_rhyme_word(t[0])
        assert r == t[1], print(r)

print('passed end sound test')


def main():
    test_end_words()
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()


if __name__ == "__main__":
    main()