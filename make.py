#!/usr/bin/env python3

# #########################################################################
#
#  2022.06.03 - First version
#
#     May you do good and not evil.
#     May you find forgiveness for yourself and forgive others.
#     May you share freely, never taking more than you give.
#
# #########################################################################
#
#  make.py -- Implement in Python3 what is unavailable on Windows (outside of
#             MinGW / Cygwin), the minimal Makefile-like behaviour of all
#             install, uninstall and a few other things. For more, see
#
#             python3 make.py help
#
# #########################################################################

import sys
import os
import os.path
import argparse
import itertools
from pathlib import Path
import shutil
import subprocess

from configvars import GENERATOR, PREFIX


CMD = 'c:\\windows\\system32\\cmd.exe'
C = '/c'
CMAKE = 'cmake'
BUILD = '--build'
PARENT = '..'
CONF = '-C'
GEN = '-G'
ARCH = '-A'


class Proc:

    def __init__(self, *args, consume=False, env=None, cwd=None):
        try:
            self.lines_ = []
            self.rc_ = None
            self.consume_ = consume
            extras = {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE,
                      'stderr': subprocess.STDOUT} if consume else {}
            if cwd:
                extras['cwd'] = cwd
            if env:
                env.update(os.environ)
                extras['env'] = env
            self.p_ = subprocess.Popen(args, **extras)
        except FileNotFoundError:
            self.p_ = None
            self.rc_ = 9009

    def rc(self):
        if self.rc_ is not None:
            return self.rc_
        if self.consume_:
            self.lines_ += self.p_.stdout.readlines()
        self.rc_ = self.p_.wait()
        return self.rc_

    def lines(self):
        if self.rc_ is None and self.consume_:
            self.lines_ += self.p_.stdout.readlines()
        return self.lines_

    def run(self):
        return self.rc()


def source_is_newer(than_file, other=None):
    if not os.path.isfile(than_file):
        return True

    # get changed-date of than_file
    than_file_stamp = os.path.getmtime(than_file)

    def newer(f):
        return os.path.getmtime(f) > than_file_stamp

    iter_these = [('configvars.py',), Path('.').rglob('CMakeLists.txt'),
                  Path('.').rglob('*[hc]')]
    if other is not None:
        iter_these.append(other)
    scan_these = itertools.chain(*iter_these)

    return any(newer(p) for p in scan_these
               if not any(str(p).startswith(deriv)
               for deriv in ['submods', 'build']))


def run_or_die(action):
    r = action()
    if r != 0:
        sys.exit(r)


def create_dirs(dirs):
    for d in dirs:
        try:
            os.mkdir(d)
        except FileExistsError as efef:
            if not os.path.isdir(d):
                return efef.args[0]
        except PermissionError as epe:
            return epe.args[0]
    return 0


def rm_f(path):
    if os.path.isdir(os.path.dirname(path)) and os.path.isfile(path):
        os.unlink(path)


class MakerDirs:

    def touch_files():
        return [os.path.join('build', 'all.touch')]

    def install_dests():
        return {"bin": os.path.join(PREFIX, "bin")}


class Maker:

    def __init__(self):
        self.build_dir_ = 'build'
        self.done_ = set()
        self.step_performed_ = False
        self.v_ = False

    def valid_order(raw_targets):
        valid = []
        if any(t == 'help' for t in raw_targets):
            return ['help']
        if any(t == 'clean' for t in raw_targets):
            valid.append('clean')
        for t in raw_targets:
            if t != 'clean':
                valid.append(t)
        if not valid:
            return ['all']
        return valid

    def make_all(self):
        create_dirs([self.build_dir_])

        if not source_is_newer('build\\all.touch'):
            self.done_.add('all')
            return

        def cmake_gen():
            if not os.path.isfile('CMakeCache.txt'):
                return Proc(CMD, C, CMAKE, PARENT, GEN,
                            GENERATOR, ARCH, 'x64',
                            cwd=self.build_dir_).run()
            return 0

        run_or_die(lambda: cmake_gen())

        def cmake_build_it():
            return lambda: Proc(CMD, C, CMAKE, BUILD, self.build_dir_,
                                '--config', 'Release', '--target',
                                'gendef').run()
        run_or_die(cmake_build_it())
        self.done_.add('all')
        self.step_performed_ = True
        with open('build\\all.touch', 'w') as f:
            print("Done!", file=f)

    def install(self):
        if 'all' not in self.done_:
            self.make_all()
        try:
            paths = MakerDirs.install_dests()
            create_dirs(paths.values())
            shutil.copy2(os.path.join('build', 'Release', 'gendef.exe'),
                         paths['bin'])
            self.step_performed_ = True
        except PermissionError as epe:
            print("{} for prefix {} must be run from an {} shell".format(
                  'make install', PREFIX, 'Admin-privilege'))
            sys.exit(epe.args[0])
        self.step_performed_ = True

    def uninstall(self):
        paths = MakerDirs.install_dests()

        try:
            rm_f(os.path.join(paths['bin'], 'gendef.exe'))
        except PermissionError as epe:
            print("{} for prefix {} must be run from an {} shell".format(
                  'make uninstall', PREFIX, 'Admin-privilege'))
            sys.exit(epe.args[0])
        self.step_performed_ = True

    def clean(self):
        def deleteThese(paths):
            for path in paths:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    rm_f(path)

        deleteThese([self.build_dir_])
        deleteThese(MakerDirs.touch_files())
        self.step_performed_ = True

    def scrub(self):
        if os.path.isdir('build'):
            Proc(CMD, C, 'rmdir', '/s', '/q', 'build').run()
        os.unlink('configvars.py')
        if os.path.isdir('__pycache__'):
            Proc(CMD, C, 'rmdir', '/s', '/q', '__pycache__').run()
        self.step_performed_ = True

    def help(self):
        print("Makefile simluator for ease-of-deployment on Windows in Win32")
        print("  * help: this message")
        print("  * all: (default target) compile of the libraries (Release)")
        print("  * install: deploy headers and libraries to prefix")
        print("  * uninstall: remove the headers and libraries at prefix")
        print("Run .\\configure.cmd before running .\\make. There are some")
        print("important settings to be determined there.")
        self.step_performed_ = True

    targets = {"all": make_all, "install": install, "uninstall": uninstall,
               "clean": clean, "scrub": scrub, "help": help}

    def process(self, args):
        self.v_ = bool(args.verbose)
        for target in Maker.valid_order(args.targets):
            assert target in Maker.targets
            Maker.targets[target](self)
        if not self.step_performed_:
            print('Nothing to do for targets, {}'.format(repr(args.targets)))


def main():
    parser = argparse.ArgumentParser(
                 description="Make script for ansak-string on Windows")
    parser.add_argument('-v', '--verbose',
                        help='more detailed progress messages',
                        action='store_true')
    targets_prompt = 'Things to build. If nothing specified, "all" '
    targets_prompt += 'is assumed. Possible values are: {}'.format(
                      str(Maker.targets.keys()))
    parser.add_argument('targets', help=targets_prompt, type=str, nargs='*')

    Maker().process(parser.parse_args())


if __name__ == '__main__':
    main()
