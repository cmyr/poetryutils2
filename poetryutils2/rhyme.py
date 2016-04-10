# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


import re
import os
import sys
import functools
import multiprocessing
import time

try:
    if (sys.version_info > (3, 0)):
        import dbm.gnu as dbm
        DBM_V = 'dbm.gnu'
    else:
        import gdbm as dbm
        DBM_V = 'gdbm'
    DBM_FLAGS = 'cs'
except ImportError:
    import anydbm as dbm
    DBM_V = 'anydbm'
    DBM_FLAGS = 'c'

from . import utils, espeak_wrapper

print('using %s for dbm' % DBM_V, file=sys.stderr)


double_end_letters = set(['f', 'e', 'l', 'i', 'o', 's'])
ipa_vowels = set("ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː")


PHONEME_DATA_DIR = os.path.join(utils.RESOURCES_DIR, 'phoneme_data')

if not os.path.exists(PHONEME_DATA_DIR):
    os.makedirs(PHONEME_DATA_DIR)

__rhymers = {}


def rhymer_for_language(lang, debug=False):
    if lang in ('en', 'fr'):
        if not __rhymers.get(lang):
            __rhymers[lang] = PhonemeRhymer(PHONEME_DATA_DIR, lang, debug=debug)
        return __rhymers[lang]
    else:
        raise Exception('lang %s is unsupported' % lang)


class PhonemeRhymer(object):
    """docstring for RhymeDB"""

    ESPEAK_LANG_TABLE = {
        'en': 'en-us',
        'fr': 'fr'
        }

    def __init__(self, basepath, lang, dbpath=None, debug=False):
        super(PhonemeRhymer, self).__init__()
        self.basepath = basepath
        self.lang = lang
        self.dbpath = dbpath or os.path.join(self.basepath, 'phonemes_%s.db' % self.lang)
        self.new_words = 0
        self.db = None
        self.debug = debug

    def __len__(self):
        self.open_db()
        dblen = len(self.db)
        self.close_db()
        return dblen

    def open_db(self):
        self.db = dbm.open(self.dbpath, DBM_FLAGS)
        self.new_words = 0

    def close_db(self):
        if self.db is not None:
            self.db.close()
            self.db = None

    def get_phonemes(self, word):
        '''returns the IPA phonemes for word, calculating them if needed'''
        assert utils.isstring(word), 'key must be string'
        word = self._normalize_word(word)
        word = word.encode('utf-8')
        try:
            self.open_db()
            if word not in self.db:
                _, phonemes = espeak_wrapper.extract_phonemes(word, self.lang)
                self.db[word] = self._adjust_phonemes(phonemes).encode('utf-8')
            phonemes = self.db[word].decode('utf-8')
            # we have some bad entries in the database from before we did phoneme adjustment
            if phonemes != self._adjust_phonemes(phonemes):
                self.db[word] = self._adjust_phonemes(phonemes).encode('utf-8')
                print('adjusted phonemes for %s' % phonemes, file=sys.stderr)
                return self.db[word].decode('utf-8')
            return phonemes
        finally:
            self.close_db()

    def is_rhyme(self, text1, text2):
        w1 = self.rhyme_word(text1)
        w2 = self.rhyme_word(text2)

        p1 = self.get_phonemes(w1)
        p2 = self.get_phonemes(w2)

        if len(p1) and len(p2):
            s1 = self._end_sound(p1)
            s2 = self._end_sound(p2)

            if self.debug:
                print(text1, text2, w1, w2, p1, p2, s1, s2)
            if s1.lstrip('ˈˌ') == s2.lstrip('ˈˌ'):
                return not self._are_homophonic(p1, p2)
            elif self.debug:
                print('no rhyme')

        return False

    def sound_for_word(self, word):
        '''this is sort of legacy: it used to presume it might use different
        functions to get different sounds from a word?'''
        p = self.get_phonemes(word)
        return self._end_sound(p)

    def _adjust_phonemes(self, phonemes):
        """
        some adjustments we make to ipa
        """
        
        if not utils.isstring(phonemes):
            print('bad phoneme data:', type(phonemes))
            return
        # phonemes = re.sub(r'[ˈˌ]', '', phonemes, flags=re.UNICODE)
        phonemes = re.sub(r'(oː|ɔː)', 'ö', phonemes, flags=re.UNICODE)
        return phonemes

    def rhyme_word(self, text):
        """returns none if last word isn't a word"""
        words = text.rstrip(' !.,?\"\'').split()
        if len(words):

            last_word = words.pop()
            if last_word[0] == '#':
                last_word = utils.fix_hashtags(text).split().pop()
            if last_word.isalpha():
                return self._normalize_word(last_word)
        return None

    def _normalize_word(self, word):
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
                    if not utils.is_real_word(word, self.lang):
                        if utils.is_real_word(word[:-1], self.lang):
                            return word[:-1]
                else:
                    # matt == mat, hatt == hat, e.g.
                    repl = word[-1]
                    word = re.sub(pattern, repl, word)

        return word

    def _end_sound(self, phonemes):
        if not phonemes or not len(phonemes):
            raise ValueError('phonemes cannot be None')

        p = list(reversed(phonemes))
        if self.debug:
            print('extracting end sound for %s' % phonemes)
        if p[0] in ipa_vowels:
            # handle sounds that end w/ vowels
            for idx, letter in enumerate(p[1:]):
                if self.debug:
                    print(idx, letter)
                # if letter in ipa_vowels and p[idx] not in ipa_vowels:
                if letter not in ipa_vowels:
                    if self.debug:
                        print('breaking on %s' % letter)
                    break
            return ''.join(reversed(p[:idx+1]))
        else:
            for idx, letter in enumerate(p[1:]):
                # stop on first consonant after a vowl
                if letter not in ipa_vowels and p[idx] in ipa_vowels:
                    if self.debug:
                        print('breaking on %s' % letter)
                    break
            return ''.join(reversed(p[:idx+1]))   

    def _are_homophonic(self, phonemes1, phonemes2):
        if phonemes1 == phonemes2:
            return True

        # if the shorter word begins with a consonant we return True
        # if the longer word contains all the shorter's phonemes

        shorter = min([phonemes1, phonemes2], key=lambda x: len(x))
        longer = phonemes1 if shorter == phonemes2 else phonemes2

        if shorter[0] not in ipa_vowels:
            if longer[-len(shorter):] == shorter:
                return True

        return False

    def add_new_words(self, wordlist):
        """
        add new words to our lookup table
        """
        self.open_db()
        try:
            wordlist = [self._normalize_word(w) for w in wordlist
                        if w.encode('utf-8') not in self.db]
            num_words = len(wordlist)
            print('extracting phonemes for %d new words' % num_words)
            start = time.time()
            pool = multiprocessing.Pool(4)
            pool_func = functools.partial(espeak_wrapper.extract_phonemes, lang=self.lang)
            result = pool.map_async(pool_func, wordlist)

            # wait for result
            while True:
                if result.ready():
                    break
                else:
                    print("%d/%d\r" % (num_words, result._number_left), file=sys.stdout)
                    sys.stdout.flush()
                    time.sleep(1)

            for w, p in result.get():
                self.db[w.encode('utf-8')] = self._adjust_phonemes(p).encode('utf-8')
            print('finished in %0.2f' % (time.time() - start))
        finally:
            self.close_db()


