# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import re
import random

from collections import defaultdict

import poetryutils2


_DEBUG = True


def make_art(source, filters):
    
    lines = get_lines(source, filters)
    nines = relevant_lines(lines[9], 3)
    fives = relevant_lines(lines[6], 2)

    random.shuffle(nines)
    random.shuffle(fives)

    poems = list()
    while len(nines) and len(fives):
        n = nines.pop()
        f = fives.pop()
        poem = n[0] + n[1] + f[0] + f[1] + n[2]

        poems.append(poem)

    return poems

def get_lines(source, filters):
    syllables = (6,9)
    lines = defaultdict(list)

    for line in poetryutils2.line_iter(source, filters):
        c = poetryutils2.count_syllables(line)

        if c in syllables:
            lines[c].append(line)

    return lines

def relevant_lines(lines, set_size):
    # return the lines we want, as a tuple
    lines = poetryutils2.rhyme.rhymes_for_lines(lines)
    lines = [l for l in lines if len(l) >= set_size]
    if _DEBUG:
        print('found %d lines' % len(lines))

    return rhyme_sets_for_rhymes(lines, set_size)
    

def rhyme_sets_for_rhymes(rhymes, set_size):
    # this is ugllly :-(


    # okay so we have a list of rhymes, sorted into homophones.
    # ie: r1,r1,r1,r1,r1,r2,r2,r2,r2,r3,r3,r4,r5,r6
    rhyme_sets = list()
    
    for r in rhymes:
        rhyme_lines = list()
        if len(r) < set_size:
            # i.e if we can't make a non-homophonic match
            continue

        r.sort(key=len, reverse=True)

        ind = 0
        while len(r) >= set_size:
            # print('down here', ind, len(r))
            if ind >= len(r):
                ind = 0
            try:
                # print('items for ind:', len(r[ind]))
                rhyme_lines.append(r[ind].pop())
                ind += 1
            except IndexError:
                # print('index error')
                r.pop(ind)
                continue

        rhyme_sets.extend(group_rhymes(rhyme_lines, set_size))

    return rhyme_sets


def group_rhymes(rhyme_lines, set_size):
    rhyme_sets = list()
    # sort them into groups
    while len(rhyme_lines):
        rhyme_set = list()
        for i in range(set_size):
            try:
                rhyme_set.append(rhyme_lines.pop())
            except IndexError:
                break
        if len(rhyme_set) == set_size:
            rhyme_sets.append(tuple(rhyme_set))

    return rhyme_sets



def _validate_schema(schema):
    schema = schema.split()
    scheme_description = []

    for idx, line in enumerate(schema):
        syllables = re.findall(r'^[0-9]+', schema)
        rhyme = re.findall(r'[A-Z]', schema)
        if len(syllables) > 1 or len(rhyme) > 1:
            print('invalid descriptor %s in schema %s' % (line, schema))

        syllables = None if not len(syllables) else syllables[0]
        rhyme = None if not len(rhyme) else rhyme[0]
            

        scheme_description.append((syllables,rhyme))



TEST_PATH =  '/Users/cmyr/Dev/projects/poetryutils2/tests/100k.tst'

TEST_FILTERS = [
    poetryutils2.filters.numeral_filter,
    poetryutils2.filters.ascii_filter,
    poetryutils2.filters.url_filter,
    poetryutils2.filters.real_word_ratio_filter(0.9)
    ]

def main():
    if _DEBUG:
        sourcepath = '/Users/cmyr/tweetdbm/may09.txt'
        # sourcepath = '/Users/cmyr/Dev/projects/poetryutils2/tests/100k.tst'
        # scheme='9a 9a 5b 5b 9a'


    filters = [
    poetryutils2.filters.numeral_filter,
    poetryutils2.filters.ascii_filter,
    poetryutils2.filters.url_filter,
    poetryutils2.filters.real_word_ratio_filter(0.85)
    ]
    source = open(sourcepath)

    art = make_art(source, filters)
    for a in art:
        print('\n\n')
        print(a)
        # for line in a:
        #     print(line)



    source.close()
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()


if __name__ == "__main__":
    main()