"""
Colors that you can import and make the text look pretty.

This enables you to simply add colors to any output.

Source: https://stackoverflow.com/questions/287871/print-in-terminal-with-colors
and the original source is from blender:
https://svn.blender.org/svnroot/bf-blender/trunk/blender/build_files/scons/tools/bcolors.py



"""

__author__ = 'Rob Edwards'


class bcolors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'

