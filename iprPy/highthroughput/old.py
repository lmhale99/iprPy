from __future__ import print_function
import os
import sys
import argparse

PY3 = sys.version_info[0] > 2 

def screen_input(prompt=''):
    """input function compatible with python 2,3 and mingw"""
    print(prompt, end='')
    sys.stdout.flush()
    if PY3: return input()
    else: return raw_input()
    
parser = argparse.ArgumentParser(description='Run iprPy high-throughput commands.')

parser.add_argument('action', help=' = build, check, clean, copy, create, destroy or runner')
parser.add_argument('args', help='action-specific optional keywords', nargs=argparse.REMAINDER)

args = parser.parse_args()

if args.action == 'build':
    print('YAY')