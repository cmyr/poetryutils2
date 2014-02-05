from __future__ import print_function
from __future__ import unicode_literals

import re

import utils
# extract useful info?
# this will change depending on what 
# sort of sonic likeness we're looking for?
double_end_letters = set(['f','e','l','i','o','s'])

def get_rhyme_word(text):
    #if the last word isn't a word, we could just pass
    words = text.split()
    word = None

    # find the last word, skipping emoji etc
    while len(words):
        word = words.pop()
        if word[0] == "#":
            word = utils.fix_hashtags(text).split().pop()

        word = ''.join(w for w in word if w.isalpha())
        if not len(word):
            return None


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


    pass

def get_end_sound(word):
    pass

# what are our usecases?
# - does x rhyme with z
# - 


def add_new_words(wordlist):
    """
    add new words to our lookup table
    """
    num_words = len(wordlist)
    print('extracting phonemes for %d new words' % num_words)
    start = time.time()
    pool = multiprocessing.Pool(4)
    result = pool.map_async(_get_phonemes, words)
    
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


def _get_phonemes(word):
    espeak_output = os.popen3("speak -v english-us -q --ipa %s"%word, 'r')[1].read()
    phonemes = espeak_output.strip().decode('utf8')
    return word, phonemes

def words_are_homophony(w1, w2):
    pass

def words_rhyme(w1, w2):
    pass






def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('arg1', type=str, help="required argument")
    parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    args = parser.parse_args()


if __name__ == "__main__":
    main()