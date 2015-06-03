from __future__ import print_function
from __future__ import unicode_literals

import re
import functools
import random

from . import utils
from . import syllables
from . import rhyme
from . import wordsets


"""
various filters for operating on a list of strings (tweets, mainly)
a philosophical question: should a filter return True when an item
passes, or when it fails?
"""

# simple filters:


def url_filter(text):
    """filters out urls"""
    if re.search(r'http://[a-zA-Z0-9\./]*\w', text):
        return True
    else:
        return False


def screenname_filter(text):
    """filters out @names"""
    if re.search(r'@[a-zA-Z0-9]+', text):
        return True
    else:
        return False


def hashtag_filter(text):
    """filters out hashtags"""
    if re.search(r'#[a-zA-Z0-9]+', text):
        return True
    else:
        return False


def numeral_filter(text):
    """filters text containing numerals"""
    if re.search(r'[0-9]', text):
        return True

    return False


def title_case_filter(text):
    if not text.istitle():
        return True

    return False


def multi_line_filter(text):
    """filters out text that contains non-trailing newlines"""
    if len(text.splitlines()) > 1:
        return True

    return False

# def tricky_characters(text, debug=False):
#     """
#     treat as a bool, need to look up counting unicode chars
#     """

#     count = len(re.findall(ur'[\u0080-\u024F]', text))

#     if count and debug:
#         print(re.findall(ur'[\u0080-\u024F]', text))
#     return count


# def tricky_char_filter(text):
#     if tricky_characters(text):
#         return True
#     return False

def ascii_filter(text):
    """filters out non-ascii text"""
    try:
        text.decode('ascii')
    except UnicodeEncodeError:
        return True
    return False

# variable filters:


def whitelist_check(text, whitelist, debug=False):
    """filter text that contains a word on the whitelist"""
    hits = 0
    for word in (utils._strip_string(w) for w in text.split()):
        if word in whitelist:
            if debug:
                print(word)
            hits += 1
            if hits == 1:
                continue
            # number of matches increases chances we'll approve
            # basically 1 hit has a 1/3 chance, 3 hits is a sure thing
            chance = random.randrange(0, 100)
            if chance > (33 * hits):
                return False

    return True


def whitelist_filter(whitelist):
    f = functools.partial(whitelist_check, **{'whitelist': whitelist})
    f.__doc__ = 'whitelist words: %s' % repr(whitelist)
    return f


def topic_syria_filter():
    return whitelist_filter(wordsets.syria)


def topic_ukraine_filter():
    return whitelist_filter(wordsets.ukraine)


def blacklist_check(text, blacklist, leakage=0):
    """filter words from a blacklist"""
    assert 0.0 <= leakage < 1.0, 'illegal value in blacklist check'

    for word in (utils._strip_string(w) for w in text.split()):
        if word in blacklist:
            if leakage:
                leak_chance = leakage * 100  # %
                leak = random.randrange(0, 100)
                if leak > leak_chance:
                    return False
            return True
    return False


def blacklist_filter(blacklist):
    assert(len(blacklist))
    assert isinstance(blacklist, set) or isinstance(blacklist, list)

    f = functools.partial(blacklist_check, **{'blacklist': blacklist})
    f.__doc__ = "filtering words: %s" % repr(blacklist)
    return f


def swears_filter(leakage=0):
    kwargs = {'blacklist': wordsets.swears, 'leakage': leakage}
    return functools.partial(blacklist_check, **kwargs)


def bad_swears_filter():
    return blacklist_filter(wordsets.bad_swears)


def low_letter_ratio(text, cutoff=0.8):
    t = re.sub(r'[^a-zA-Z ]', '', text)
    try:
        if (float(len(t)) / len(text)) < cutoff:
            return True
    except ZeroDivisionError:
        pass
    return False


def low_letter_filter(cutoff):
    assert(0.0 < cutoff < 1.0)
    f = functools.partial(low_letter_ratio, **{'cutoff': cutoff})
    f.__doc__ = "filtering tweets with letter ratio below %0.2f" % cutoff
    return f


def line_length_check(text, line_lengths):
    if len(text) in line_lengths:
        return False
    return True


def line_length_filter(line_lengths):
    """
    line_lengths should be a string of format 0,1,5-8.
    this would represent lengths 0,1,5,6,7,8.
    line lengths can also be a tuple of ints.
    """
    lengths = _parse_range_string(line_lengths)
    if not len(lengths):
        raise ValueError("no line lengths received")

    f = functools.partial(line_length_check, **{'line_lengths': lengths})
    f.__doc__ = "filtering line lengths to %s" % repr(lengths)
    return f


