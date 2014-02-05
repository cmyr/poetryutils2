# coding=utf-8

from __future__ import print_function
from __future__ import unicode_literals
import cPickle as pickle
import sys
import os
import re
import requests
import string
import multiprocessing
import time

import poetryutils
import syllables

# RHYME_DB_PATH = 'rhymes.db'
file_dir = os.path.dirname(os.path.realpath(__file__))
PHONEME_INDEX_PICKLE_PATH = os.path.join(file_dir, "data/phonemes.p")
phoneme_index = None
modified_phonemes = None
wordlist = None


def load_phoneme_index():
    """
    loads our phoneme index from disk
    """
    global phoneme_index, modified_phonemes, wordlist
    if not phoneme_index:
        print('loading phoneme index')
        try:
            phoneme_index = pickle.load(open(PHONEME_INDEX_PICKLE_PATH, 'r'))
            modified_phonemes = convert_phoneme_index()
            wordlist = phoneme_index.keys()
        except IOError:
            print('io error in rhymes')
            phoneme_index = dict()


# rhyme_index = {}
# wordlist = set(phoneme_index.keys())


def rhyme_word(line):
    """finds the last word of a sentance,
     but in special cases will modify
    it to help our pronounciation engine. """
    word = _get_last_word(line)
    if not word:
        return None

    word = re.sub(r'^thx$', 'thanks', word)
    word = re.sub(r'uhh+$', 'uh', word)
    word = re.sub(r'(n|s|y|h)oo+$', lambda m: '%so' % m.group(1), word)

    return word


def _get_last_word(sentance):
    
    sentance = sentance.split()
    while len(sentance):
        word = sentance.pop()
        word = ''.join([w for w in word if w.isalpha()])
        if word:
            # if is_camel(word):
            #     return de_camel(word).split().pop()
            return word.lower()


ipa_vowels = ['a','e','i','o','u','y','ɑ','ɛ','ɪ','ɩ','ɔ','ɚ','ɷ','ʊ','ʌ','œ','ø','ə','æ','ö']

def get_phonemes(word):
    if not phoneme_index:
        load_phoneme_index()
    global modified_phonemes
    phonemes = phoneme_index.get(word)
    if not phonemes:
        word = word.lower().strip()
        if not word or any(ch in string.punctuation for ch in word):
            return ""
        espeak_output = os.popen3("speak -v english-us -q --ipa %s"%word, 'r')[1].read()
        phonemes = espeak_output.strip().decode('utf8')
    
        # we don't want to add words to our index when bulk-adding
        # because we're using multiprocessing
        phoneme_index[word] = phonemes
        phonemes = adjust_phonemes(phoneme_index[word])
        modified_phonemes.add((word, phonemes))
        return phonemes

    return adjust_phonemes(phonemes)

def _mp_get_phonemes(word):
    espeak_output = os.popen3("speak -v english-us -q --ipa %s"%word, 'r')[1].read()
    phonemes = espeak_output.strip().decode('utf8')
    return word, phonemes

def convert_phoneme_index():
    """some changes to IPA for our own purposes"""
    modp = set()
    for w,p in phoneme_index.items():
        # modp[adjust_phonemes(p)] = w
        modp.add((w, adjust_phonemes(p)))

    return modp


def adjust_phonemes(phonemes):
    
    if not isinstance(phonemes, basestring):
        print('bad phoneme data:', type(phonemes))
        return
    phonemes = re.sub(r'[ˈˌ]', '', phonemes, flags=re.UNICODE)
    phonemes = re.sub(r'(oː|ɔː)', 'ö', phonemes, flags=re.UNICODE)

    return phonemes


def get_rhyme_words(word):
    word = word.lower().strip()
    
    phonemes = get_phonemes(word)
    ending = end_sound(phonemes)

    source_words = [(x,y) for x,y in modified_phonemes if x in wordlist]
    rhymes = [x for x,y in source_words if end_sound(y) == ending]
    rhymes = [x for x in rhymes if not words_are_homonymy(x, word)]
    return rhymes


def end_sound(phonemes):
    if not phonemes or not len(phonemes):
        print('no phonemes submitted to end_sound')
        sys.exit(1)
        return
    # end sound is the last syllable - initial consonants, if any
    pattern = ur'[ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː]+[^ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː]*$'
    endsound = re.findall(pattern, phonemes, re.UNICODE)
    
    if len(endsound) == 0:
        # print("NO END SOUND?", phonemes)
        return
    try:
        return endsound[0]
    except IndexError:
        # print("INDEX ERROR?", phonemes, endsound)
        raise



