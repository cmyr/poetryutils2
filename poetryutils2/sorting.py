# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict, Counter, namedtuple
import sys
import re

from textblob import TextBlob
from . import rhyme
from .syllables import count_syllables

NormalizedLine = namedtuple('NormalizedLine', ['text', 'info'])


class Poet(object):

    """Poet is an abstract superclass for poem generators."""

    def __init__(self, debug=False):
        super(Poet, self).__init__()
        self.lines_seen = 0
        self.debug = debug

    def identifier(self):
        return self.__doc__

    def generate_from_source(self, source, key=None, yield_lines=False):
        for item in source:
            if isinstance(item, basestring):
                if isinstance(item, str):
                    line = NormalizedLine(item.decode('utf-8'), None)
                else:
                    line = NormalizedLine(item, None)
            else:
                if not key:
                    print('non-string sources require a key')
                    return
                line = NormalizedLine(item[key], item)

            self.lines_seen += 1
            if yield_lines:
                yield line.text
            poem = self.add_line(line)
            # multipoet returns lists of poems
            if isinstance(poem, list):
                for p in poem:
                    yield p
            elif isinstance(poem, tuple):
                yield poem

    def add_line(self, line):
        # poems are tuples for a reason i should probably revisit?
        return (line,)

    def prettify(self, poem):
        lines = [l.text for l in poem]
        return "\n" + "\n".join(lines) + "\n"

    def dictify(self, poem):
        return [{"text": l.text, "info": l.info} for l in poem]


class Rhymer(Poet):

    """
    finds pairs of rhymes in input
    our only basic worry is quality checking our rhymes?
    """

    def __init__(self, debug=False, rhyme_count=2):
        super(Rhymer, self).__init__(debug)
        self.endings = defaultdict(list)
        self.rhyme_count = rhyme_count

    def add_line(self, line):
        end_word = rhyme.rhyme_word_if_appropriate(line.text)
        if end_word:
            end_sound = rhyme.sound_for_word(end_word)

            if self.not_homophonic(line, end_sound):
                self.endings[end_sound].append(line)
                if len(self.endings[end_sound]) == self.rhyme_count:
                    to_return = tuple(self.endings[end_sound])
                    self.endings[end_sound] = list()
                    return to_return

    def not_homophonic(self, line, end_sound):
        for other_line in self.endings[end_sound]:
            if not rhyme.lines_rhyme(line.text, other_line.text):
                # print('homophones:\n%s\n%s' % (line, other_line))
                return False

        return True

    def debug_info(self):
        ending_counts = Counter([len(v) for v in self.endings.values()])
        for item, count in ending_counts.most_common():
            print("%d rhyme groups with length %d" % (count, item))


class Coupler(Poet):

    """finds rhyming couplets"""

    def __init__(self):
        super(Coupler, self).__init__()
        self.rhymers = defaultdict(Rhymer)

    def add_line(self, line):
        syllable_count = count_syllables(line.text)
        return self.rhymers[syllable_count].add_line(line)


class SyllablePoet(Poet):
    """Generates poems with lines of given syllable counts"""
    def __init__(self, line_syllables):
        super(SyllablePoet, self).__init__()
        self.line_syllables = line_syllables
        self.desired_syllables_set = set(line_syllables)
        self.syllable_numbers = {s: line_syllables.count(s) for s in set(line_syllables)}
        self.lines = defaultdict(list)

    def add_line(self, line):
        syllable_count = count_syllables(line.text)
        if syllable_count in self.desired_syllables_set:
            self.lines[syllable_count].append(line)
            return self.check_for_art()

    def check_for_art(self):
        for syllables, count in self.syllable_numbers.items():
            if len(self.lines[syllables]) < count:
                return

        return tuple([self.lines[s].pop() for s in self.line_syllables])


        
class Limericker(Poet):

    """finds limericks"""

    def __init__(self, debug=False):
        super(Limericker, self).__init__(debug)
        self.lines = defaultdict(list)
        self.rhymers = {9: Rhymer(rhyme_count=3), 6: Rhymer()}

    def add_line(self, line):
        syllable_count = count_syllables(line.text)
        new_rhyme = None
        if syllable_count == 6 or syllable_count == 9:
            new_rhyme = self.rhymers[syllable_count].add_line(line)

        if new_rhyme:
            self.lines[syllable_count].append(new_rhyme)
            return self.check_for_art()

    def check_for_art(self):
        if len(self.lines[9]) and len(self.lines[6]):
            for niner in self.lines[9]:
                for sixer in self.lines[6]:
                    if not rhyme.lines_rhyme(niner[0].text, sixer[0].text):
                        self.lines[9].remove(niner)
                        self.lines[6].remove(sixer)
                        poem = (
                            niner[0], niner[1], sixer[0], sixer[1], niner[2])
                        return poem

    def debug_info(self):
        for (key, value) in self.lines.items():
            print('lines[%d] = %d' % (key, len(value)))
        for count in (6, 9):
            print("%d syllable rhymes:" % count)
            self.rhymers[count].debug_info()


class Haikuer(Poet):

    """writes boooootiful poem"""

    def __init__(self, debug=False):
        super(Haikuer, self).__init__(debug)
        self.sevens = list()
        self.fives = list()
        self.number_of_poems = 0
        self.item_lookup = dict()

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

            return (
                self.fives.pop(),
                self.sevens.pop(),
                self.fives.pop()
            )

class Mimic(Poet):
    """docstring for Mimic"""
    def __init__(self, poem):
        super(Mimic, self).__init__()
        self.poem = poem
        self.normalized = self.normalize_poem(poem)
        self.pos = self.line_pos(self.normalized)
        self.reset()
        

    def reset(self):
        self.pos_map = list(self.pos)
        self.found_words = [None for w in self.pos]
        self.looking_for_pos = set(self.pos)
        # print(self.pos)
        # print(self.normalized, self.pos_map, self.looking_for_pos)

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
            return tuple(NormalizedLine(l, None) for l in outlines)


class Concrete(Poet):
    """writes concrete poems, where the qualifier is line length."""
    def __init__(self, line_lengths=list(range(8, 40))):
        super(Concrete, self).__init__()
        self.line_lengths = line_lengths
        self.next_index = 0
        self.lines = list()
        print(self.line_lengths)

    def add_line(self, line):
        if len(line.text) == self.line_lengths[self.next_index]:
            self.lines.append(line)
            self.next_index = (self.next_index + 1) % len(self.line_lengths)
            if self.next_index != 0:
                return tuple(self.lines)
            else:
                poem = tuple(self.lines)
                self.lines = list()
                return poem


class MultiPoet(Poet):
    """wraps multiple poet subclasses, feeding lines to each"""
    def __init__(self, poets):
        super(MultiPoet, self).__init__()
        self.poets = poets
        self.keyed_poets = {p.identifier(): p for p in poets}
        
    def add_line(self, line):
        poems = [p.add_line(line) for p in self.poets]
        poems = [p for p in poems if p]
        if len(poems):
            return poems

    def add_poet(self, poet, key=None):
        self.poets.append(poet)
        pkey = key or poet.identifier()
        self.keyed_poets[pkey] = poet

    def replace_poet(self, poet, key=None):
        pkey = key or poet.identifier()
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
