# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


import re
import os
import sys
try: 
    import gdbm as dbm
except ImportError:
    import anydbm as dbm

import cPickle as pickle
import time
import multiprocessing

from collections import defaultdict
from .mpycache import LRUCache

from . import utils
from . import wordsets

# extracting phonemes relies on espeak (http://espeak.sourceforge.net)
# espeak is aliased to 'speak' on some systems
ESPEAK_COMMAND_NAME = ""
if len(os.popen3("espeak -v english-us -q --ipa %s", 'r')[1].read()):
    ESPEAK_COMMAND_NAME = "espeak"
elif len(os.popen3("speak -v english-us -q --ipa %s", 'r')[1].read()):
    ESPEAK_COMMAND_NAME = "speak"
else:
    raise ImportError("rhyme module requires espeak to be installed. http://espeak.sourceforge.net")


RHYME_DEBUG = False

double_end_letters = set(['f', 'e', 'l', 'i', 'o', 's'])
ipa_vowels = set("ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː")



data_dir = os.path.join(utils.MODULE_PATH, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

dbpath = os.path.join(data_dir, 'phonemes.db')


db = None
stats = dict()
phone_cache = LRUCache()


def open_db():
    global db
    if not db:
        db = dbm.open(dbpath, 'c')
        stats['new'] = 0


def close_db():
    global db
    if not db:
        return
        
    if stats['new'] > 0 and RHYME_DEBUG:
        print('added %d new words to phoneme index' % stats['new'])
    db.close()
    db = None


def rhyme_word(text, debug=False):
    # if the last word isn't a word, we could just pass
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

    return _normalize_word(word)


def rhyme_word_if_appropriate(text):
    """returns none if last word isn't a word"""
    words = text.rstrip(' !.,?\"\'').split()
    
    if not len(words):
        return None

    last_word = words.pop()
    if last_word[0] == "#":
        last_word = last_word[1:]
    if last_word.isalpha():
        return last_word

    return None


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


def get_phonemes(word):
    if RHYME_DEBUG:
        assert word == _normalize_word(word), print(
            'passed unnormalized %s to get_phonemes' % word)

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


def _end_sound(phonemes):
    if not phonemes or not len(phonemes):
        raise ValueError('phonemes cannot be None')

    p = list(phonemes)
    sound = p.pop()
    if sound[0] in ipa_vowels:
        brake = False
        while True:
            try:
                l = p.pop()
            except IndexError:
                break
            if l in ipa_vowels and brake == True:
                break
            elif l not in ipa_vowels:
                brake = True
            sound = l + sound

        # handle sounds that end w/ vowels
    else:
        # sounds that end in consonants
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

    # last syllable minus initial consonants.
    # brake = False
    # while True:
    #     try:
    #         l = p.pop()
    #     except IndexError:
    #         break
    #     if l not in ipa_vowels and brake == True:
    #         break
    #     elif l in ipa_vowels:
    #         brake = True
    #     sound = l + sound

    return sound


def sound_for_word(word, func=_end_sound):
    """
    a sort of convenience function for getting a specific
    sound for a word, returning None on any errors
    """
    open_db()
    try:
        w = _normalize_word(word)
        p = get_phonemes(w)
        sound = func(p)
        return sound
    except ValueError as err:
        return None


def _extract_phonemes(word):
    espeak_command = "%s -v english-us -q --ipa %s" % (ESPEAK_COMMAND_NAME, word)
    espeak_output = os.popen3(espeak_command, 'r')[1].read()
    phonemes = espeak_output.strip().decode('utf8')
    stats['new'] += 1
    return word, phonemes


def words_are_homophony(w1, w2):
    phoneme1 = get_phonemes(w1)
    phoneme2 = get_phonemes(w2)

    if RHYME_DEBUG:
        print(type(phoneme1), type(phoneme2))
        print(phoneme1, phoneme2)

    # phoneme1 = re.sub(ur'[ˈˌ]', '', phoneme1, re.UNICODE)
    # phoneme2 = re.sub(ur'[ˈˌ]', '', phoneme2, re.UNICODE)

    if RHYME_DEBUG:
        print(phoneme1, phoneme2)

    if phoneme1 == phoneme2:
        return True

    shorter = phoneme1 if (len(phoneme1) < len(phoneme2)) else phoneme2
    longer = phoneme1 if shorter == phoneme2 else phoneme2

    # if the shorter word begins with a consonant we return True
    # if the longer word contains all the shorter's phonemes
    if shorter[0] not in ipa_vowels:
        if longer[-len(shorter):] == shorter:
            return True

    return False


def words_rhyme(w1, w2):
    open_db()
    w1 = _normalize_word(w1)
    w2 = _normalize_word(w2)

    p1 = get_phonemes(w1)
    p2 = get_phonemes(w2)
    close_db()
    if _end_sound(p1) == _end_sound(p2):
        if not words_are_homophony(w1, w2):
            return True

    return False

def lines_rhyme(l1, l2):
    return words_rhyme(rhyme_word(l1), rhyme_word(l2))

def rhymes_for_word(word, wordlist):
    open_db()
    new_words = set(w for w in wordlist if w.encode('utf8') not in db)
    
    if len(new_words):
        close_db()
        # because add_new opens it itself
        add_new_words(new_words)
        open_db()

    print('looking for rhymes of %s amongst %d words' % (word, len(wordlist)))
    try:
        sound = sound_for_word(word)
        if not sound:
            print('could not extract sound for word: %s' % word)

        rhymes = [w for w in wordlist if sound_for_word(w) == sound]
    finally:
        close_db()
    return rhymes



def rhymes_for_lines(lines, textkey=None):
    """ 
    takes an iterable containing lines of text
    returns them grouped by rhyme
    returns a list of lists of homophones
        """

    open_db()
    organized_rhyme = defaultdict(list)

    fails = 0
    for l in lines:
        try:
            w = rhyme_word(l)
            if w:
                p = get_phonemes(w)
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

    # TODO: now check keys for homophonity
    
    return sorted_rhymes.values()


def add_new_words(wordlist):
    """
    add new words to our lookup table
    """
    open_db()
    num_words = len(wordlist)
    print('extracting phonemes for %d new words' % num_words)
    start = time.time()
    pool = multiprocessing.Pool(4)
    result = pool.map_async(_extract_phonemes, wordlist)

    while True:
        if result.ready():
            break
        status = "%d/%d\r" % (num_words, result._number_left)
        sys.stdout.write(status)
        sys.stdout.flush()
        time.sleep(1)

    result = result.get()
    for w,p in result:
        db[w.encode('utf8')] = p.encode('utf8')
    #     modified_phonemes.add((w, adjust_phonemes(p)))
    print('finished in %0.2f' % (time.time() - start))
    close_db()


def UPDATE_PHONEME_LIST(phonemes=wordsets.custom_ipa):
    """
    a utility function for manually updating our phoneme list.
    phonemes should be a list of (word, ipa) tuples.
    """
    open_db()
    for w, p in phonemes:
        db[w.encode('utf8')] = p.encode('utf8')
    close_db()




def main():
    pass
    import argparse
    parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    parser.add_argument('--update',
                        help='update phoneme list', action="store_true")

    args = parser.parse_args()

    if args.update:
        UPDATE_PHONEME_LIST()

    


if __name__ == "__main__":
    main()
