from __future__ import print_function
from __future__ import unicode_literals

import re
import functools

import Stemmer

import utils
import syllables


"""
various filters for operating on a list of strings (tweets, mainly)
a philosophical question: should a filter return True when an item
passes, or when it fails?
"""

# simple filters:


def url_filter(text):
    if re.search(r'http://[a-zA-Z0-9\./]*\w', text):
        return True
    else:
        return False


def screenname_filter(text):
    if re.search(r'@[a-zA-Z0-9]+', text):
        return True
    else:
        return False


def hashtag_filter(text):
    if re.search(r'#[a-zA-Z0-9]+', text):
        return True
    else:
        return False


def numeral_filter(text):
    if re.search(r'[0-9]', text):
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
    try:
        text.decode('ascii')
    except UnicodeEncodeError:
        return True
    return False

# variable filters:
def blacklist_check(text, blacklist):
    for word in (utils._strip_string(w) for w in text.split()):
        if word in blacklist:
            return True
    return False


def blacklist_filter(blacklist):
    assert(len(blacklist))
    return functools.partial(blacklist_check, **{'blacklist': blacklist})


def low_letter_ratio(text, cutoff=0.8):
    t = re.sub(r'[^a-zA-Z ]', '', text)
    if (float(len(t)) / len(text)) < cutoff:
        return True
    return False


def low_letter_filter(cutoff):
    assert(0.0 < cutoff < 1.0)
    return functools.partial(low_letter_ratio, **{'cutoff': cutoff})


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

    return functools.partial(line_length_check, **{'line_lengths': lengths})


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
    return functools.partial(syllable_count_check, **kwargs)



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
    return functools.partial(regex_check, **kwargs)


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

    are_words = [w for w in sentance_words if is_real_word(w)]
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


STEMMER = Stemmer.Stemmer('english')


def is_real_word(word):
    assert isinstance(word, unicode), 'word "%s" not unicode' % word
    if not hasattr(is_real_word, "words"):
        is_real_word.words = utils.wordlist()
        print('loaded %d words' % len(is_real_word.words))

    if word in is_real_word.words:
        return True

  # now this is a bunch of stemming handlers for plurals and tenses etc.
    if word[-1] =='s':
        # cheap handling of plurals not in our dict
        return is_real_word(word[:-1])
    elif word[-1] in {'g', 'd', 's', 'r', 't'}:
        # cheap handling of gerunds not in our dict.
        # this won't do great for nouns ending in e
        # print('degerunding: %s' % word)
        # if re.search(r'ing$', word):
        #     word = word[:-3]
        #     print('trying %s' % word)
        #     if is_real_word(word):
        #         print('success')
        #         return True
        #     else:
        #         word = word + 'e'
        #         print('trying %s' % word)
        #         if is_real_word(word):
        #             print('success')
        #             return True
        stem = STEMMER.stemWord(word)
        if stem != word:
            result = is_real_word(stem)
            if result:
                return True

            if stem[-1] == 'i':
                # sacrificing 'skiing' for the common good
                stem = stem[:-1] + 'y'
                return is_real_word(stem)

            stem += 'e'
            result = is_real_word(stem)
            if result:
                return True

            print('trying stem %s for word %s' % (stem, word))
            
 
    return False

def real_word_ratio_filter(cutoff):
    return functools.partial(real_word_ratio, **{'cutoff': cutoff})


def emoticons(text):
    # non functional
    emotes = re.findall(r'[=:;].{0,2}[\(\)\[\]\{\}|\\\$DpoO0\*]+', text)
    return emotes


def _convert_custom_regex(in_re):
    """
    takes a string in our custom regex format
    and converts it to acceptable regex 
    """
    regex = re.sub(r'(?:[^\\]~|\A~)([a-zA-Z]*)',
                   lambda m: '(%s)' % '|'.join(utils.synonyms(m.group(1))),
                   in_re)  # expand '~word' to a (list|of|synonyms)

    regex = re.sub(r'\\~', '~', regex)  # replace escaped tildes
    return regex


def main():
    pass


if __name__ == "__main__":
    main()
