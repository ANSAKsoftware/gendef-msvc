#!/usr/bin/env python3

# #########################################################################
#
# Copyright (c) 2022, Arthur N. Klassen
# All rights reserved.
#
#  2022.06.03 - First version
#
#     May you do good and not evil.
#     May you find forgiveness for yourself and forgive others.
#     May you share freely, never taking more than you give.
#
# #########################################################################
#
#  configure.py -- Implement in Python3 what is unavailable on Windows
#                  (outside of MinGW / Cygwin), the minimal autoconf/automake-
#                  like behaviour of the config shell script provided for use
#                  in Linux / MinGW/Cygwin, macOS. For more, see
#
#                  python3 configure.py --help
#
# #########################################################################

import sys
import os
import os.path
import argparse
import pathlib
from subprocess import STDOUT, PIPE
import subprocess

called_by = 'python'
compiler = None
v = False

DEFAULT_PREFIX = 'C:\\ProgramData'


def run_it(*args):
    try:
        p = subprocess.Popen(args, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        return [line.decode('utf-8') for line in p.stdout.readlines()]
    except FileNotFoundError:
        return None


def find_generator():
    global v
    cmake_help_lines = run_it('cmake', '--help')
    if v:
        print("Read {} lines from cmake --help".format(len(cmake_help_lines)))
    studio_lines = [line.strip() for line in cmake_help_lines
                    if "Visual Studio" in line]
    if v:
        print("Read {} Visual Studio generator lines from cmake --help".format(
              len(studio_lines)))
    starred = [line for line in studio_lines if line.startswith('*')]
    if v:
        print("Read {} starred generator line(s) from cmake --help".format(
              len(starred)))
        for s in starred:
            print("   {}".format(s))

    if len(starred) == 0:
        print("No default Visual Studio generator. Install Visual Studio")
        sys.exit(1)
    elif len(starred) > 1:
        print("{} default Visual Studio generators? Something is wrong".format(
              len(starred)))
        sys.exit(1)
    else:
        star_line = starred[0][1:]
        star_left_half = star_line.split('=')[0].strip()
        star_before_bracket = star_left_half.split('[')[0].strip()
        if v:
            print("Default Visual Studio generator found: {}".format(
                  star_before_bracket))
        return star_before_bracket


def main(argv=sys.argv):
    global v

    parser = argparse.ArgumentParser(
            description="Configure script for ansak-string on Windows")
    parser.add_argument('--prefix',
                        help='non-default location to install files (does not '
                             'affect \'make package\')',
                        type=str,
                        default=DEFAULT_PREFIX)
    parser.add_argument('-v', '--verbose',
                        help='more detailed progress messages',
                        action='store_true')

    args = parser.parse_args()
    v = bool(args.verbose)

    # determine ... prefix, MSDev generator
    prefix = os.path.realpath(args.prefix)
    if not os.path.isdir(prefix):
        pathlib.Path(prefix).mkdir(parents=True, exist_ok=True)
    if not os.path.isdir(prefix):
        raise Exception("Prefix is not an available directory: {}".format(
                        prefix))
    generator = find_generator()

    # write configvars.py with generator, prefix, compiler values
    with open('configvars.py', 'w') as configs:
        print('GENERATOR = {}'.format(repr(generator)), file=configs)
        print('PREFIX = {}'.format(repr(prefix)), file=configs)
    if v:
        print('Created configvars.py file with values:')
        print('    GENERATOR = {}'.format(repr(generator)))
        print('    PREFIX = {}'.format(repr(prefix)))

    # write make.cmd running python make.py %*
    with open('make.cmd', 'w') as makebat:
        print('@{} make.py %*'.format(called_by), file=makebat)


if __name__ == '__main__':
    if len(sys.argv) != 1 and not sys.argv[1].startswith('-'):
        called_by = sys.argv[1]
        replacement = [sys.argv[0]]
        replacement = replacement + sys.argv[2:]
        sys.argv = replacement
    main()
