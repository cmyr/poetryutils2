# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict, Counter, namedtuple
import sys
import re
import functools

from . import rhyme
from .syllables import count_syllables

NormalizedLine = namedtuple('NormalizedLine', ['text', 'info'])


class Poem(object):

    """lines + metadata"""

    def __init__(self, poem_type, lines):
        super(Poem, self).__init__()
        self.poem_type = poem_type
        self.lines = lines

    def __str__(self):
        return str(unicode(self).encode('utf-8'))

    def __unicode__(self):
        return "\n" + "\n".join(l.text for l in self.lines) + "\n"

    def to_dict(self):
        return {
            'poem_type': self.poem_type,
            'lines': [{"text": l.text, "info": l.info} for l in self.lines]
        }

    def pretty_print(self):
        return unicode(self)


class Poet(object):

    """Poet is an abstract superclass for poem generators."""

    def __init__(self, debug=False):
        super(Poet, self).__init__()
        self.lines_seen = 0
        self.debug = debug
        self._poem_type = "base poem"

    @property
    def poem_type(self):
        return self._poem_type

    def generate_from_source(self, source, key=None, yield_lines=False):
        for item in source:
            line = self.normalize_line(item, key)
            self.lines_seen += 1
            if yield_lines:
                yield line.text
            poem = self.add_line(line)

            # multipoet returns lists of poems
            if isinstance(poem, list):
                for p in poem:
                    yield p
            elif isinstance(poem, Poem):
                yield poem

    def add_keyed_line(self, line, key=None, yield_lines=False):
        line = self.normalize_line(line, key)
        self.lines_seen += 1
        poem = self.add_line(line)
        if poem:
            return poem

    def normalize_line(self, line, key):
        if isinstance(line, basestring):
            if isinstance(line, str):
                line = NormalizedLine(line.decode('utf-8'), None)
            else:
                line = NormalizedLine(line, None)
        else:
            if not key:
                print('non-string sources require a key')
                return
            line = NormalizedLine(line[key], line)
        return line

    def add_line(self, line):
        # poems are tuples for a reason i should probably revisit?
        return Poem(self.poem_type, [line])

    def dictify(self, poem):
        return [{"text": l.text, "info": l.info} for l in poem]


