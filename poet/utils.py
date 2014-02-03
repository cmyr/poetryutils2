from __future__ import print_function
from __future__ import unicode_literals
import re


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
    import nltk
    words = set([w.lower() for w in nltk.corpus.words.words()])
    with open('words.txt') as f:
        words.update(set(f.read().splitlines()))

    return words


def lines_from_file(filepath):
    lines = None
    with open(filepath) as f:
        lines = f.read().splitlines()

    return lines


def debug_lines():
    return lines_from_file('tests/100k.txt')


def main():
    pass


if __name__ == "__main__":
    main()
