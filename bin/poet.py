#!/usr/bin/env python

"""
poetry utilities
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import poetryutils2

# import filters
# import rhyme


def get_source_iter(filepaths):
    """chain together input files if necessary"""
    if len(filepaths) == 1:
        return open(filepaths[0])
    else:
        import itertools
        return itertools.chain.from_iterable([open(x) for x in filepaths])


def main(args=sys.argv):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('src', type=str, nargs='+', help="source file")
    parser.add_argument('-u', '--url-filter',
                        help='filter out lines containing urls', action='store_true')
    parser.add_argument('-a', '--ascii-filter',
                        help='filter out line with non-ascii characters', action='store_true')
    parser.add_argument('-n', '--numeral-filter',
                        help='filter out lines with numerals', action='store_true')
    parser.add_argument('-t', '--title-case-filter',
                        help='only tweets in title case', action='store_true')
    parser.add_argument('--re', type=str, help='regular expression filter')
    parser.add_argument('--blacklist', type=str, help='blacklisted words')
    parser.add_argument('-L', '--letter-ratio', type=float,
                        help='filter out tweets with low letter ratio')
    parser.add_argument('-R', '--real-word-ratio', type=float,
                        help='filter out tweets with low real-word ratio')
    parser.add_argument('--rhyme', type=str,
                        help='filter to lines that rhyme with input')
    parser.add_argument('-l', '--line-length', type=str,
                        help='allowed line lengths')
    parser.add_argument('-s', '--syllable-count', type=str,
                        help='allowed line syllables')
    parser.add_argument('-i', '--ignore-case',
                        help='regex is case-insensitive', action='store_true')

    args = parser.parse_args()
    poet_filters = []

    if not args.src:
        print('please specify a source file')

    if args.title_case_filter:
        poet_filters.append(poetryutils2.filterstitle_case_filter)
    if args.line_length:
        poet_filters.append(
            poetryutils2.filtersline_length_filter(args.line_length))
    if args.blacklist:
        blacklist = args.blacklist.split(',')
        print('blacklist: %s' % repr(blacklist))
        poet_filters.append(poetryutils2.filters.blacklist_filter(blacklist))
    if args.ascii_filter:
        poet_filters.append(poetryutils2.filters.ascii_filter)
    if args.numeral_filter:
        poet_filters.append(poetryutils2.filters.numeral_filter)
    if args.letter_ratio:
        poet_filters.append(
            poetryutils2.filters.low_letter_filter(args.letter_ratio))
    if args.url_filter:
        poet_filters.append(poetryutils2.filters.url_filter)
    if args.real_word_ratio:
        poet_filters.append(
            poetryutils2.filters.real_word_ratio_filter(args.real_word_ratio))
    if args.re:
        poet_filters.append(
            poetryutils2.filters.regex_filter(args.re, args.ignore_case))

    if args.syllable_count:
        poet_filters.append(
            poetryutils2.filters.syllable_count_filter(args.syllable_count))

    if args.rhyme:
        poet_filters.append(poetryutils2.filters.rhyme_filter(args.rhyme))

    # print(args.src)
    # return
    # paths = args.src
    source = get_source_iter(args.src)
    return poetryutils2.line_iter(source, poet_filters)


        # i'm not entirely sure how to close() our input, files trapped in
        # chain -_-`

# def main():
#     pass


if __name__ == "__main__":
    for l in main():
        print(l.rstrip())
