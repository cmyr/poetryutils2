# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import sys

import poetryutils2
from collections import defaultdict


def couplet_iter(source):
    coupler = poetryutils2.Coupler()
    seen = 0
    for line in source:
        seen += 1
        result = coupler.add_line(line)
        if result:
            yield result
            print('seen %d' % seen, file=sys.stderr)


    def debug(self):
        for k in self.rhymers:
            self.rhymers[k].debug()




def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dbpath', type=str, help="path for db to filter")

    args = parser.parse_args()

    file_path = args.dbpath


def tests():
    definite_passes = [
    'one two four five',
    'you feel alive']

    lines = poetryutils2.utils.debug_lines()
    lines = poetryutils2.utils.lines_from_file('/Users/cmyr/tweetdbm/may2k.txt')
    lines.extend(definite_passes)
 
    for couplet in couplet_iter(lines):
        # print(couplet[0], '\n', couplet[1])
        poem = '%s\n%s' % (couplet[0], couplet[1])
        print(poem.encode('utf8'))


    # coupler.debug()


if __name__ == "__main__":
    # main()
    tests()