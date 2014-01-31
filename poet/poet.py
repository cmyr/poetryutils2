from __future__ import print_function


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
        if not f(line):
            return False

    return True

    # so we want, basically, to chain together filters somehow?


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('arg1', type=str, help="required argument")
    parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    args = parser.parse_args()


if __name__ == "__main__":
    main()