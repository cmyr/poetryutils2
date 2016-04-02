# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import poetryutils2


def haiku_test(sourcepath):
    '''sourcepath should be a path to a file of newline-delimited text'''
    lines = poetryutils2.utils.lines_from_file(sourcepath)
    haik = poetryutils2.Haikuer()

    filters = [
        poetryutils2.filters.url_filter,
        poetryutils2.filters.ascii_filter,
        poetryutils2.filters.low_letter_filter(0.9),
        poetryutils2.filters.real_word_ratio_filter(0.75)]

    source = poetryutils2.line_iter(lines, filters)

    for beauty in haik.generate_from_source(source):
        print(beauty)


def limerick_test(sourcepath):

    lines = poetryutils2.utils.lines_from_file(sourcepath)
    limer = poetryutils2.sorting.Limericker()

    for poem in limer.generate_from_source(lines):
        print(poem)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="demonstrates limericks & haiku")
    parser.add_argument('form', type=str, help="one of [limerick, haiku]")
    parser.add_argument('source', help='text file containing source lines')
    args = parser.parse_args()
    if args.form == 'haiku':
        func = haiku_test
    elif args.form == 'limerick':
        func = limerick_test
    else:
        raise Exception('unknown poem type %s' % args.form)

    func(args.source)


if __name__ == "__main__":
    main()
