# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import poetryutils2
from collections import defaultdict


# class Rhymer(object):
#     """
#     finds pairs of rhymes in input
#     our only basic worry is quality checking our rhymes?
#     """
#     def __init__(self):
#         super(Rhymer, self).__init__()
#         self.endings = dict()

#     def add_line(self, line):
#         # get our end sound
#         end_word = poetryutils2.rhyme.rhyme_word_if_appropriate(line)

#         if end_word:
#             end_sound = poetryutils2.rhyme.sound_for_word(end_word)
#             rhyme = self.endings.get(end_sound)
#             if rhyme and poetryutils2.rhyme.lines_rhyme(line, rhyme):

#                 # print('\n', line, rhyme, sep='\n')
#                 self.endings[end_sound] = None
#                 return (line, rhyme)
#             else:
#                 self.endings[end_sound] = line

#     def debug(self):
#         print(self.endings)



# class Coupler(object):
#     """finds rhyming couplets"""
#     def __init__(self):
#         super(Coupler, self).__init__()
#         self.rhymers = defaultdict(Rhymer)

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


    def debug(self):
        for k in self.rhymers:
            self.rhymers[k].debug()




def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dbpath', type=str, help="path for db to filter")

    args = parser.parse_args()

    file_path = args.dbpath


def tests():
    definite_passes = [
    'one two four five',
    'you feel alive']

    lines = poetryutils2.utils.debug_lines()
    lines.extend(definite_passes)
 
    for couplet in couplet_iter(lines):
        print(couplet[0], '\n', couplet[1])


    # coupler.debug()


if __name__ == "__main__":
    # main()
    tests()