def syllable_count_check(text, syllable_counts, max_syllables):
    count = syllables.count_syllables(text, cutoff=max_syllables)
    if count in syllable_counts:
        return False

    return True


def syllable_count_filter(syllable_counts):
    counts = _parse_range_string(syllable_counts)
    if not len(counts):
        raise ValueError("please specify a range of syllable counts")

    kwargs = {'syllable_counts': counts, 'max_syllables': max(counts)}
    f = functools.partial(syllable_count_check, **kwargs)
    f.__doc__ = "filtering syllable counts to %s" % repr(counts)
    return f


def _parse_range_string(range_string):
    """
    parses strings that represent a range of ints.
    """

    if re.search(r'[^,0-9\-]', range_string):
        raise ValueError("invalid characters in range")

    result = set(int(x) for x in re.findall(r'[0-9]+', range_string))
    ranges = re.findall(r'([0-9]+)\-([0-9]+)', range_string)
    if len(ranges):
        for r in ranges:
            result.update([x for x in range(int(r[0]), int(r[1]) + 1)])

    return tuple(result)


def regex_check(text, pattern, ignore_case):
    if ignore_case and re.search(pattern, text, flags=re.I):
        return False
    elif not ignore_case and re.search(pattern, text):
        return False
    return True


def regex_filter(pattern, ignore_case):
    pattern = _convert_custom_regex(pattern)
    kwargs = {'pattern': pattern, 'ignore_case': ignore_case}
    f = functools.partial(regex_check, **kwargs)
    f.__doc__ = "regex pattern: %s" % pattern
    if ignore_case:
        f.__doc__ += " (case-insensitive)"

    return f

