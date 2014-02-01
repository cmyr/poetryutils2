from __future__ import print_function

import re


# helpers etc

def _strip_string(text):
    """
    for removing punctuation for certain tests
    """

    return re.sub(r'[^a-zA-Z]', '',  text).lower()

def _de_camel(word):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', word)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()

def fix_contractions(text, debug=False):
    text = re.sub(r"(it|what|that|there)'s", lambda m: '%s is' % m.group(1), text)
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

def main():
    pass


if __name__ == "__main__":
    main()