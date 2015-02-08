# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

from . import rhyme
from .syllables import count_syllables


class Rhymer(object):
    """
    finds pairs of rhymes in input
    our only basic worry is quality checking our rhymes?
    """
    def __init__(self, rhyme_count=2):
        super(Rhymer, self).__init__()
        self.endings = defaultdict(list)
        self.rhyme_count = rhyme_count

    def add_line(self, line):
        # get our end sound
        end_word = rhyme.rhyme_word_if_appropriate(line)

        if end_word:
            end_sound = rhyme.sound_for_word(end_word)

            if self.not_homophonic(line, end_sound):
                self.endings[end_sound].append(line)
                if len(self.endings[end_sound]) == self.rhyme_count:
                    to_return = tuple(self.endings[end_sound])
                    self.endings[end_sound] = list()
                    return to_return

            # rhyme_line = self.endings.get(end_sound)
            # if rhyme_line and rhyme.lines_rhyme(line, rhyme_line):

                # print('\n', line, rhyme, sep='\n')
            #     self.endings[end_sound] = None
            #     return (line, rhyme_line)
            # else:
            #     self.endings[end_sound] = line

    def not_homophonic(self, line, end_sound):
        for other_line in self.endings[end_sound]:
            if not rhyme.lines_rhyme(line, other_line):
                # print('homophones:\n%s\n%s' % (line, other_line))
                return False

        return True



    def debug(self):
        print(self.endings)



class Coupler(object):
    """finds rhyming couplets"""
    def __init__(self):
        super(Coupler, self).__init__()
        self.rhymers = defaultdict(Rhymer)

    def add_line(self, line):
        syllable_count = count_syllables(line)
        return self.rhymers[syllable_count].add_line(line)

    def generate_from_source(self, source):
        for line in source:
            couplet = self.add_line(line)
            if couplet:
                yield couplet


class Limericker(object):
    """finds limericks"""
    def __init__(self):
        super(Limericker, self).__init__()
        self.lines = defaultdict(list)
        self.nines = Rhymer(rhyme_count=3)
        self.sixes = Rhymer()


    def add_line(self, line):
        syllable_count = count_syllables(line)
        new_rhyme = None
        lines = None
        if syllable_count == 6:
            lines, new_rhyme = 6, self.sixes.add_line(line)
        elif syllable_count == 9:
            lines, new_rhyme = 9, self.nines.add_line(line)

        if not new_rhyme:
            return None

        self.lines[lines].append(new_rhyme)
        return self.check_for_art()


    def check_for_art(self):
        if (len(self.lines[9]) and len(self.lines[6]) and 
            not rhyme.lines_rhyme(self.lines[9][0][0], self.lines[6][0][0])):

            nines = self.lines[9].pop()
            sixes = self.lines[6].pop()

            poem = (nines[0], nines[1], sixes[0], sixes[1], nines[2])
            return poem

    def generate_from_source(self, source):
        for line in source:
            poem = self.add_line(line)
            if poem:
                yield poem

    def prettify(self, poem):
        return "\n%s\n%s\n%s\n%s\n%s\n" % poem



class Haikuer(object):
    """writes boooootiful poem"""
    def __init__(self, debug=False):
        self.sevens = list()
        self.fives = list()
        self.debug = debug
        self.lines_seen = 0
        self.number_of_poems = 0
        self.item_lookup = dict()

    def add_line(self, line):
        if self.debug:
            self.lines_seen += 1
        syllable_count = count_syllables(line)
        if syllable_count == 5:
            self.fives.append(line)

        elif syllable_count == 7:
            self.sevens.append(line)

        if (len(self.fives) >=2 and len(self.sevens)):
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

    def generate_from_source(self, source):
        for line in source:
            poem  = self.add_line(line)
            if poem:
                yield poem

    def generate_from_keyed_source(self, keyed_source, key):
        """
        for working with dictionaries rather than strings.
        key should be the dictionary key for the actual text to be analyzed.
        """

        for item in keyed_source:
            line = item[key]
            self.item_lookup[line] = item
            poem = self.add_line(line)
            if poem:
                yield tuple(self.item_lookup[k] for k in poem)


def main():
    pass

if __name__ == "__main__":
    main()