emoji_single = re.compile(
    u'[\u3297\U0001f196\U0001f197\U0001f194\U0001f195\U0001f192\U0001f193\U0001f191\U0001f19a\U0001f198\U0001f199\U0001f18e\U0001f1f7\U0001f1f5\U0001f1f3\U0001f1f0\U0001f1fa\U0001f1f8\U0001f1f9\U0001f1e7\U0001f1ee\U0001f1ef\U0001f1ec\U0001f1ea\U0001f1eb\U0001f1e8\U0001f1e9\U0001f461\U0001f460\u2705\u2196\u26c4\U0001f170\U0001f171\U0001f17e\U0001f17f\u264f\U0001f6a7\u2b1c\U0001f444\u263a\u26c5\u2744\u2663\u2764\U0001f0cf\u2b07\u270f\U0001f004\u2665\u23ec\u26fa\U0001f3b6\U0001f3b7\U0001f3b4\U0001f3b5\U0001f3b2\U0001f3b3\U0001f3b0\U0001f3b1\U0001f3be\U0001f3bf\U0001f3bc\U0001f3bd\U0001f3ba\U0001f3bb\U0001f3b8\U0001f3b9\U0001f3a6\U0001f3a7\U0001f3a4\U0001f3a5\U0001f3a2\U0001f3a3\U0001f3a0\U0001f3a1\U0001f3ae\U0001f3af\U0001f3ac\U0001f3ad\U0001f3aa\U0001f3ab\U0001f3a8\U0001f3a9\u2122\U0001f392\U0001f393\U0001f390\U0001f391\U0001f386\U0001f387\U0001f384\U0001f385\U0001f382\U0001f383\U0001f380\U0001f381\U0001f38e\U0001f38f\U0001f38c\U0001f38d\U0001f38a\U0001f38b\U0001f388\U0001f389\U0001f3f0\u274e\U0001f3e6\U0001f3e7\U0001f3e4\U0001f3e5\U0001f3e2\U0001f3e3\U0001f3e0\U0001f3e1\U0001f3ee\U0001f3ef\U0001f3ec\U0001f3ed\U0001f3ea\U0001f3eb\U0001f3e8\U0001f3e9\U0001f3c6\U0001f3c7\U0001f3c4\U0001f3c2\U0001f3c3\U0001f3c0\U0001f3c1\U0001f3ca\U0001f3c8\U0001f3c9\U0001f337\U0001f334\U0001f335\U0001f332\U0001f333\U0001f330\U0001f331\U0001f33e\U0001f33f\U0001f33c\U0001f33d\U0001f33a\U0001f33b\U0001f338\U0001f339\U0001f320\U0001f316\U0001f317\U0001f314\U0001f315\U0001f312\U0001f313\U0001f310\U0001f311\U0001f31e\U0001f31f\U0001f31c\U0001f31d\U0001f31a\U0001f31b\U0001f318\U0001f319\U0001f306\U0001f307\U0001f304\U0001f305\U0001f302\U0001f303\U0001f300\U0001f301\U0001f30e\U0001f30f\U0001f30c\U0001f30d\U0001f30a\U0001f30b\U0001f308\U0001f309\U0001f376\U0001f377\U0001f374\U0001f375\U0001f372\U0001f373\U0001f370\U0001f371\U0001f37c\U0001f37a\U0001f37b\U0001f378\U0001f379\U0001f366\U0001f367\U0001f364\U0001f365\U0001f362\U0001f363\U0001f360\U0001f361\U0001f36e\U0001f36f\U0001f36c\U0001f36d\U0001f36a\U0001f36b\U0001f368\U0001f369\U0001f356\U0001f357\U0001f354\U0001f355\U0001f352\U0001f353\U0001f350\U0001f351\U0001f35e\U0001f35f\U0001f35c\U0001f35d\U0001f35a\U0001f35b\U0001f358\U0001f359\U0001f346\U0001f347\U0001f344\U0001f345\U0001f342\U0001f343\U0001f340\U0001f341\U0001f34e\U0001f34f\U0001f34c\U0001f34d\U0001f34a\U0001f34b\U0001f348\U0001f349\u260e\u2197\u264e\u2b50\U0001f4fb\u23eb\U0001f236\U0001f237\U0001f234\U0001f235\U0001f232\U0001f233\U0001f23a\U0001f238\U0001f239\U0001f22f\u2b1b\U0001f21a\U0001f202\U0001f201\u26ce\U0001f250\U0001f251\u2702\u2199\u231a\u264c\u25b6\u2139\u2b55\U0001f4a1\U0001f4a0\u270c\u2797\u25ab\u274c\u2198\u25c0\u264d\u2757\U0001f48b\U0001f48a\u2600\u2716\u27a1\u26ab\u2660\U0001f560\u2796\u26a0\u2935\u264b\u3299\u26a1\u2934\u2601\u270b\u24c2\U0001f520\U0001f475\U0001f474\U0001f477\U0001f476\U0001f471\U0001f470\U0001f473\U0001f472\U0001f47d\U0001f47c\U0001f47f\u270a\U0001f479\U0001f478\U0001f47b\U0001f47a\U0001f465\U0001f464\U0001f467\U0001f466\u2795\u2614\U0001f463\U0001f462\U0001f46d\U0001f46c\U0001f46f\U0001f46e\U0001f469\U0001f468\U0001f46b\U0001f46a\U0001f455\U0001f454\U0001f457\U0001f456\U0001f451\U0001f450\U0001f453\U0001f452\U0001f45d\U0001f45c\U0001f45f\U0001f45e\U0001f459\U0001f458\U0001f45b\U0001f45a\U0001f445\u3030\U0001f447\U0001f446\U0001f440\U0001f443\U0001f442\U0001f44d\U0001f44c\U0001f44f\U0001f44e\U0001f449\U0001f448\U0001f44b\U0001f44a\U0001f435\U0001f434\U0001f437\U0001f436\U0001f431\U0001f430\U0001f433\U0001f432\U0001f43d\U0001f43c\U0001f43e\U0001f439\U0001f438\U0001f43b\U0001f43a\U0001f425\U0001f424\U0001f427\U0001f426\U0001f421\U0001f420\U0001f423\U0001f422\U0001f42d\U0001f42c\U0001f42f\U0001f42e\U0001f429\U0001f428\U0001f42b\U0001f42a\U0001f415\U0001f414\U0001f417\U0001f416\U0001f411\U0001f410\U0001f413\U0001f412\U0001f41d\U0001f41c\U0001f41f\U0001f41e\U0001f419\U0001f418\U0001f41b\U0001f41a\U0001f405\U0001f404\U0001f407\U0001f406\U0001f401\U0001f400\U0001f403\U0001f402\U0001f40d\U0001f40c\U0001f40f\U0001f40e\U0001f409\U0001f408\U0001f40b\U0001f40a\U0001f4f5\U0001f4f4\U0001f4f7\U0001f4f6\U0001f4f1\U0001f4f0\U0001f4f3\U0001f4f2\U0001f4fc\U0001f4f9\ufe0f\U0001f4fa\U0001f4e5\U0001f4e4\U0001f4e7\U0001f4e6\U0001f4e1\U0001f4e0\U0001f4e3\U0001f4e2\U0001f4ed\U0001f4ec\U0001f4ef\U0001f4ee\U0001f4e9\U0001f4e8\U0001f4eb\U0001f4ea\U0001f4d5\U0001f4d4\U0001f4d7\U0001f4d6\U0001f4d1\U0001f4d0\U0001f4d3\U0001f4d2\U0001f4dd\U0001f4dc\U0001f4df\U0001f4de\U0001f4d9\U0001f4d8\U0001f4db\U0001f4da\U0001f4c5\U0001f4c4\U0001f4c7\U0001f4c6\U0001f4c1\U0001f4c0\U0001f4c3\U0001f4c2\U0001f4cd\U0001f4cc\U0001f4cf\U0001f4ce\U0001f4c9\U0001f4c8\U0001f4cb\U0001f4ca\U0001f4b5\U0001f4b4\U0001f4b7\U0001f4b6\U0001f4b1\U0001f4b0\U0001f4b3\U0001f4b2\U0001f4bd\U0001f4bc\U0001f4bf\U0001f4be\U0001f4b9\U0001f4b8\U0001f4bb\U0001f4ba\U0001f4a5\U0001f4a4\U0001f4a7\U0001f4a6\u2755\u26d4\U0001f4a3\U0001f4a2\U0001f4ad\U0001f4ac\U0001f4af\U0001f4ae\U0001f4a9\U0001f4a8\U0001f4ab\U0001f4aa\U0001f495\U0001f494\U0001f497\U0001f496\U0001f491\U0001f490\U0001f493\U0001f492\U0001f49d\U0001f49c\U0001f49f\U0001f49e\U0001f499\U0001f498\U0001f49b\U0001f49a\U0001f485\U0001f484\U0001f487\U0001f486\U0001f481\U0001f480\U0001f483\U0001f482\U0001f48d\U0001f48c\U0001f48f\U0001f48e\U0001f489\U0001f488\u267f\u25fe\U0001f565\U0001f564\U0001f567\U0001f566\U0001f561\u2714\U0001f563\U0001f562\U0001f555\U0001f554\U0001f557\U0001f556\U0001f551\U0001f550\U0001f553\U0001f552\U0001f55d\U0001f55c\U0001f55f\U0001f55e\U0001f559\U0001f558\U0001f55b\U0001f55a\u2734\u27bf\U0001f535\U0001f534\U0001f537\U0001f536\U0001f531\U0001f530\U0001f533\U0001f532\U0001f53d\U0001f53c\u264a\U0001f539\U0001f538\U0001f53b\U0001f53a\U0001f525\U0001f524\U0001f527\U0001f526\U0001f521\u2754\U0001f523\U0001f522\U0001f52d\U0001f52c\U0001f52f\U0001f52e\U0001f529\U0001f528\U0001f52b\U0001f52a\U0001f515\U0001f514\U0001f517\U0001f516\U0001f511\U0001f510\U0001f513\U0001f512\U0001f51d\U0001f51c\U0001f51f\U0001f51e\U0001f519\U0001f518\U0001f51b\U0001f51a\U0001f505\U0001f504\U0001f507\U0001f506\u26f5\U0001f500\U0001f503\U0001f502\U0001f50d\U0001f50c\U0001f50f\U0001f50e\U0001f509\U0001f508\U0001f50b\U0001f50a\U0001f5fd\U0001f5fc\U0001f5ff\U0001f5fe\U0001f5fb\u2615\u26aa\U0001f501\u26ea\u2693\U0001f645\U0001f647\U0001f646\U0001f640\U0001f64d\U0001f64c\U0001f64f\U0001f64e\U0001f649\u203c\U0001f64b\U0001f64a\U0001f635\U0001f634\U0001f637\U0001f636\U0001f631\U0001f630\U0001f633\U0001f632\U0001f63d\u2648\U0001f63f\U0001f63e\U0001f639\U0001f638\U0001f63b\U0001f63a\U0001f625\U0001f624\U0001f627\U0001f626\U0001f621\U0001f620\U0001f623\U0001f622\U0001f62d\U0001f62c\U0001f62f\U0001f62e\U0001f629\U0001f628\U0001f62b\U0001f62a\U0001f615\U0001f614\U0001f617\U0001f616\U0001f611\U0001f610\U0001f613\U0001f612\U0001f61d\u2668\U0001f61f\U0001f61e\U0001f619\U0001f618\U0001f61b\U0001f61a\U0001f605\U0001f604\u26f3\U0001f606\U0001f601\U0001f600\U0001f603\U0001f602\U0001f60d\U0001f60c\U0001f60f\U0001f60e\U0001f609\U0001f608\U0001f60b\U0001f60a\u2709\u25aa\U0001f6c5\U0001f6c4\U0001f6c1\U0001f6c0\U0001f6c3\U0001f6c2\U0001f6b5\U0001f6b4\U0001f6b7\U0001f6b6\U0001f6b1\U0001f6b0\U0001f6b3\U0001f6b2\U0001f6bd\U0001f6bc\U0001f6bf\U0001f6be\U0001f6b9\U0001f6b8\U0001f6bb\U0001f6ba\U0001f6a5\U0001f6a4\u2653\U0001f6a6\U0001f6a1\U0001f6a0\U0001f6a3\U0001f6a2\U0001f6ad\U0001f6ac\U0001f6af\U0001f6ae\U0001f6a9\U0001f6a8\U0001f6ab\U0001f6aa\U0001f695\U0001f694\U0001f697\U0001f696\U0001f691\U0001f690\U0001f693\U0001f692\U0001f69d\U0001f69c\U0001f69f\U0001f69e\U0001f699\U0001f698\U0001f69b\U0001f69a\U0001f685\U0001f684\U0001f687\U0001f686\U0001f681\U0001f680\U0001f683\U0001f682\U0001f68d\U0001f68c\U0001f68f\U0001f68e\U0001f689\U0001f688\U0001f68b\U0001f68a\u2708\u2728\u231b\u2733\u303d\u26be\u2649\u2753\u23f0\u2712\u21a9\u2b06\u2b05\u23ea\u26bd\u2652\u2611\U0001f648\u25fb\u26fd\u261d\U0001f63c\u2747\u2049\u26f2\u2195\u2650\u23e9\U0001f61c\u25fd\u21aa\U0001f607\u267b\u2666\u23f3\U0001f47e\u2194\u27b0\u2651\u25fc]')


