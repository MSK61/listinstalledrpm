#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
summarizes the currently installed RPM packages from the given yum log

Usage: listInstalledRPM.py LOGFILE
"""

############################################################
#
# Copyright 2009, 2010 Mohammed El-Afifi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or(at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# program:      RPM package enumerator
#
# file:         listInstalledRPM.py
#
# function:     complete program listing in this file
#
# description:  summarizes the currently installed RPM packages on the
#               system from the given yum log
#
# author:       Mohammed Safwat (MS)
#
# environment:  Kate 4.3.1, python 2.6, Fedora release 11 (Leonidas)
#               KWrite 4.3.1, python 2.6, Fedora release 11 (Leonidas)
#
# notes:        This is a private program.
#
############################################################

import logging
from logging import debug, info
import os
from re import compile
import sys
import optparse

def process_command_line(argv):
    """
    Return a 2-tuple: (settings object, args list).
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = optparse.OptionParser("%prog LOGFILE",
        formatter=optparse.TitledHelpFormatter(width=78),
        add_help_option=None)

    # define options here:
    parser.add_option(      # customized description; put --help last
        '-h', '--help', action='help',
        help='Show this help message and exit.')

    settings, args = parser.parse_args(argv)

    # check number of arguments:
    mandatoryArgs = 1
    extraArgs = len(args) - mandatoryArgs

    if extraArgs != 0:
        parser.error('program takes exactly one yum log file; ' +
                     (('"%s" ignored' % args[mandatoryArgs:]) if
                     extraArgs > 0 else "none specified") + '.')

    return settings, args

def main(argv=None):
    out_file = "rpmResult"
    args = process_command_line(argv)[1]
    logging.basicConfig(level=logging.INFO)
    run(args[0], out_file)
    return os.EX_OK        # success


def run(in_log_file, out_file):
    """Identify the installed packages from the input file.

    `in_log_file` is the yum log file to parse.
    `out_file` is the output file to dump the results into.
    The function reads in the provided yum log file and infer which
    packages are still installed after passing through the log
    operations. The results are dumped to an output file.

    """
    # some filters to identify different package operations
    op_pkg_sep = ": "  # separator between the operation and the package
    install_filter = compile("Installed" + op_pkg_sep + "(?:\d+:)?(.+?)-\d")
    erase_filter = compile("(?<=Erased" + op_pkg_sep + ").+")
    # Process the input file.
    info("Parsing input file %s...", in_log_file)
    pkg_set = set()
    with open(in_log_file) as yum_file:
        for line in yum_file:

            pkg_info = install_filter.search(line)

            if pkg_info:  # If the packages is installed, add it.

                pkg_name = pkg_info.group(1)
                debug("Found installed package %s!", pkg_name)
                pkg_set.add(pkg_name)

            else:  # If the package has been removed, exclude it.

                pkg_info = erase_filter.search(line)

                if pkg_info:

                    pkg_name = pkg_info.group()
                    debug("Found erased package %s!", pkg_name)

                    if pkg_name in pkg_set:
                        _remove_pkg(pkg_set, pkg_name)

    info("Finished reading input file %s, dumping results to file %s...",
        in_log_file, out_file)
    # Dump results.
    write_permit = 'w'
    with open(out_file, write_permit) as res_file:
        for pkg_name in pkg_set:
            res_file.write(pkg_name + os.linesep)
    info("Done!")


def _remove_pkg(pkg_set, pkg):
    """Remove the specified package from the package set.

    `pkg_set` is the package set to exclude from.
    `pkg` is the package to be excluded.

    """
    debug("Excluding package %s...", pkg)
    pkg_set.remove(pkg)


if __name__ == '__main__':
    status = main()
    sys.exit(status)