def words_are_homonymy(word1, word2, debug=False):

    phoneme1 = get_phonemes(word1)
    phoneme2 = get_phonemes(word2)

    if debug:
        print(type(phoneme1), type(phoneme2))
        print(phoneme1, phoneme2)

    phoneme1 = re.sub(ur'[ˈˌ]', '', phoneme1, re.UNICODE)
    phoneme2 = re.sub(ur'[ˈˌ]', '', phoneme2, re.UNICODE)

    if debug:
        print(phoneme1, phoneme2)

    if phoneme1 == phoneme2:
        return True

    shorter = phoneme1 if (len(phoneme1) < len(phoneme2)) else phoneme2
    longer = phoneme1 if shorter == phoneme2 else phoneme2

    # if the shorter word begins with a consonant we return True
    # if the longer word contains all the shorter's phonemes
    if re.search(ur'^[^ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː]', shorter):
        if longer[-len(shorter):] == shorter:
            return True

    return False


def set_word_list(words):
    load_phoneme_index()
    global wordlist
    wordlist = set(words)
    new_words = set()
    for word in wordlist:
        if word not in phoneme_index:
            new_words.add(word)

    print('set wordlist with %d words, %d new' % (len(wordlist), len(new_words)))
    if not len(new_words):
        # build_rhyme_index()
        return

    add_new_words(new_words)


def add_new_words(words):
    print('extracting phonemes for %d new words' % len(words))
    print('this might take a while.')
    start = time.time()
    pool = multiprocessing.Pool(4)
    result = pool.map(_mp_get_phonemes, words)
    for w,p in result:
        phoneme_index[w] = p
        modified_phonemes.add((w, adjust_phonemes(p)))
    print('finished in %0.2f' % (time.time() - start))
    print('saving updated phoneme list')
    pickle.dump(phoneme_index, open(PHONEME_INDEX_PICKLE_PATH, 'w'))

    

def rhyme_check(word1, word2, debug=False):
    if not hasattr(rhyme_check, 'cache'):
        rhyme_check.cache = dict()


    e1 = rhyme_check.cache.get(word1) or end_sound(get_phonemes(word1))
    e2 = rhyme_check.cache.get(word2) or end_sound(get_phonemes(word2))

    if (e1 == e2
        and not words_are_homonymy(word1, word2)):
        return True

    return False

# playing around with slant rhymes / other phonetic likenesses
def center_sound(word):
    """
    isolating the l'an sound shared by plan and lands, for instance
    """
    # this currently only is relevant for single syllables
    if not word or not len(word):
        print('bad input in center_sound')
        return 0

    # if syllables.syllables_in_word(word) != 1:
    #     return 0

    phonemes = get_phonemes(word)
    # basically we want: (c,v+c)
    # or maybe (c?v+c?) it's sort of questionable at this point

    pattern = ur'^.+?([^ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː]?[ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː]+[^ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː]?)[^ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː]*$'
    endsound = re.findall(pattern, phonemes, re.UNICODE)

    try:
        return endsound[0]
    except IndexError:
        print('failed to find center sound for %s' % word)
        return 0


def center_rhymes(word):
    print(word)
    word = word.lower().strip()
    sound = center_sound(word)
    if not sound:
        return
    print('center rhymes for sound %s from word %s' % (sound, word))

    source_words = [x for x,y in modified_phonemes if x in wordlist]
    results = [x for x in source_words if center_sound(x) == sound]
    results = [x for x in results if not words_are_homonymy(x, word)]
    return results

# testing and debug stuff:

def debug_end_sounds(word, modified=False):
    phonemes = get_phonemes(word)
    # if modified:
    #     phonemes = adjust_phonemes(phonemes)
    print("%s/%s"% (word, phonemes))
    print(end_sound(phonemes))


def fetch_rhyme_words(word):
    url = 'http://rhymebrain.com/talk?function=getRhymes&word=%s' % word
    words = requests.get(url).json()
    return [w['word'] for w in words]

# def 

def main():
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()
    setup_tests()
    # test_simple_rhymes()
    # interactive_debug()
    # test_homonymity()
    # test_rhymes()
    test_import_spead()



# okay, so: we have some sort of basic rhyming thing working.
# but we want our rhymer to find the *good* rhymes, not just *any* rhymes.
# what makes a rhyme good?

# syllable count: the closer they are, the better
# the closeness of the sound, generally;
# not actually just containing the entire sound, or being homonyms

if __name__ == "__main__":
    main()


