from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import re
import time


MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIR = os.path.join(
    MODULE_PATH,
    os.pardir,
    'resources')

# helpers etc


def isstring(value):
    if (sys.version_info > (3, 0)):
        return isinstance(value, str)
    else:
        return isinstance(value, basestring)


def isunicode(value):
    if (sys.version_info > (3, 0)):
        return isinstance(value, str)
    else:
        return isinstance(value, unicode)


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
    if not isstring(text):
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
    return text


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


def wordlist_en():
    words = set()   
    try:
        import nltk
        words.update(
            w.decode('utf-8').lower().strip() for w in nltk.corpus.words.words())
    except ImportError:
        print('failed to import nltk, using shorter english wordlist', file=sys.stderr)
    filepath = os.path.join(RESOURCES_DIR, 'words.txt')
    with open(filepath) as f:
        words.update(
            l.decode('utf-8').lower().strip() for l in f.read().splitlines())

    print('loaded %d words (en)' % len(words))
    return words


def wordlist_fr():
    words = set()
    filepath = os.path.join(RESOURCES_DIR, 'mots_fr.txt')
    with open(filepath) as f:
        words.update(
            l.decode('utf-8').lower().strip() for l in f.read().splitlines())
    print('loaded %d words (fr)' % len(words))
    return words


def load_words(lang):
    if lang == 'en':
        return wordlist_en()
    elif lang == 'fr':
        return wordlist_fr()


def is_real_word(word, lang='en', debug=False):
    assert isunicode(word), 'word "%s" not unicode' % word
    if not hasattr(is_real_word, lang):
        setattr(is_real_word, lang, load_words(lang))

    wordlist = getattr(is_real_word, lang)
    return word in wordlist


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
            assert key is None, 'non-string sources require a key'
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
