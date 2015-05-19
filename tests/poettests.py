# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import os
import poetryutils2 as poetry

testfile = os.path.expanduser("~/tweetdbm/may09.txt")

def testBase(poet=None):
    print("testing", poet)
    if poet == None:
        poet = poetry.sorting.Poet()
    with open(testfile) as f:
        for poem in poet.generate_from_source(f.readlines()):
            print(poem.pretty_print())

def testRhymer():
    poet = poetry.sorting.Rhymer()
    testBase(poet)

def testCouplets():
    poet = poetry.sorting.Coupler()
    testBase(poet)

def testLimericks():
    testBase(poetry.sorting.Limericker())

def testHaikuer():
    testBase(poetry.sorting.Haikuer())    

def testSyllablePoet():
    testBase(poetry.sorting.SyllablePoet(line_syllables=[5, 7, 5]))

def testConcretePoet():
    testBase(poetry.sorting.Concrete())        

def testMultiPoet():
    poet = poetry.sorting.Poet()
    print(poet.poem_type)
    poets = [poetry.sorting.Limericker(), poetry.sorting.Haikuer()]
    multi = poetry.sorting.MultiPoet(poets=poets)
    # print(multi)
    # return
    testBase(multi)
    # poetry.sorting.Coupler()
if __name__ == "__main__":
    testMultiPoet()