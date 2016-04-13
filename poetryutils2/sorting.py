# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict, Counter
import sys
import re
import functools

from . import rhyme, utils
from .syllables import count_syllables


class Line(object):
    '''a line in a poem, with some associated metadata'''

    def __init__(self, text, info=None, end_sound=None, syllable_count=None):
        self._text = text
        self._info = info
        self._end_sound = end_sound
        self._syllable_count = syllable_count

    @property
    def text(self):
        return self._text

    @property
    def info(self):
        return self._info

    @property
    def end_sound(self):
        return self._end_sound

    @property
    def syllable_count(self):
        return self._syllable_count

    def __repr__(self):
        return ("<Line: %s>" % self.text).encode('utf-8')

    def __str__(self):
        return self.text.encode('utf-8')


class Poem(object):

    """lines + metadata"""

    def __init__(self, poem_type, lang, lines, line_breaks=None):
        '''if line_breaks is not None it should be an iterable of indexes
        cooresponding to lines after which we should insert a newline.'''
        super(Poem, self).__init__()
        self._poem_type = poem_type
        self._lang = lang
        self._lines = lines
        self.line_breaks = line_breaks

    @property
    def lang(self):
        return self._lang

    @property
    def poem_type(self):
        return self._poem_type

    @property
    def lines(self):
        return self._lines

    def __str__(self):
        return str(unicode(self).encode('utf-8'))

    def __unicode__(self):
        if not self.line_breaks:
            return "\n%s\n" % "\n".join(l.text for l in self.lines)
        else:
            out = []
            for idx, line in enumerate(self.lines):
                out.append(line.text)
                if idx in self.line_breaks:
                    out.append('')
            return '\n%s\n' % '\n'.join(out)

    def __repr__(self):
        return self.to_dict()

    def to_dict(self):
        return {
            'poem_type': self.poem_type,
            'lang': self.lang,
            'lines': [{"text": l.text, "info": l.info} for l in self.lines]
        }

    def pretty_print(self):
        return unicode(self)


class Poet(object):

    """Poet is an abstract superclass for poem generators."""

    def __init__(self, debug=False, lang='en'):
        super(Poet, self).__init__()
        self.lines_seen = 0
        self.debug = debug
        self.lang = lang
        self._poem_type = "base poem"

    @property
    def poem_type(self):
        return self._poem_type

    def generate_from_source(self, source, key=None, yield_lines=False):
        for item in source:
            if yield_lines:
                yield self.normalize_line(item, key).text

            poems = self.add_keyed_line(item, key)
            if not poems:
                continue

            if not isinstance(poems, list):
                poems = [poems]
            for p in poems:
                yield p

    def add_keyed_line(self, line, key=None):
        line = self.normalize_line(line, key)
        # skip lines not in our language
        if self.lang and line.info and line.info.get('lang', self.lang) != self.lang:
            return None
        self.lines_seen += 1
        poem = self._add_line(line)
        return poem

    def normalize_line(self, line, key):
        if utils.isstring(line):
            line = utils.unicodify(line)
            return Line(line, None)
        else:
            if not key:
                raise Exception('non-string sources require a key')
            line = Line(line[key], line)
        return line

    def _add_line(self, line):
        return Poem(poem_type=self.poem_type, lang=self.lang, lines=[line])


