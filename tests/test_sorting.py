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
    lines[2] = 'I have the wrong nubmer of syllables pretty sure'
    assert sum(1 for p in sorting.Haikuer().generate_from_source(lines)) == 0
