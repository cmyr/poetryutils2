from __future__ import print_function
from __future__ import unicode_literals
import re
import os
import Stemmer


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
    filepath = os.path.dirname(os.path.realpath(__file__))
    print(filepath)
    filepath = os.path.join(filepath, 'words.txt')
    print(filepath)
    with open(filepath) as f:
        words.update(set(f.read().splitlines()))

    return words


STEMMER = Stemmer.Stemmer('english')

def is_real_word(word, debug=False):
    assert isinstance(word, unicode), 'word "%s" not unicode' % word
    if not hasattr(is_real_word, "words"):
        is_real_word.words = wordlist()
        print('loaded %d words' % len(is_real_word.words))

    if word in is_real_word.words:
        return True

  # now this is a bunch of stemming handlers for plurals and tenses etc.
    if word[-1] == 's':
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
            if debug:
                print('trying stem %s for word %s' % (stem, word))

    return False


def lines_from_file(filepath):
    lines = None
    with open(filepath) as f:
        lines = f.read().splitlines()
        lines = [unicode(l.decode('utf8')) for l in lines]
    return lines


def debug_lines():
    return lines_from_file('tests/100k.tst')


def main():
    pass


if __name__ == "__main__":
    main()
