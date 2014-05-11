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


def example_limerick_iter():
    source = '/Users/cmyr/Dev/projects/poetryutils2/sources/maylimericks.txt'
    with open(source) as f:
        limerick = list()
        for line in f:
            if len(line.rstrip()):
                limerick.append(line)
            if len(limerick) == 5:
                yield tuple(limerick)
                limerick = list()



def test_haiku():
    for poem in example_haiku_iter():
        print(poem)

def test_limericks():
    for poem in example_limerick_iter():
        print(poem)


if __name__ == "__main__":
    test_haiku()
    test_limericks()