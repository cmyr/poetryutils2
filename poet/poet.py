from __future__ import print_function
import filters


"""
a proper refactoring of poetry utils
first off: input
input can be either:
    - a file
    - an iter of a) strings or b) dicts
    - if dicts, must include a getattr key


in this final case, 
"""


def get_lines(source, filters, line_key=None):
    for item in source:
        if isinstance(item, basestring):
            line = item
        else:
            if not line_attr:
                print('non-string sources require a line_key')
                return
            line = item[line_key]

        if filter_line(line, filters):
            yield line


def filter_line(line, filters):
    for f in filters:
        if f(line):
            return False

    return True

    # so we want, basically, to chain together filters somehow?


def main():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('src', type=str, help="source file")
    parser.add_argument('-u', '--url-filter',
                        help='filter out lines containing urls', action='store_true')
    parser.add_argument('-a', '--ascii-filter',
                        help='filter out line with non-ascii characters', action='store_true')
    parser.add_argument('--re', type=str, help='regular expression filter')
    parser.add_argument('--blacklist', type=str, help='blacklisted words')
    parser.add_argument('-L', '--letter-ratio', type=float,
                        help='filter out tweets with low letter ratio')
    parser.add_argument('-R', '--real-word-ratio', type=float,
                        help='filter out tweets with low real-word ratio')
    parser.add_argument('-l', '--line-length', type=str,
                        help='allowed line lengths')
    parser.add_argument('-i', '--ignore-case',
                        help='regex is case-insensitive', action='store_true')

    args = parser.parse_args()
    poet_filters = []
    if not args.src:
        print('please specify a source file')
        sys.exit(1)

    # unpack args.src
    source = open(args.src)

    if args.url_filter:
        poet_filters.append(filters.url_filter)
    if args.line_length:
        poet_filters.append(filters.line_length_filter(args.line_length))
    if args.blacklist:
        blacklist = args.blacklist.split(',')
        print('blacklist: %s' % repr(blacklist))
        poet_filters.append(filters.blacklist_filter(blacklist))
    if args.ascii_filter:
        poet_filters.append(filters.tricky_char_filter)
    if args.letter_ratio:
        poet_filters.append(filters.low_letter_filter(args.letter_ratio))
    if args.real_word_ratio:
        poet_filters.append(
            filters.real_word_ratio_filter(args.real_word_ratio))
    if args.re:
        poet_filters.append(filters.regex_filter(args.re, args.ignore_case))

    for l in get_lines(source, poet_filters):
        print(l.rstrip())

    source.close()


if __name__ == "__main__":
    main()
