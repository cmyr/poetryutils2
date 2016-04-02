# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import poetryutils2


def test_end_words():
    end_tests = """
    matttt mat
    lolllllll loll
    #WhyLiveee live
    meleeee melee
    suxxxx69 sux"""

    end_tests = [t.split() for t in end_tests.splitlines() if len(t)]

    for t in end_tests:
        print('t: %s' % t)
        r = poetryutils2.rhyme.rhyme_word(t[0])
        assert r == t[1], print(t, r)

    print('passed end sound test')


def end_sound_tests():
    sound_tests = """
     həlˈoʊ ˈoʊ
     wˈaɪ ˈaɪ
     wˈʌt ˈʌt
     ˌɪnɾəfˈɪɹəns əns
     plˈeɪts ˈeɪts
     ɛkspɹˈɛʃən ən
     skˈiːmə ə
     ˈɛldɹɪtʃt ɪtʃt
     hˈuːɾɪnˌæni i"""

    sound_tests = [tuple(x.split()) for x in sound_tests.splitlines() if len(x)]
    for t in sound_tests:
        s = poetryutils2.rhyme._end_sound(t[0])
        assert s == t[1], '%s %s %s' % (t[0], t[1], s)


def test_espeak():
    poetryutils2.rhyme.open_db()
    assert poetryutils2.rhyme._extract_phonemes('hello')[1] == 'həlˈoʊ'
    poetryutils2.rhyme.close_db()
