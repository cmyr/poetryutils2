from __future__ import print_function
from __future__ import unicode_literals

import re
import functools
import random

from . import utils
from . import syllables
from . import rhyme
from . import wordsets


"""
various filters for operating on a list of strings (tweets, mainly)
a philosophical question: should a filter return True when an item
passes, or when it fails?
"""

# simple filters:


def url_filter(text):
    """filters out urls"""
    if re.search(r'http://[a-zA-Z0-9\./]*\w', text):
        return True
    else:
        return False


def screenname_filter(text):
    """filters out @names"""
    if re.search(r'@[a-zA-Z0-9]+', text):
        return True
    else:
        return False


def hashtag_filter(text):
    """filters out hashtags"""
    if re.search(r'#[a-zA-Z0-9]+', text):
        return True
    else:
        return False


def numeral_filter(text):
    """filters text containing numerals"""
    if re.search(r'[0-9]', text):
        return True

    return False

def title_case_filter(text):
    if not text.istitle():
        return True

    return False

# def tricky_characters(text, debug=False):
#     """
#     treat as a bool, need to look up counting unicode chars
#     """

#     count = len(re.findall(ur'[\u0080-\u024F]', text))

#     if count and debug:
#         print(re.findall(ur'[\u0080-\u024F]', text))
#     return count


# def tricky_char_filter(text):
#     if tricky_characters(text):
#         return True
#     return False

def ascii_filter(text):
    """filters out non-ascii text"""
    try:
        text.decode('ascii')
    except UnicodeEncodeError:
        return True
    return False

# variable filters:


def blacklist_check(text, blacklist, leakage=0):
    """filter words from a blacklist"""
    assert 0.0 <= leakage < 1.0, 'illegal value in blacklist check'

    for word in (utils._strip_string(w) for w in text.split()):
        if word in blacklist:
            if leakage:
                leak_chance = leakage * 100  # %
                leak = random.randrange(0, 100)
                if leak > leak_chance:
                    return False
            return True
    return False


def blacklist_filter(blacklist):
    assert(len(blacklist))
    assert isinstance(blacklist, set) or isinstance(blacklist, list)

    f = functools.partial(blacklist_check, **{'blacklist': blacklist})
    f.__doc__ = "filtering words: %s" % repr(blacklist)
    return f

def swears_filter(leakage=0):
    kwargs = {'blacklist': wordsets.swears, 'leakage': leakage}
    return functools.partial(blacklist_check, **kwargs)


def low_letter_ratio(text, cutoff=0.8):
    t = re.sub(r'[^a-zA-Z ]', '', text)
    try:
        if (float(len(t)) / len(text)) < cutoff:
            return True
    except ZeroDivisionError:
        pass
    return False


def low_letter_filter(cutoff):
    assert(0.0 < cutoff < 1.0)
    f = functools.partial(low_letter_ratio, **{'cutoff': cutoff})
    f.__doc__ = "filtering tweets with letter ratio below %0.2f" % cutoff
    return f


def line_length_check(text, line_lengths):
    if len(text) in line_lengths:
        return False
    return True


def line_length_filter(line_lengths):
    """
    line_lengths should be a string of format 0,1,5-8.
    this would represent lengths 0,1,5,6,7,8.
    line lengths can also be a tuple of ints.
    """
    lengths = _parse_range_string(line_lengths)
    if not len(lengths):
        raise ValueError("no line lengths received")

    f = functools.partial(line_length_check, **{'line_lengths': lengths})
    f.__doc__ = "filtering line lengths to %s" % repr(lengths)
    return f


def syllable_count_check(text, syllable_counts, max_syllables):
    count = syllables.count_syllables(text, cutoff=max_syllables)
    if count in syllable_counts:
        return False

    return True


def syllable_count_filter(syllable_counts):
    counts = _parse_range_string(syllable_counts)
    if not len(counts):
        raise ValueError("please specify a range of syllable counts")

    kwargs = {'syllable_counts': counts, 'max_syllables': max(counts)}
    f = functools.partial(syllable_count_check, **kwargs)
    f.__doc__ = "filtering syllable counts to %s" % repr(counts)
    return f

def _parse_range_string(range_string):
    """
    parses strings that represent a range of ints.
    """

    if re.search(r'[^,0-9\-]', range_string):
        raise ValueError("invalid characters in range")

    result = set(int(x) for x in re.findall(r'[0-9]+', range_string))
    ranges = re.findall(r'([0-9]+)\-([0-9]+)', range_string)
    if len(ranges):
        for r in ranges:
            result.update([x for x in range(int(r[0]), int(r[1]) + 1)])

    return tuple(result)


def regex_check(text, pattern, ignore_case):
    if ignore_case and re.search(pattern, text, flags=re.I):
        return False
    elif not ignore_case and re.search(pattern, text):
        return False
    return True


def regex_filter(pattern, ignore_case):
    pattern = _convert_custom_regex(pattern)
    kwargs = {'pattern': pattern, 'ignore_case': ignore_case}
    f = functools.partial(regex_check, **kwargs)
    f.__doc__ = "regex pattern: %s" % pattern
    if ignore_case:
        f.__doc__ += " (case-insensitive)"

    return f


def real_word_ratio(sentance, debug=False, cutoff=None):
    """
    becomes pass/fail if cutoff is not None
    """
    # if not hasattr(real_word_ratio, "words"):
    #     real_word_ratio.words = utils.wordlist()

    sentance = utils.fix_hashtags(sentance)

    sentance = re.sub(r'[#,\.\?\!]', '', sentance)
    sentance_words = [w.lower() for w in sentance.split()]
    if not len(sentance_words):
        return 0

    are_words = [w for w in sentance_words if utils.is_real_word(w)]
    # debuging:
    # not_words = set(sentance_words).difference(set(are_words))

    ratio = float(len(''.join(are_words))) / len(''.join(sentance_words))

    # pass/fail
    if cutoff > 0:
        if ratio < cutoff:
            return True
        else:
            return False

    if debug:
        print('debugging real word ratio:')
        print(sentance, sentance_words, are_words, ratio, sep='\n')
    return ratio




def real_word_ratio_filter(cutoff):
    f = functools.partial(real_word_ratio, **{'cutoff': cutoff})
    f.__doc__ = "filtering real-word-ratio with cutoff %0.2f" % cutoff
    return f


def rhymes_with_word(text, word):
    rhyme_word = rhyme.rhyme_word(text)
    if rhyme.words_rhyme(rhyme_word, word):
        return False
    return True

def rhyme_filter(word):
    f = functools.partial(rhymes_with_word, **{'word': word})
    f.__doc__ = "filtering for rhymes with %s" % word
    return f



def emoticons(text):
    # non functional
    emotes = re.findall(r'[=:;].{0,2}[\(\)\[\]\{\}|\\\$DpoO0\*]+', text)
    return emotes


def _convert_custom_regex(in_re):
    """
    takes a string in our custom regex format
    and converts it to acceptable regex 
    """
    regex = re.sub(r'([^\\])(?:~)([a-zA-Z]*)',
                   lambda m: '%s(%s)' % (m.group(1), '|'.join(utils.synonyms(m.group(2)))),
                   in_re)  # expand '~word' to a (list|of|synonyms)

    regex = re.sub(r'\\~', '~', regex)  # replace escaped tildes
    return regex


def main():
    pass


if __name__ == "__main__":
    main()