class Rhymer(Poet):

    """
    finds pairs of rhymes in input
    our only basic worry is quality checking our rhymes?
    """

    def __init__(self, rhyme_count=2, **kwargs):
        super(Rhymer, self).__init__(**kwargs)
        self.endings = defaultdict(list)
        self.rhyme_count = rhyme_count
        self._poem_type = "rhyme"
        self.rhyme_finder = rhyme.rhymer_for_language(self.lang)

    def _add_line(self, line, raw=False):
        """
        because rhymer is used by other poet subclasses
        the raw flag returns just lines, instead of Poem objects
        """
        end_word = self.rhyme_finder.rhyme_word(line.text)
        if end_word:
            end_sound = self.rhyme_finder.sound_for_word(end_word)
            line._end_sound = end_sound
            if self.debug:
                print(line, end_word, end_sound)
            if self.not_homophonic(line, end_sound):
                self.endings[end_sound].append(line)
                if len(self.endings[end_sound]) == self.rhyme_count:
                    if raw:
                        to_return = tuple(self.endings[end_sound])
                    else:
                        to_return = Poem(self.poem_type,
                                         self.lang,
                                         list(self.endings[end_sound]))
                    self.endings[end_sound] = list()
                    return to_return

    def not_homophonic(self, line, end_sound):
        for other_line in self.endings[end_sound]:
            if not self.rhyme_finder.is_rhyme(line.text, other_line.text):
                # print('homophones:\n%s\n%s' % (line, other_line))
                return False

        return True

    def debug_info(self):
        ending_counts = Counter([len(v) for v in self.endings.values()])
        for item, count in ending_counts.most_common():
            print("%d rhyme groups with length %d" % (count, item))


class Coupler(Poet):

    """finds rhyming couplets"""

    def __init__(self, syllable_counts=None, **kwargs):
        """finds rhyming couplets with equal syllable counts.
        :param syllable_counts: None or int or collection of ints or str .
        If str, should contain numbers, ',' and '-', describing a range, e.g:
        '1,2,6-9' == [1, 2, 6, 7, 8, 9] """

        super(Coupler, self).__init__(**kwargs)
        self.syllable_counts = syllable_counts
        if utils.isstring(syllable_counts):
            self.syllable_counts = set(utils.parse_range_string(syllable_counts))
        elif hasattr(syllable_counts, '__len__'):
            self.syllable_counts = set(syllable_counts)
        elif isinstance(syllable_counts, int):
            self.syllable_counts = set([syllable_counts])

        _Rhymer = functools.partial(Rhymer, lang=self.lang)
        self.rhymers = defaultdict(_Rhymer)
        self._poem_type = "couplet"

    def _add_line(self, line, raw=False):
        syllable_count = count_syllables(line.text)
        if not self.syllable_counts or syllable_count in self.syllable_counts:
            poem = self.rhymers[syllable_count]._add_line(line, raw=raw)
            if poem and not raw:
                poem._poem_type = self.poem_type
            return poem


class SyllablePoet(Poet):

    """Generates poems with lines of given syllable counts"""

    def __init__(self, line_syllables):
        super(SyllablePoet, self).__init__()
        self.line_syllables = line_syllables
        self.desired_syllables_set = set(line_syllables)
        self.syllable_numbers = {
            s: line_syllables.count(s) for s in set(line_syllables)}
        self.lines = defaultdict(list)
        self._poem_type = "syllable poem"

    def _add_line(self, line):
        syllable_count = count_syllables(line.text)
        if syllable_count in self.desired_syllables_set:
            self.lines[syllable_count].append(line)
            return self.check_for_art()

    def check_for_art(self):
        for syllables, count in self.syllable_numbers.items():
            if len(self.lines[syllables]) < count:
                return

        return Poem(
            self.poem_type,
            self.lang,
            [self.lines[s].pop() for s in self.line_syllables])


class Limericker(Poet):

    """finds limericks"""

    def __init__(self, **kwargs):
        super(Limericker, self).__init__(**kwargs)
        self.lines = defaultdict(list)
        self.rhymers = {9: Rhymer(rhyme_count=3, lang=self.lang), 6: Rhymer(lang=self.lang)}
        self._poem_type = "limerick"

    def _add_line(self, line):
        syllable_count = count_syllables(line.text)
        new_rhyme = None
        if syllable_count == 6 or syllable_count == 9:
            new_rhyme = self.rhymers[syllable_count]._add_line(line, raw=True)

        if new_rhyme:
            self.lines[syllable_count].append(new_rhyme)
            return self.check_for_art()

    def check_for_art(self):
        if len(self.lines[9]) and len(self.lines[6]):
            for niner in self.lines[9]:
                for sixer in self.lines[6]:
                    if not self.rhymers[9].rhyme_finder.is_rhyme(niner[0].text, sixer[0].text):
                        self.lines[9].remove(niner)
                        self.lines[6].remove(sixer)
                        lines = [
                            niner[0], niner[1], sixer[0], sixer[1], niner[2]]
                        return Poem(self.poem_type, self.lang, lines)

    def debug_info(self):
        for (key, value) in self.lines.items():
            print('lines[%d] = %d' % (key, len(value)))
        for count in (6, 9):
            print("%d syllable rhymes:" % count)
            self.rhymers[count].debug_info()


