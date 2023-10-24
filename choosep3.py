#!/usr/bin/env python3

# #########################################################################
#
#  2022.02.20 - First version
#
#     May you do good and not evil.
#     May you find forgiveness for yourself and forgive others.
#     May you share freely, never taking more than you give.
#
# #########################################################################
#
#  choosep3.py -- Checks the python version of a particular running
#                 environment and exit with that number as the error code
#
# #########################################################################

import sys

version_num_string = sys.version.split()[0]
major_version = int(version_num_string.split('.')[0])

sys.exit(major_version)
