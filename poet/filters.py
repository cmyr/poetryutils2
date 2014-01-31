from __future__ import print_function
from __future__ import unicode_literals
import re
import functools

"""
various filters for operating on a list of strings (tweets, mainly)
a philosophical question: should a filter return True when an item
passes, or when it fails?
"""

# simple filters:
def contains_url(text):
    if re.search(r'http://[a-zA-Z0-9\./]*\w', text):
        return True
    else:
        return False


def contains_screenname(text):
    if re.search(r'@[a-zA-Z0-9]+', text):
        return True
    else:
        return False

def contains_hashtag(text):
    if re.search(r'#[a-zA-Z0-9]+', text):
        return True
    else:
        return False

def contains_numerals(text):
    if re.search(r'[0-9]', text):
        return True

    return False

def tricky_characters(text, debug=False):
    """
    treat as a bool, need to look up counting unicode chars
    """

    count = len(re.findall(ur'[\u0080-\u024F]', text))
    if count and debug:
        print()
        print(re.findall(ur'[\u0080-\u024F]', text))
    return count


#variable filters:

def low_letter_ratio(text, cutoff=0.8):
    t = re.sub(r'[^a-zA-Z ]', '', text)
    if (float(len(t)) / len(text)) < cutoff:
        return True
    return False

def low_letter_filter(cutoff):
    assert(0.0 < cutoff < 1.0):
    return functools.partial(low_letter_ratio, **{'cutoff': cutoff})

def blacklist_filter(text, blacklist):
    for word in (_strip_string(w) for w in text.split()):
        if word in blacklist:
            return True
    return False

def _strip_string(text):
    """
    for removing punctuation for certain tests
    """

    return re.sub(r'[^a-zA-Z]', '',  text).lower()


def real_word_ratio(sentance, debug=False):
    """
    is not currently pass/fail
    """
    if not hasattr(real_word_ratio, "words"):
        real_word_ratio.words = set(w.lower() for w in nltk.corpus.words.words())
    # sentance = format_input(sentance)
    sentance = de_camel(sentance)

    sentance = re.sub(r'[#,\.\?\!]', '', sentance)
    sentance_words = [w.lower() for w in sentance.split()]
    if not len(sentance_words):
        return 0

    are_words = [w for w in sentance_words if w in real_word_ratio.words]

    ratio = float(len(''.join(are_words))) / len(''.join(sentance_words))
    if debug:
        print('debugging real word ratio:')
        print(sentance, sentance_words, are_words, ratio, sep='\n')
    return ratio

def emoticons(text):
    pass


def main():
    pass
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()


if __name__ == "__main__":
    main()