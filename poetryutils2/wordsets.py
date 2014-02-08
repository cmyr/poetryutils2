# coding: utf-8
from __future__ import unicode_literals

swears = """
shit
fuck
shitting
fucking
fucked
shits
fucks
fuckers
pussy
bitch
bitches
asshole
assholes
faggots
faggot
cunt
cunts
pussies
shitty
gay
"""

swears = set([x for x in swears.splitlines() if len(x)])


custom_ipa = """
eg ˈɛɡ
thx θˈæŋks
xx ˈɛksˈɛks
selfies sˈɛlfiːz
"""

custom_ipa = [tuple(x.split()) for x in custom_ipa.splitlines() if len(x)]