def emoji_filter(text):
    if len(emoji_single.findall(text)) > 0:
        return True
    return False


def includes_emoji_filter(text):
    return not emoji_filter(text)


def real_word_ratio(sentance, debug=False, cutoff=None):
    """
    becomes pass/fail if cutoff is not None
    """
    # if not hasattr(real_word_ratio, "words"):
    #     real_word_ratio.words = utils.wordlist()

    sentance = utils.fix_hashtags(sentance)

    sentance = re.sub(r'[#,\.\?\!]', '', sentance)
    sentance_words = [w.lower() for w in sentance.split()]
    if not len(sentance_words):
        return 0

    are_words = [w for w in sentance_words if utils.is_real_word(w)]
    # debuging:
    # not_words = set(sentance_words).difference(set(are_words))

    ratio = float(len(''.join(are_words))) / len(''.join(sentance_words))

    # pass/fail
    if cutoff > 0:
        if ratio < cutoff:
            return True
        else:
            return False

    if debug:
        print('debugging real word ratio:')
        print(sentance, sentance_words, are_words, ratio, sep='\n')
    return ratio


def real_word_ratio_filter(cutoff):
    f = functools.partial(real_word_ratio, **{'cutoff': cutoff})
    f.__doc__ = "filtering real-word-ratio with cutoff %0.2f" % cutoff
    return f


def rhymes_with_word(text, word):
    rhyme_word = rhyme.rhyme_word(text)
    if rhyme.words_rhyme(rhyme_word, word):
        return False
    return True


def rhyme_filter(word):
    f = functools.partial(rhymes_with_word, **{'word': word})
    f.__doc__ = "filtering for rhymes with %s" % word
    return f


def emoticons(text):
    # non functional
    emotes = re.findall(r'[=:;].{0,2}[\(\)\[\]\{\}|\\\$DpoO0\*]+', text)
    return emotes


def _convert_custom_regex(in_re):
    """
    takes a string in our custom regex format
    and converts it to acceptable regex 
    """
    regex = re.sub(r'([^\\])(?:~)([a-zA-Z]*)',
                   lambda m: '%s(%s)' % (
                       m.group(1), '|'.join(utils.synonyms(m.group(2)))),
                   in_re)  # expand '~word' to a (list|of|synonyms)

    regex = re.sub(r'\\~', '~', regex)  # replace escaped tildes
    return regex


def main():
    pass


if __name__ == "__main__":
    main()