class Haikuer(Poet):

    """writes boooootiful poem"""

    def __init__(self, **kwargs):
        super(Haikuer, self).__init__(**kwargs)
        self.sevens = list()
        self.fives = list()
        self.number_of_poems = 0
        self.item_lookup = dict()
        self._poem_type = "haiku"

    def _add_line(self, line):
        if self.debug:
            sys.stdout.write("seen %d\r" % self.lines_seen)
            sys.stdout.flush()
        syllable_count = count_syllables(line.text)
        if syllable_count == 5:
            self.fives.append(line)

        elif syllable_count == 7:
            self.sevens.append(line)

        if (len(self.fives) >= 2 and len(self.sevens)):
            if self.debug:
                self.number_of_poems += 1
                print('found %d haiku in %d lines' % (
                    self.number_of_poems,
                    self.lines_seen)
                )

            return Poem(self.poem_type,
                        self.lang,
                        [self.fives.pop(),
                         self.sevens.pop(),
                         self.fives.pop()]
                        )


class FleurDuMal(Poet):
    def __init__(self, **kwargs):
        super(FleurDuMal, self).__init__(**kwargs)
        self.coupler = Coupler((12, 10))
        self.couplets = defaultdict(list)
        self.rhyme_finder = rhyme.rhymer_for_language(self.lang)
        self._poem_type = 'baudelairist'

    def _add_line(self, line):
        syllable_count = count_syllables(line.text, lang=self.lang)
        if syllable_count in (10, 12):
            couplet = self.coupler._add_line(line, raw=True)
            if couplet:
                return self.check_fo_art(couplet, syllable_count)

    def check_fo_art(self, couplet, syllable_count):
        other_key = 12 if syllable_count == 10 else 10
        if len(self.couplets[other_key]):
            for other_couplet in self.couplets[other_key]:
                if not self.rhyme_finder.is_rhyme(couplet[0].text, other_couplet[0].text):
                    self.couplets[other_key].remove(other_couplet)
                    longer = couplet if syllable_count == 12 else other_couplet
                    shorter = couplet if syllable_count == 10 else other_couplet
                    return Poem(
                        self.poem_type,
                        self.lang,
                        lines=[longer[0], shorter[0], shorter[1], longer[1]])
        # no match found, add to couplets
        self.couplets[syllable_count].append(couplet)


class Sonnetter(Poet):
    def __init__(self, **kwargs):
        super(Sonnetter, self).__init__(**kwargs)
        self.coupler = Coupler(10)
        self.couplets = defaultdict(list)
        self._poem_type = 'sonnet'
        self.line_breaks = set([3, 7, 11])

    def _add_line(self, line):
        couplet = self.coupler._add_line(line, raw=True)
        if couplet:
            self.couplets[line.end_sound].append(couplet)
            return self.check_for_art()

    def check_for_art(self):
        sounds_with_couplets = [k for k in self.couplets if len(self.couplets[k])]
        if len(sounds_with_couplets) >= 7:
            sounds_with_couplets = sounds_with_couplets[:7]
            couplets = [list(self.couplets[k].pop()) for k in sounds_with_couplets]
            assert len(couplets) == 7

            lines = list(
                zip(couplets[0], couplets[1]) +
                zip(couplets[2], couplets[3]) +
                zip(couplets[4], couplets[5]))

            lines = [l for ll in lines for l in ll] + list(couplets[6])

            return Poem(
                poem_type=self.poem_type,
                lang=self.lang,
                lines=lines,
                line_breaks=self.line_breaks)


