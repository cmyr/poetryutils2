# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from poetryutils2 import rhyme


rhymer_en = rhyme.rhymer_for_language('en')


def test_espeak():
    cmd = rhyme._get_espeak_command()
    assert cmd is not None


def test_get_phonemes():
    assert rhymer_en
    with rhymer_en as r:
        assert r.get_phonemes('hello') == 'həlˈoʊ'


def test_end_words():
    end_tests = """
    matttt mat
    lolllllll loll
    #WhyLiveee live
    meleeee melee"""

    end_tests = [t.split() for t in end_tests.splitlines() if len(t)]

    with rhymer_en as ren:
        for t in end_tests:
            print('t: %s' % t)
            r = ren._rhyme_word(t[0])
            assert r == t[1], print(t, r)

        assert ren._rhyme_word('suxxxx69') is None


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
    with rhymer_en as r:
        for t in sound_tests:
            s = r.sound_for_word(t[0])
            assert s == t[1], '%s %s %s' % (t[0], t[1], s)


def test_rhyme_word():
        pass