class Rhymer(Poet):

    """
    finds pairs of rhymes in input
    our only basic worry is quality checking our rhymes?
    """

    def __init__(self, debug=False, rhyme_count=2, lang='en'):
        super(Rhymer, self).__init__(debug)
        self.endings = defaultdict(list)
        self.rhyme_count = rhyme_count
        self._poem_type = "rhyme"
        self.language = lang
        self.rhyme_finder = rhyme.rhymer_for_language(self.language)

    def add_line(self, line, raw=False):
        """
        because rhymer is used by other poet subclasses
        the raw flag returns just lines, instead of Poem objects
        """
        # with self.rhyme_finder as rf:
        #     end_sound = rf.
        end_word = self.rhyme_finder.rhyme_word(line.text)
        if end_word:
            end_sound = self.rhyme_finder.sound_for_word(end_word)

            if self.not_homophonic(line, end_sound):
                self.endings[end_sound].append(line)
                if len(self.endings[end_sound]) == self.rhyme_count:
                    if raw:
                        to_return = tuple(self.endings[end_sound])
                    else:
                        to_return = Poem(self.poem_type,
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

    def __init__(self, lang='en'):
        super(Coupler, self).__init__()
        self.lang = lang
        _Rhymer = functools.partial(Rhymer, lang=self.lang)
        self.rhymers = defaultdict(_Rhymer)
        self._poem_type = "couplet"

    def add_line(self, line):
        syllable_count = count_syllables(line.text)
        return self.rhymers[syllable_count].add_line(line)


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

    def add_line(self, line):
        syllable_count = count_syllables(line.text)
        if syllable_count in self.desired_syllables_set:
            self.lines[syllable_count].append(line)
            return self.check_for_art()

    def check_for_art(self):
        for syllables, count in self.syllable_numbers.items():
            if len(self.lines[syllables]) < count:
                return

        return Poem(self.poem_type, [self.lines[s].pop() for s in self.line_syllables])


class Limericker(Poet):

    """finds limericks"""

    def __init__(self, debug=False, lang='en'):
        super(Limericker, self).__init__(debug)
        self.lines = defaultdict(list)
        self.lang = lang
        self.rhymers = {9: Rhymer(rhyme_count=3, lang=self.lang), 6: Rhymer(lang=self.lang)}
        self._poem_type = "limerick"

    def add_line(self, line):
        syllable_count = count_syllables(line.text)
        new_rhyme = None
        if syllable_count == 6 or syllable_count == 9:
            new_rhyme = self.rhymers[syllable_count].add_line(line, raw=True)

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
                        return Poem(self.poem_type, lines)

    def debug_info(self):
        for (key, value) in self.lines.items():
            print('lines[%d] = %d' % (key, len(value)))
        for count in (6, 9):
            print("%d syllable rhymes:" % count)
            self.rhymers[count].debug_info()

# class Villaneller(Poet):
#     """ finds villanelles """
#     def __init__(self):
#         super(Villaneller, self).__init__()
#         self.lines = defaultdict(list)
#         self.rhymer = Rhymer(rhyme_count=7)

#     def add_line(self, line):
#         new_rhyme = False
#         syllable_count = count_syllables(line.text)
#         if syllable_count == 10:
#             new_rhyme = self.rhymer.add_line(line, raw=True)

#         if new_rhyme:



class Haikuer(Poet):

    """writes boooootiful poem"""

    def __init__(self, debug=False):
        super(Haikuer, self).__init__(debug)
        self.sevens = list()
        self.fives = list()
        self.number_of_poems = 0
        self.item_lookup = dict()
        self._poem_type = "haiku"

    def add_line(self, line):
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
                        [self.fives.pop(),
                         self.sevens.pop(),
                         self.fives.pop()]
                        )


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

    def add_line(self, line):
        tags = TextBlob(line.text).tags
        for word, tag in tags:
            if tag in self.looking_for_pos:
                self.handle_new_word((word, tag))
        return self.check_for_art()

    def handle_new_word(self, tagged_word):
        i = self.pos_map.index(tagged_word[1])
        assert i != None, "failed to find %s in pos map" % tagged_word[1]
        self.pos_map[i] = None
        self.found_words[i] = tagged_word[0]
        self.looking_for_pos = set(i for i in self.pos_map if i != None)

    def check_for_art(self):
        if len(self.looking_for_pos) == 0:
            outlines = list()
            for line in self.normalized:
                outlines.append(" ".join(self.found_words[:len(line)]))
                self.found_words = self.found_words[len(line):]

            self.reset()
            return Poem(self.poem_type,
                        [NormalizedLine(l, None) for l in outlines])


class Concrete(Poet):

    """writes concrete poems, where the qualifier is line length."""

    def __init__(self, line_lengths=list(range(8, 40)), show_progress=False):
        super(Concrete, self).__init__()
        self.line_lengths = line_lengths
        self.next_index = 0
        self.lines = list()
        self.show_progress = show_progress
        self._poem_type = "concrete"

    def add_line(self, line):
        if len(line.text) == self.line_lengths[self.next_index]:
            self.lines.append(line)
            self.next_index = (self.next_index + 1) % len(self.line_lengths)
            if self.next_index != 0 and self.show_progress:
                return Poem(self.poem_type, self.lines)
            else:
                lines = list(self.lines)
                self.lines = list()
                return Poem(self.poem_type, lines)


class MultiPoet(Poet):

    """wraps multiple poet subclasses, feeding lines to each"""

    def __init__(self, poets):
        super(MultiPoet, self).__init__()
        self.poets = poets
        self.keyed_poets = {p.poem_type: p for p in poets}
        self._poem_type = "multipoet"

    def add_line(self, line):
        poems = [p.add_line(line) for p in self.poets]
        poems = [p for p in poems if p]
        if len(poems):
            return poems

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
