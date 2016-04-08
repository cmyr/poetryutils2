# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import subprocess

ESPEAK_LANG_TABLE = {
    'en': 'en-us',
    'fr': 'fr'
    }


def _get_espeak_command():
    '''extracting phonemes relies on espeak (http://espeak.sourceforge.net)
    espeak is aliased to 'speak' on some systems
    '''
    if not hasattr(_get_espeak_command, 'ESPEAK_COMMAND_NAME'):
        cmd = None
        if subprocess.call(["espeak", "--version"]) == 0:
            cmd = 'espeak'
        elif subprocess.call(["speak", "--version"]) == 0:
            cmd = "speak"
        else:
            raise ImportError(
                "rhyme module requires espeak to be installed. http://espeak.sourceforge.net")

        setattr(_get_espeak_command, 'ESPEAK_COMMAND_NAME', cmd)
    return getattr(_get_espeak_command, 'ESPEAK_COMMAND_NAME')


def extract_phonemes(word, lang='en'):
        cmd = [
            _get_espeak_command(), '-v',
            ESPEAK_LANG_TABLE[lang],
            '-q', '--ipa', word]
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        phonemes = output.stdout.read().decode('utf-8').strip()
        return word, phonemes