class Mimic(Poet):

    """docstring for Mimic"""

    def __init__(self, poem):
        try:
            TextBlob()
        except NameError:
            try:
                from textblob import TextBlob
            except ImportError:
                print('use of mimic requires textblob module.')
                sys.exit(1)

        super(Mimic, self).__init__()
        self.poem = poem
        self.normalized = self.normalize_poem(poem)
        self.pos = self.line_pos(self.normalized)
        self._poem_type = "mimic"
        self.reset()

    def reset(self):
        self.pos_map = list(self.pos)
        self.found_words = [None for w in self.pos]
        self.looking_for_pos = set(self.pos)

    def normalize_poem(self, poem):
        normalized = re.sub(r'—', ' ', poem)
        return normalized.splitlines()

    def line_pos(self, lines):
        pos = [TextBlob(l).tags for l in lines]
        pos = [p for l in pos for w, p in l]
        return pos

    def _add_line(self, line):
        tags = TextBlob(line.text).tags
        for word, tag in tags:
            if tag in self.looking_for_pos:
                self.handle_new_word((word, tag))
        return self.check_for_art()

    def handle_new_word(self, tagged_word):
        i = self.pos_map.index(tagged_word[1])
        assert i is not None, "failed to find %s in pos map" % tagged_word[1]
        self.pos_map[i] = None
        self.found_words[i] = tagged_word[0]
        self.looking_for_pos = set(i for i in self.pos_map if i is not None)

    def check_for_art(self):
        if len(self.looking_for_pos) == 0:
            outlines = list()
            for line in self.normalized:
                outlines.append(" ".join(self.found_words[:len(line)]))
                self.found_words = self.found_words[len(line):]

            self.reset()
            return Poem(self.poem_type,
                        [Line(l, None) for l in outlines])

# class Villaneller(Poet):
#     """ finds villanelles """
#     def __init__(self):
#         super(Villaneller, self).__init__()
#         self.lines = defaultdict(list)
#         self.rhymer = Rhymer(rhyme_count=7)

#     def _add_line(self, line):
#         new_rhyme = False
#         syllable_count = count_syllables(line.text)
#         if syllable_count == 10:
#             new_rhyme = self.rhymer._add_line(line, raw=True)

#         if new_rhyme:


class Concrete(Poet):

    """writes concrete poems, where the qualifier is line length."""

    def __init__(self, line_lengths=list(range(8, 40)), show_progress=False, **kwargs):
        super(Concrete, self).__init__(**kwargs)
        self.line_lengths = line_lengths
        self.next_index = 0
        self.lines = list()
        self.show_progress = show_progress
        self._poem_type = "concrete"

    def _add_line(self, line):
        if len(line.text) == self.line_lengths[self.next_index]:
            self.lines.append(line)
            self.next_index = (self.next_index + 1) % len(self.line_lengths)
            if self.next_index != 0 and self.show_progress:
                return Poem(self.poem_type, self.lang, self.lines)
            else:
                lines = list(self.lines)
                self.lines = list()
                return Poem(self.poem_type, self.lang, lines)


class MultiPoet(Poet):

    """wraps multiple poet subclasses, feeding lines to each"""

    def __init__(self, poets):
        super(MultiPoet, self).__init__()
        self.poets = poets
        self.keyed_poets = {p.poem_type: p for p in poets}
        self._poem_type = "multipoet"
        self.lang = None

    def add_keyed_line(self, line, key=None):
        self.lines_seen += 1
        poems = [p.add_keyed_line(line, key) for p in self.poets]
        poems = [p for p in poems if p]
        return poems if len(poems) else None

    def add_poet(self, poet, key=None):
        self.poets.append(poet)
        pkey = key or poet.poem_type
        self.keyed_poets[pkey] = poet

    def replace_poet(self, poet, key=None):
        pkey = key or poet.poem_type
        existing = self.keyed_poets.get(pkey)
        if existing:
            idx = self.poets.index(existing)
            self.poets[idx] = poet
        self.keyed_poets[pkey] = poet

    def remove_poet(self, key):
        if key in self.keyed_poets:
            self.poets.remove(self.keyed_poets[key])
            del self.keyed_poets[key]


def main():
    pass

if __name__ == "__main__":
    main()
