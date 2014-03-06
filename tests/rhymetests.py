# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import poetryutils2



end_tests = """
matttt mat
lolllllll loll
#WhyLiveee live
meleeee melee
suxxxx69 sux
"""

end_tests = [t.split() for t in end_tests.splitlines() if len(t)]
print(end_tests)
def test_end_words():
    for t in end_tests:
        r = poetryutils2.rhyme.get_rhyme_word(t[0])
        assert r == t[1], print(t, r)

    print('passed end sound test')


sound_tests = """
 həlˈoʊ ˈoʊ 
 wˈaɪ ˈaɪ
 wˈʌt ˈʌt
 ˌɪnɾəfˈɪɹəns əns
 plˈeɪts ˈeɪts
 ɛkspɹˈɛʃən ən
 skˈiːmə ə
 ˈɛldɹɪtʃt ɪtʃt
 hˈuːɾɪnˌæni i
"""

sound_tests = [tuple(x.split()) for x in sound_tests.splitlines() if len(x)]
# print(sound_tests)

def end_sound_tests():
    for t in sound_tests:
        s = poetryutils2.rhyme.get_end_sound(t[0])
        assert s == t[1], print(t, s)

    print('passed end sound test')

def main():
    test_end_words()
    end_sound_tests()
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('arg1', type=str, help="required argument")
    # parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
    # args = parser.parse_args()


if __name__ == "__main__":
    main()