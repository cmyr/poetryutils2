# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


import re
import os
import sys
import subprocess

try:
    if (sys.version_info > (3, 0)):
        import dbm.gnu as dbm
    else:
        import gdbm as dbm
    DBM_FLAGS = 'cs'
except ImportError:
    import anydbm as dbm
    DBM_FLAGS = 'c'


from . import utils


def isstring(value):
    if (sys.version_info > (3, 0)):
        return isinstance(value, str)
    else:
        return isinstance(value, basestring)

double_end_letters = set(['f', 'e', 'l', 'i', 'o', 's'])
ipa_vowels = set("ˈˌaeiouyɑɛɪöɩɔɚɷʊʌœöøəæː")


data_dir = os.path.join(utils.MODULE_PATH, 'data')

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

dbpath = os.path.join(data_dir, 'phonemes.db')

# extracting phonemes relies on espeak (http://espeak.sourceforge.net)
# espeak is aliased to 'speak' on some systems

__rhymers = {}


def rhymer_for_language(language):
    if language == 'en':
        if not __rhymers.get('en'):
            __rhymers['en'] = Rhymer(data_dir, language, dbpath)
        return __rhymers['en']


def _get_espeak_command():
    if not hasattr(_get_espeak_command, 'ESPEAK_COMMAND_NAME'):
        cmd = None
        if subprocess.call("espeak") == 0:
            cmd = 'espeak'
        elif subprocess.call("speak") == 0:
            cmd = "speak"
        else:
            raise ImportError(
                "rhyme module requires espeak to be installed. http://espeak.sourceforge.net")

        setattr(_get_espeak_command, 'ESPEAK_COMMAND_NAME', cmd)
    return getattr(_get_espeak_command, 'ESPEAK_COMMAND_NAME')


class Rhymer(object):
    """docstring for RhymeDB"""

    ESPEAK_LANG_TABLE = {
        'en': 'en-us',
        'fr': 'fr'
        }

    ESPEAK_COMMAND_NAME = _get_espeak_command()

    def __init__(self, basepath, language, dbpath=None):
        super(Rhymer, self).__init__()
        self.basepath = basepath
        self.language = language
        self.dbpath = dbpath or os.path.join(self.basepath, 'phonemes_%s.db' % self.language)
        self.new_words = 0
        self.db = None

    def __enter__(self):
        self.db = dbm.open(self.dbpath, DBM_FLAGS)
        self.new_words = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print('added %d new words to %s' % (self.new_words, self.dbpath), file=sys.stderr)
        self.db.close()
        self.db = None

    def __getitem__(self, key):
        assert self.db is not None, 'db should only be access in "with" statement'
        assert isstring(key), 'key must be string'
        key = key.encode('utf-8')
        try:
            return self.db[key].decode('utf-8')
        except KeyError:
            return None

    def __setitem__(self, key, value):
        assert self.db is not None, 'db should only be accessed in "with" statement'
        assert isstring(key), 'key must be string'
        assert isstring(value), 'value must be string not %s' % type(value)
        key = key.encode('utf-8')
        self.db[key] = value.encode('utf-8')

    def is_rhyme(self, text1, text2):
        text1 = self._rhyme_word(text1)
        text2 = self._rhyme_word(text2)

        p1 = self.get_phonemes(text1)
        p2 = self.get_phonemes(text2)

        if len(p1) and len(p2):
            if self._end_sound(p1) == self._end_sound(p2):
                return not self._are_homophonic(p1, p2)

        return False

    def sound_for_word(self, word):
        '''this is sort of legacy: it used to presume it might use different
        functions to get different sounds from a wordd?'''
        p = self.get_phonemes(word)
        return self._end_sound(p)

    def get_phonemes(self, word):
        word = self._normalize_word(word)
        p = self[word]
        if not p:
            p = self.extract_phonemes(word)
            self[word] = p
        return p

    def extract_phonemes(self, word):
        cmd = [
            self.ESPEAK_COMMAND_NAME, '-v',
            self.ESPEAK_LANG_TABLE[self.language],
            '-q', '--ipa', word]
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        phonemes = output.stdout.read().decode('utf-8').strip()
        return self._adjust_phonemes(phonemes)

    def _adjust_phonemes(self, phonemes):
        """
        some adjustments we make to ipa
        """

        if not isstring(phonemes):
            print('bad phoneme data:', type(phonemes))
            return
        phonemes = re.sub(r'[ˈˌ]', '', phonemes, flags=re.UNICODE)
        phonemes = re.sub(r'(oː|ɔː)', 'ö', phonemes, flags=re.UNICODE)

        return phonemes

    def _rhyme_word(self, text):
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
                    if not utils.is_real_word(word):
                        if utils.is_real_word(word[:-1]):
                            return word[:-1]
                else:
                    # matt == mat, hatt == hat, e.g.
                    repl = word[-1]
                    word = re.sub(pattern, repl, word)

        return word

    def _end_sound(self, phonemes):
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
                if l in ipa_vowels and brake is True:
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
                if l not in ipa_vowels and brake is True:
                    break
                elif l in ipa_vowels:
                    brake = True
                sound = l + sound

        return sound

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
    # def add_new_words(self, wordlist):


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


# def add_new_words(wordlist):
#     """
#     add new words to our lookup table
#     """
#     open_db()
#     num_words = len(wordlist)
#     print('extracting phonemes for %d new words' % num_words)
#     start = time.time()
#     pool = multiprocessing.Pool(4)
#     result = pool.map_async(_extract_phonemes, wordlist)

#     while True:
#         if result.ready():
#             break
#         status = "%d/%d\r" % (num_words, result._number_left)
#         sys.stdout.write(status)
#         sys.stdout.flush()
#         time.sleep(1)

#     result = result.get()
#     for w, p in result:
#         db[w.encode('utf8')] = p.encode('utf8')
#     #     modified_phonemes.add((w, adjust_phonemes(p)))
#     print('finished in %0.2f' % (time.time() - start))
#     close_db()


# def UPDATE_PHONEME_LIST(phonemes=wordsets.custom_ipa):
#     """
#     a utility function for manually updating our phoneme list.
#     phonemes should be a list of (word, ipa) tuples.
#     """
#     open_db()
#     for w, p in phonemes:
#         db[w.encode('utf-8')] = p.encode('utf-8')
#     close_db()
