# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from poetryutils2 import sorting


def test_poet():
    poet = sorting.Poet()
    poem = poet.add_keyed_line('hi')
    assert poem is not None
    poems = [p for p in poet.generate_from_source(['hi', 'bye,', 'three'])]
    assert len(poems) == 3


def test_haiku_en():
    lines = ['my day is coming', 'are you my one true good bud', 'or are you a bro']
    poems = [p for p in sorting.Haikuer().generate_from_source(lines)]
    assert len(poems) == 1
    assert poems[0].lang == 'en'
    lines[2] = 'I have the wrong nubmer of syllables pretty sure'
    assert sum(1 for p in sorting.Haikuer().generate_from_source(lines)) == 0


def test_coupler_arg_parsing():
    assert sorting.Coupler(syllable_counts='1,2').syllable_counts == set([1, 2])
    assert sorting.Coupler(syllable_counts=[1, 2, 3]).syllable_counts == set([1, 2, 3])
    assert sorting.Coupler(syllable_counts=(1, 2, 4)).syllable_counts == set([1, 2, 4])
    assert sorting.Coupler(syllable_counts=7).syllable_counts == set([7])


def test_rhymer_en():
    lines = ['i love you too', 'I know you do']
    assert sum(1 for p in sorting.Rhymer(debug=True).generate_from_source(lines)) == 1
    lines[0] = 'i rhyme with nothing'
    assert sum(1 for p in sorting.Rhymer(debug=True).generate_from_source(lines)) == 0


def test_ignore_language():
    poet_fr = sorting.Poet(lang='fr')
    poet_en = sorting.Poet(lang='en')
    item = {'text': 'a line, for a poem.', 'lang': 'en'}
    assert not poet_fr.add_keyed_line(item, key='text')
    assert poet_en.add_keyed_line(item, key='text')


def test_multi_poet_language_ignore():
    poet_fr = sorting.Poet(lang='fr')
    poet_en = sorting.Poet(lang='en')
    multi = sorting.MultiPoet(poets=[poet_fr, poet_en])
    assert len(multi.add_keyed_line(
        {'text': 'a line, for a poem.', 'lang': 'en'},
        key='text')) == 1
    assert len(multi.add_keyed_line('keyless line')) == 2
