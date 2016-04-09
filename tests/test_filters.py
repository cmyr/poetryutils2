# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from poetryutils2 import filters, utils


def test_low_letter_ratio():
    assert filters.low_letter_ratio('hi!', cutoff=0.5)
    assert not filters.low_letter_ratio('hi!', cutoff=0.7)
    assert filters.low_letter_ratio('francais', cutoff=1.0)
    assert filters.low_letter_ratio('français', cutoff=1.0)


def test_hashtag_filter():
    assert filters.hashtag_filter('this is normal')
    assert filters.hashtag_filter('this is just a # sign')
    assert not filters.hashtag_filter('#this has hashtag')


def test_URL_filter():
    assert filters.url_filter('this is normal: /not bad at all')
    assert not filters.url_filter('this is https://inbox.google.com/?pli=1')
    assert not filters.url_filter('#this http://www.slashdot.org')


def screenname_filter():
    assert filters.screenname_filter('this is not a screenname')
    assert filters.screenname_filter('this is just an @ sign')
    assert not filters.screenname_filter('this is @cmyr\'s test case')


def test_ascii_and_emoji():
    assert filters.ascii_and_emoji_filter('just a thing')
    assert not filters.ascii_and_emoji_filter('this is çomplicated')
    assert not filters.ascii_and_emoji_filter('this has an 🤓')
    assert not filters.ascii_and_emoji_filter('this has an 💩')


def test_title_case():
    assert filters.title_case_filter('This is ju\'st Colin capitalizing something normally')
    assert not filters.title_case_filter('This Is Title Case')


def test_multiline_filter():
    assert filters.multi_line_filter('this is jut a nrmoal line with a \t tab')
    assert not filters.multi_line_filter("""this
        has a newline tho""")


def test_blacklist_filter():
    blacklist_filter = filters.blacklist_filter(['bad', 'word'])
    assert blacklist_filter('this doesn\'t have the badd wers')
    assert not blacklist_filter('the word is bond')
    assert not blacklist_filter('what is the WORD')


def test_line_length():
    ll_filter = filters.line_length_filter('4,5, 7-8')
    assert not ll_filter('22')
    assert not ll_filter('333')
    assert ll_filter('4444')
    assert ll_filter('55555')
    assert not ll_filter('666666')
    assert ll_filter('7777777')
    assert ll_filter('88888888')

    assert not ll_filter('some normal string that is pretty long')


def test_emoji_filter():
    assert filters.emoji_filter('this is çoöl')
    assert filters.emoji_filter('these are not emoji either ➳⊂⊙㉿')
    assert not filters.emoji_filter('😀')
    assert not filters.emoji_filter('🤓')
    assert not filters.emoji_filter('👽')
    assert not filters.emoji_filter('✊')
    assert not filters.emoji_filter('💄')
    assert not filters.emoji_filter('⛄️')
    assert not filters.emoji_filter('☃️')
    assert not filters.emoji_filter('🎟')
    assert not filters.emoji_filter('🛳')
    assert not filters.emoji_filter('1️⃣')
    assert not filters.emoji_filter('🇧🇪')
    assert not filters.emoji_filter('🇬🇩')
    assert not filters.emoji_filter('✌️')


def test_regex_filter():
    assert filters.regex_check('this is some text', r'xt.', False)
    assert not filters.regex_check('this is some text', r'xt$', False)
    assert not filters.regex_check('this is some text', r'XT$', True)
    assert filters.regex_check('this is some text', r'XT$', False)


def test_line_iter():
    lines = ['This Is Title Case', 'this has an @name', 'this has a #tag', 'this is just right']
    filts = [filters.title_case_filter, filters.screenname_filter, filters.hashtag_filter]
    passed = list(utils.line_iter(lines, filts))
    assert len(passed) == 1


def test_real_word_ratio():
    words = "hello hi alskdfjsdlkfj"
    words_fr = "quelconque mouvoir sdfkjlsdf"
    assert filters.real_word_ratio_filter(0.5, 'en', True)(words)
    assert not filters.real_word_ratio_filter(0.7, 'en', True)(words)
    assert filters.real_word_ratio_filter(0.5, 'fr', True)(words_fr)
    assert not filters.real_word_ratio_filter(0.7, 'fr', True)(words_fr)
