# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


import re
import os
import anydbm
import cPickle as pickle

from collections import defaultdict
from mpycache import LRUCache

import utils



# PHONEME_INDEX_PICKLE_PATH = os.path.join(utils.MODULE_PATH, "data/phonemes.p")

# phoneme_index = None
# modified_phonemes = None

wordlist =  None
rhyme_table = None

double_end_letters = set(['f','e','l','i','o','s'])
ipa_vowels = set("ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː")


# def load_phoneme_index():
#     global phoneme_index, modified_phonemes, wordlist
#     if not phoneme_index:
#         print('loading phoneme index')
#         try:
#             phoneme_index = pickle.load(open(PHONEME_INDEX_PICKLE_PATH, 'r'))
#             # modified_phonemes = convert_phoneme_index()
#             # wordlist = phoneme_index.keys()
#         except IOError:
#             print('io error in rhymes')
#             phoneme_index = dict()



# def build_rhyme_index():
#     global rhyme_table
#     rhyme_table = defaultdict(set)

#     for w,p in phoneme_index.items():
#         e = end_sound(p)
#         rhyme_table[e].add(w)


# def get_phonemes(word):
    
#     if not phoneme_index:
#         load_phoneme_index()
#     word = normalize_word(word)
#     if word:
#         phonemes = phoneme_index.get(word)
#         if not phonemes:
#             phonemes = _extract_phonemes(word)[1]
#         phoneme_index[word] = phonemes

#     return phonemes
     

dbpath = os.path.join(utils.MODULE_PATH, 'data/phonemes.db')
db = None
phone_cache = LRUCache()

def open_db():
    global db
    db = anydbm.open(dbpath, 'cs')

def close_db():
    db.close() 

def _get_phonemes(word):
    # word = normalize_word(word)
    assert isinstance(word, basestring) 
    phonemes = phone_cache.get(word)

    if not phonemes:
        k = word.encode('utf8')
        try:
            # dbm only takes string keys/values
            phonemes = db[k].decode('utf8')
            phonemes = _adjust_phonemes(phonemes)
            phone_cache.put(word, phonemes)
            return phonemes
        except KeyError:
            phonemes = _extract_phonemes(word)[1]
            db[k] = phonemes.encode('utf8')
            phonemes = _adjust_phonemes(phonemes)
            phone_cache.put(word, phonemes)

    return phonemes

def _adjust_phonemes(phonemes):
    """
    some adjustments we make to ipa 
    """
    
    if not isinstance(phonemes, basestring):
        print('bad phoneme data:', type(phonemes))
        return
    phonemes = re.sub(r'[ˈˌ]', '', phonemes, flags=re.UNICODE)
    phonemes = re.sub(r'(oː|ɔː)', 'ö', phonemes, flags=re.UNICODE)

    return phonemes

def rhyme_word(text, debug=False):
    #if the last word isn't a word, we could just pass
    words = text.split()
    word = None

    # find the last word, skipping emoji etc
    while len(words):
        word = words.pop()

        if word[0] == "#":
            word = utils.fix_hashtags(text).split().pop()

        word = ''.join(w for w in word if w.isalpha())
        if len(word):
            break

    if not word or not len(word):
        return None

    return normalize_word(word)



def _normalize_word(word):
    if not word or not len(word):
        raise ValueError('expected string')

    word = word.lower()
    # handle lolllll and uhhhh and haahhhh
    if len(word) > 2:
        if word[-1] == word[-2]:
            pattern = word[-1] + '+$'
            if word[-1] in double_end_letters:
                # ass != as, e.g.
                repl = word[-1] * 2
                word = re.sub(pattern, repl, word)

                # we want melee not mele, but home not homee:
                if not utils.is_real_word(word):
                    if utils.is_real_word(word[:-1]):
                        return word[:-1]
            else:
                # matt == mat, hatt == hat, e.g.
                repl = word[-1]
                word = re.sub(pattern, repl, word)


    return word

def _end_sound(phonemes):
    if not phonemes:
        raise ValueError('phonemes cannot be None')
    sound = ""
    p = list(phonemes)

    # last syllable minus initial consonants.
    brake = False
    while True:
        try:
            l = p.pop()
        except IndexError:
            break
        if l not in ipa_vowels and brake == True:
            break
        elif l in ipa_vowels:
            brake = True
        sound = l + sound

    return sound


def add_new_words(wordlist):
    """
    add new words to our lookup table
    """
    num_words = len(wordlist)
    print('extracting phonemes for %d new words' % num_words)
    start = time.time()
    pool = multiprocessing.Pool(4)
    result = pool.map_async(_extract_phonemes, words)
    
    while True:
        if result.read():
            break
        status = "%d/%d\r" % (num_words, result._number_left)
        sys.stdout.write(status)
        sys.stdout.flush()
    
    result = result.get()
    # for w,p in result:
    #     phoneme_index[w] = p
    #     modified_phonemes.add((w, adjust_phonemes(p)))
    print('finished in %0.2f' % (time.time() - start))
    print('saving updated phoneme list')
    # pickle.dump(phoneme_index, open(PHONEME_INDEX_PICKLE_PATH, 'w'))


def _extract_phonemes(word):
    espeak_output = os.popen3("speak -v english-us -q --ipa %s"%word, 'r')[1].read()
    phonemes = espeak_output.strip().decode('utf8')
    return word, phonemes

def words_are_homophony(w1, w2):
    return False

def words_rhyme(w1, w2):
    w1 = _normalize_word(w1)
    w2 = _normalize_word(w2)

    p1 = _get_phonemes(w1)
    p2 = _get_phonemes(w2)
    if _end_sound(p1) == _end_sound(p2):
        if not words_are_homophony(w1, w2):
            return True

    return False

def rhymes_for_lines(lines, textkey=None):
    """ 
    takes an iterable containing lines of text
    returns them grouped by rhyme
    """

    open_db()
    organized_rhyme = defaultdict(list)

    fails = 0
    for l in lines:
        try:
            w = rhyme_word(l)
            if w:
                p = _get_phonemes(w)
                e = _end_sound(p)
                organized_rhyme[e].append((l, p))
        except ValueError:
            fails += 1


    print('failed to find rhyme words in %d lines' % fails)

    # now we'd like to sort based on homophones?
    results = list()

    for key, value in organized_rhyme.items():
        if len(value) > 1:
            results.append(_sort_rhymes(value))

    close_db()
    return results


def _sort_rhymes(rhymes):
    # for a list of rhymes, sort them by homophones
    sorted_rhymes = defaultdict(list)
    for line, phonemes in rhymes:
        sorted_rhymes[phonemes].append(line)

    return sorted_rhymes.values()









def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('arg1', type=str, help="required argument")
    parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    args = parser.parse_args()


if __name__ == "__main__":
    main()