# def rhymes_for_lines(lines, textkey=None):
#     """
#     takes an iterable containing lines of text
#     returns them grouped by rhyme
#     returns a list of lists of homophones
#     """

#     open_db()
#     organized_rhyme = defaultdict(list)

#     fails = 0
#     for l in lines:
#         try:
#             w = rhyme_word(l)
#             if w:
#                 p = get_phonemes(w)
#                 e = _end_sound(p)
#                 organized_rhyme[e].append((l, p))
#         except ValueError:
#             fails += 1

#     print('failed to find rhyme words in %d lines' % fails)

#     # now we'd like to sort based on homophones?
#     results = list()

#     for key, value in organized_rhyme.items():
#         if len(value) > 1:
#             results.append(_sort_rhymes(value))

#     close_db()
#     return results


# def _sort_rhymes(rhymes):
#     # for a list of rhymes, sort them by homophones
#     sorted_rhymes = defaultdict(list)
#     for line, phonemes in rhymes:
#         sorted_rhymes[phonemes].append(line)

#     # TODO: now check keys for homophonity

#     return sorted_rhymes.values()


# def UPDATE_PHONEME_LIST(phonemes=wordsets.custom_ipa):
#     """
#     a utility function for manually updating our phoneme list.
#     phonemes should be a list of (word, ipa) tuples.
#     """
#     open_db()
#     for w, p in phonemes:
#         db[w.encode('utf-8')] = p.encode('utf-8')
#     close_db()
