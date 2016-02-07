import string
import re
import os
# from . import special_syllables

from . import utils
from .special_syllables import special_syllables_en


fallback_cache = dict()

fallback_subsyl = ["cial", "tia", "cius", "cious", "gui", "ion", "iou",
                   "sia$", ".ely$"]

fallback_addsyl = ["ia", "riet", "dien", "iu", "io", "ii",
                   "[aeiouy]bl$", "mbl$",
                   "[aeiou]{3}",
                   "^mc", "ism$",
                   "(.)(?!\\1)([aeiouy])\\2l$",
                   "[^l]llien",
                   "^coad.", "^coag.", "^coal.", "^coax.",
                   "(.)(?!\\1)[gq]ua(.)(?!\\2)[aeiou]",
                   "dnt$"]


# Compile our regular expressions
for i in range(len(fallback_subsyl)):
    fallback_subsyl[i] = re.compile(fallback_subsyl[i])
for i in range(len(fallback_addsyl)):
    fallback_addsyl[i] = re.compile(fallback_addsyl[i])


def _normalize_word(word):
    return word.strip().lower()

# Read our syllable override file and stash that info in the cache
for line in special_syllables_en:
    if line:
        toks = line.split()
        assert len(toks) == 2
        fallback_cache[_normalize_word(toks[0])] = int(toks[1])


def syllables_in_number(number):
    # yes I'm inelegant
    # main special-case: the teens
    pass

def count_syllables(sentance, debug=False, cutoff=None):
    # first lets strip out punctuation and emotive marks
    count = 0

    try:
        sentance = _format_input(sentance)
    except TypeError:
        # bad input
        return 0

    if debug:
        print('received sentance: %s' % sentance)
        print('formatted sentance: %s' % sentance)

    words = [w for w in sentance.split() if w.isalpha()]

    if debug:
        print('extracted words: %s' % repr(words))
        nonwords = [w for w in sentance.split() if not w.isalpha()]
        if nonwords:
            print('found nonwords: %s' % repr(words))

    for w in words:
        # if is_camel(w):
        #     sylls = count_syllables(de_camel(w))
        # else:
        sylls = _count(w)

        count += sylls
        if cutoff and count > cutoff:
            return
            # what do we want to return, in this case?

        if debug:
            print('%s\t\t\t%d' % (w, sylls))

    if debug:
        print('total\t\t\t%d' % count)
    return count


# def _format_input(sentance):
    # """formatting for syllable counting"""
    # text = utils.fix_hashtags(sentance)
    # text = re.sub(r'&', ' and ', text) #  handle ampersands
    # text = re.sub(r'http://[a-zA-Z0-9\./]*\w', '(link)', text) # remove links
    # text = re.sub(r'(\w)\'(\w)', r'\1\2', text) # contract it's, isn't, wasn't etc.
    # text = re.sub(r'[,#!;~\?\.\'\"\:\(\)\-]', ' ', text)  # remove punctuation
    # text = re.sub(r' +', ' ', text)  # redudent spaces
    # return text

LINK_RE = re.compile(r'http://[a-zA-Z0-9\./]*\w')
APOST_RE = re.compile(r'(\w)\'(\w)')
PUNCT_RE = re.compile(r'[,#!;~\?\.\'\"\:\(\)\-\*]')


def _format_input(sentance):
    text = utils.fix_hashtags(sentance)
    text = re.sub(r'&', ' and ', text)  # handle ampersands
    text = LINK_RE.sub('(link)', text)  # remove links
    text = APOST_RE.sub(r'\1\2', text)  # contract it's, isn't, wasn't etc.
    text = PUNCT_RE.sub(' ', text)  # remove punctuation
    text = re.sub(r'[^a-zA-Z ]', '', text) # remove everything else
    text = re.sub(r' +', ' ', text)  # redudent spaces
    return text


def _count(word, debug=False):
    # global fallback_cache

    word = _normalize_word(word)
    orig_word = word

    if not word:
        return 0

    # Check for a cached syllable count
    count = fallback_cache.get(orig_word, -1)
    if count > 0:
        return count

    # Remove final silent 'e'
    if word[-1] == "e":
        word = word[:-1]

    # Count vowel groups
    count = 0
    prev_was_vowel = 0
    for c in word:
        is_vowel = c in ("a", "e", "i", "o", "u", "y")
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel

    # Add & subtract syllables
    for r in fallback_addsyl:
        if r.search(word):
            count += 1
    for r in fallback_subsyl:
        if r.search(word):
            count -= 1

    # Cache the syllable count

    if count == 0:
        count = 1

    fallback_cache[orig_word] = count
    
    return count

#
# Phoneme-driven syllable counting
#

# def count_decomp(decomp):
#     count = 0
#     for unit in decomp:
#         if gnoetics.phoneme.is_xstressed(unit):
#             count += 1
#     return count
