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
                print('homophones:\n%s\n%s' % (line, other_line))
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


class Limericker(object):
    """finds limericks"""
    def __init__(self):
        super(Limericker, self).__init__()
        self.lines = defaultdict(list)
        self.nines = Rhymer(line_count=3)
        self.sixes = Rhymer()


    def add_line(self, line):
        syllable_count = count_syllables(line)
        new_rhyme = None
        lines = None
        if syllables == 6:
            lines, new_rhyme = 6, self.sixes.add_line(line)
        elif syllables == 9:
            lines, new_rhyme = 9, self.nines.add_line(line)

        self.lines[lines] = new_rhyme
        return self.check_for_art()


    def check_for_art(self):
        if (len(self.lines[9]) and len(self.lines[6]) and 
            not rhyme.lines_rhyme(self.lines[9][0], self.lines[6][0])):

            nines = self.lines[9].pop()
            sixes = self.lines[6].pop()

            poem = (nines.pop(), nines.pop(), sixes.pop(), sixes.pop(), nines.pop())
            return poem

    def generate_from_source(self, source):
        for line in source:
            poem = self.add_line(line)
            if poem:
                yield poem


#     def add_line(self, line):
#         syllable_count = poetryutils2.count_syllables(line)
#         return self.rhymers[syllable_count].add_line(line)

        
# def coupler(input_iter):
#     line_lengths = dict()

def couplet_iter(source):
    coupler = poetryutils2.Coupler()
    for line in source:
        result = coupler.add_line(line)
        if result:
            yield result

def main():
    pass

if __name__ == "__main__":
    main()