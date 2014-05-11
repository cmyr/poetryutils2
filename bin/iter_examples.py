# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

def example_haiku_iter():
    source = '/Users/cmyr/Dev/projects/poetryutils2/sources/mayhaiku.txt'
    with open(source) as f:
        haiku = list()
        for line in f:
            if len(line.rstrip()):
                haiku.append(line)
            if len(haiku) == 3:
                yield tuple(haiku)
                haiku = list()


def test_haiku():
    for poem in example_haiku_iter():
        print(poem)

if __name__ == "__main__":
    test_haiku()