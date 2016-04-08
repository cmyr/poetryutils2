# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from poetryutils2 import filters


def test_low_letter_ratio():
    assert filters.low_letter_filter('hi!', cutoff=0.5)
    assert not filters.low_letter_filter('hi!', cutoff=0.7)
    assert filters.low_letter_filter('francais', cutoff=1.0)
    assert filters.low_letter_filter('français', cutoff=1.0)
