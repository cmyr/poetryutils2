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
cunt
cunts
pussies
shitty
gay
"""

swears = set([x for x in swears.splitlines() if len(x)])

bad_swears = """
faggot
faggots
nigger
niggers
"""

bad_swears = set([x for x in bad_swears.splitlines() if len(x)])
swears.update(bad_swears)

swears_fr = """
tapette
pédale
nique
niquer
pute
suceboule
raton
baise
baiser
black
blacks
bite
bites
putes
pute
niké
nické
niker
nicker
chienne
chiennes
"""

swears_fr = set([x for x in swears_fr.splitlines() if len(x)])


custom_ipa = """
eg ˈɛɡ
thx θˈæŋks
xx ˈɛksˈɛks
selfies sˈɛlfiːz
dms dˈiːɛmz
"""

custom_ipa = [tuple(x.split()) for x in custom_ipa.splitlines() if len(x)]



ukraine = ['show',
 'demand',
 'sbseurovision',
 'azerbaijan',
 'separatist',
 'hungary',
 'trouble',
 'giant',
 'pray',
 'point',
 'reuters',
 'pretty',
 'east',
 'hope',
 'tock',
 'good',
 'song',
 'big',
 'joinus',
 'stop',
 'gonna',
 'game',
 'world',
 'bit',
 'tick',
 'lady',
 'day',
 'netherlands',
 'bad',
 'latvia',
 'troop',
 'night',
 'guy',
 'wheel',
 'england',
 'people',
 'back',
 'eurovision',
 'year',
 'crimea',
 'girl',
 'kiev',
 'wow',
 'prop',
 'wwiii',
 'esc',
 'defy',
 'victory',
 'supporting',
 'pls',
 'mariupol',
 'free',
 'maidan',
 'rebel',
 'wtf',
 'news',
 'ukraine',
 'ahead',
 'country',
 'violence',
 'hamster',
 'hunger',
 'military',
 'ticktock',
 'love',
 'final',
 'drunk',
 'win',
 'washington',
 'vote',
 'message',
 'singing',
 'crisis',
 'market',
 'omg',
 'union',
 'positive',
 'political',
 'referendum',
 'mark',
 'call',
 'calm',
 'pro',
 'friend',
 'odessa',
 'moscow',
 'gas',
 'award',
 'child',
 'russian',
 'hold',
 'pull',
 'war',
 'sweden',
 'meet',
 'feeling',
 'russia',
 'portugal',
 'awesome',
 'fuck',
 'topic',
 'woman',
 'chat',
 'home',
 'border',
 'shit',
 'sings',
 'autonomy',
 'end',
 'civilian',
 'delay',
 'hot',
 'protester',
 'european',
 'week',
 'tension',
 'putin',
 'http',
 'iceland',
 'price',
 'thetraders',
 'america',
 'man',
 'singer',
 'amid',
 'chief',
 'wind',
 'detained',
 'time',
 'entry',
 'talk']

ukraine = set(ukraine)
syria = ['bomb',
 'mission',
 'world',
 'debate',
 'bombing',
 'program',
 'pilot',
 'sniper',
 'assyrian',
 'return',
 'worse',
 'government',
 'breakingnews',
 'watch',
 'assas',
 'suffering',
 'bassel',
 'assad',
 'level',
 'cry',
 'withsyria',
 'troop',
 'cease',
 'ceasefire',
 'neighborhood',
 'people',
 'absolutely',
 'fish',
 'allah',
 'homs',
 'colin',
 'street',
 'election',
 'falafel',
 'iran',
 'god',
 'crucial',
 'middleeast',
 'abi',
 'cradle',
 'capital',
 'cnn',
 'learned',
 'leader',
 'delegate',
 'bistro',
 'korea',
 'explosion',
 'muslim',
 'victory',
 'opposition',
 'exciting',
 'country',
 'days',
 'thing',
 'massive',
 'bringbackourcountry',
 'syria',
 'evacuating',
 'rebel',
 'assadbasharal',
 'civil',
 'washington',
 'scene',
 'stop',
 'cancel',
 'watchdog',
 'crisis',
 'city',
 'ancient',
 'army',
 'west',
 'fight',
 'sends',
 'attack',
 'war',
 'evacuated',
 'kerry',
 'hotel',
 'missile',
 'warn',
 'craft',
 'loose',
 'russian',
 'obama',
 'sabr',
 'impasse',
 'refugee',
 'control',
 'force',
 'pro',
 'israel',
 'topic',
 'armeni',
 'fnriqevorg',
 'syriah',
 'syrian',
 'regime',
 'court',
 'torture',
 'efficient',
 'deserve',
 'peace',
 'chief',
 'chemical',
 'aleppo',
 'conflict',
 'uprising',
 'heartbreaking',
 'utterly',
 'proverb',
 'future',
 'revealed',
 'ummah',
 'barackobama',
 'stronghold',
 'weapon',
 'hhdwsudpcj',
 'push',
 'truce',
 'uno',]

syria = set(syria)