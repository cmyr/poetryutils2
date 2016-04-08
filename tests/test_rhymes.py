# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import os

from poetryutils2 import rhyme, espeak_wrapper


rhymer_en = rhyme.rhymer_for_language('en')
rhymer_fr = rhyme.rhymer_for_language('fr')


def test_espeak():
    cmd = espeak_wrapper._get_espeak_command()
    assert cmd is not None


def test_get_phonemes():
    assert rhymer_en
    assert rhymer_en.get_phonemes('hello') == 'həlˈoʊ'


def test_get_phonemes_fr():
    assert rhymer_fr
    rhymer_fr.get_phonemes('français') == "fʁɑ̃sˈɛ"


def test_end_words():
    end_tests = """
    matttt mat
    lolllllll loll
    #WhyLiveee live
    meleeee melee"""

    end_tests = [t.split() for t in end_tests.splitlines() if len(t)]

    for t in end_tests:
        r = rhymer_en.rhyme_word(t[0])
        assert r == t[1], print(t, r)

    assert rhymer_en.rhyme_word('suxxxx69') is None


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
        s = rhymer_en.sound_for_word(t[0])
        assert s == t[1], '%s %s %s' % (t[0], t[1], s)


def test_rhyme_word():
        pass


def test_add_words():
    try:
        test_db_path = 'test_db.tmp'
        rhymer = rhyme.PhonemeRhymer('.', 'en', test_db_path)
        assert len(rhymer) == 0
        rhymer.add_new_words(['hi', 'bye', 'dumb'])
        assert len(rhymer) == 3
    finally:
        os.remove(test_db_path)
