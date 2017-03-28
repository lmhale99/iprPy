from __future__ import print_function
import sys

PY3 = sys.version_info[0] > 2

def screen_input(prompt=''):
    """input function compatible with python 2,3 and mingw"""
    print(prompt, end=' ')
    sys.stdout.flush()
    if PY3: return input()
    else: return raw_input()