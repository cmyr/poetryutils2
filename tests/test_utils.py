# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from poetryutils2 import utils


def test_contractions():
    assert utils.fix_contractions("don't") == "do not"
    assert utils.fix_contractions('you\'ve') == "you have"
    assert utils.fix_contractions("we'll") == "we will"


def test_real_words():
    assert not utils.is_real_word('somedumbfakeworda;dslfjk', 'en')
    assert not utils.is_real_word('somedumbfakeworda;dslfjk', 'fr')
    assert utils.is_real_word('cow', 'en')
    assert not utils.is_real_word('vacance', 'en')
    assert not utils.is_real_word('cow', 'fr')
    assert utils.is_real_word('vacance', 'fr')
