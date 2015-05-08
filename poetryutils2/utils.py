from __future__ import print_function
from __future__ import unicode_literals
import re
import os
import time
# import Stemmer

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# helpers etc

def _strip_string(text):
    """
    for removing punctuation for certain tests
    """

    return re.sub(r'[^a-zA-Z]', '',  text).lower()


# def _de_camel(word):
#     s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', word)
#     return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()


HASHTAG_RE = re.compile(r'#(?:[A-Z][a-z]+)+')
HASHTAG_SUB1 = re.compile(r'([#a-z])([A-Z][a-z]+)')
HASHTAG_SUB2 = re.compile(r'([a-z0-9])([A-Z])')


def fix_hashtags(text):
    if not isinstance(text, basestring):
        print(text)
        return False
        
    hashtags = HASHTAG_RE.findall(text)
    for h in hashtags:
        fix = HASHTAG_SUB1.sub(r'\1 \2', h)
        fix = HASHTAG_SUB2.sub(r'\1 \2', fix).lower()
        text = re.sub(h, fix, text, count=1)
    return text

# def sub_non_latin_chars(text):
#     return re.sub(ur'[\u00FF-\u024F]', '', text)

def _find_hashtags(text):
    hashtags = re.findall(r'#(?:[A-Z][a-z]+)+', text)
    return hashtags


def fix_contractions(text, debug=False):
    text = re.sub(r"(it|what|that|there)'s", lambda m: '%s is' %
                  m.group(1), text)
    text = re.sub(r"([a-zA-Z])n't", lambda m: '%s not' % m.group(1), text)
    text = re.sub(r"([a-zA-Z])'ve", lambda m: '%s have' % m.group(1), text)
    text = re.sub(r"([a-zA-Z])'ll", lambda m: '%s will' % m.group(1), text)


def synonyms(word):
    syns = set([word])
    try:
        synsets = wordnet.synsets(word)
    except NameError:
        from nltk.corpus import wordnet
        synsets = wordnet.synsets(word)

    for sn in synsets:
        syns.update(set(sn.lemma_names))

    return syns


def wordlist():
    # if not hasattr(wordlist, "words"):
    try:
        import nltk
        words = set([w.lower().decode('utf8') for w in nltk.corpus.words.words()])
        filepath = os.path.join(MODULE_PATH, 'words.txt')
        with open(filepath) as f:
            more_words = [l.decode('utf8') for l in f.read().splitlines()]
            words.update(set(more_words))
    except ImportError as err:
        words = list()

    return words


# STEMMER = Stemmer.Stemmer('english')

# So this is kind of messy, and doesn't work very well right now.
# Basically: I want to do 'realness checking' to figure out
# whether a word is a real word or not. This doesn't work using just a look-up,
# because gerunds and plurals etcetera frequently aren't on wordlists.
# I was trying to use a stemmer, but then the *stems* are often
# not real words, either. 

# possible solutions: 
#     - some sort of custom stemmer?
#     - some sort of thing that converts stems back into words
#     - using some sort of spell-checking API
#     - getting a better wordlist?
#     - etcetera.

#     I'm not sure where to go with this, right now.


def is_real_word(word, debug=False):
    assert isinstance(word, unicode), 'word "%s" not unicode' % word
    if not hasattr(is_real_word, "words"):
        is_real_word.words = wordlist()
        print('loaded %d words' % len(is_real_word.words))

    if word in is_real_word.words:
        return True

  # now this is a bunch of stemming handlers for plurals and tenses etc.
   
   # ------option 1 ------- #

    # if word[-1] == 's':
    #     # cheap handling of plurals not in our dict
    #     return is_real_word(word[:-1])
    # elif word[-1] in {'g', 'd', 's', 'r', 't'}:
    #     # cheap handling of gerunds not in our dict.
    #     # this won't do great for nouns ending in e
    #     if debug:
    #         print('degerunding: %s' % word)
    #     if re.search(r'ing$', word):
    #         word = word[:-3]
    #         if debug:
    #             print('trying %s' % word)
    #         if is_real_word(word):
    #             if debug:
    #                 print('success')
    #             return True
    #         else:
    #             word = word + 'e'
    #             if debug:
    #                 print('trying %s' % word)
    #             if is_real_word(word):
    #                 if debug:
    #                     print('success')
    #                 return True

    # ------option 2 ------- #

        # stem = STEMMER.stemWord(word)
        # if stem != word:
        #     result = is_real_word(stem)
        #     if result:
        #         return True

        #     if stem[-1] == 'i':
        #         # sacrificing 'skiing' for the common good
        #         stem = stem[:-1] + 'y'
        #         return is_real_word(stem)

        #     stem += 'e'
        #     result = is_real_word(stem)
        #     if result:
        #         return True
        #     if debug:
        #         print('trying stem %s for word %s' % (stem, word))


    # don't comment me
    return False


def lines_from_file(filepath):
    lines = None
    with open(filepath) as f:
        lines = f.read().splitlines()
        lines = [unicode(l.decode('utf8')) for l in lines]
    return lines


def debug_lines():
    filepath = os.path.join(MODULE_PATH, os.path.pardir, 'tests/100k.tst')
    return lines_from_file(filepath)

# these, at some point, might want to be in another file:


def line_iter(source, filters, key=None, delay=0):
    """
    takes a source iterator and a list of filters
    yields items from source that pass filters.

    if items in source are not strings, they must be dict-like
    (they must implement __get__)
    in this case, a key should be provided to relevant line property, i.e.:

    for tweets where we want to preserve metadata,
    we would pass key='text', e.g.
    """

    for item in source:
        if isinstance(item, basestring):
            line = unicodify(item)
        else:
            assert key != None, 'non-string sources require a key'
            line = unicodify(item[key])

        if filter_line(line, filters):
            yield item
            if delay:
                time.sleep(delay)


def unicodify(item):
    assert isinstance(item, basestring), "unicodify expects a string type"
    if isinstance(item, str):
        return item.decode('utf-8')
    if isinstance(item, unicode):
        return item


def lines(source, filters, key=None):
    return [l for l in line_iter(source, filters, key)]

def filter_line(line, filters):
    for f in filters:
        if f(line):
            return False

    return True
    

def main():
    pass


if __name__ == "__main__":
    main()
