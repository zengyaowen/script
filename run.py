#!/usr/bin/python
# encoding: utf-8

import sys
import getopt

def Usage():
    print 'check balance run script usage:'
    print '-e, --enviroment: set run script enviroment,such as daily, prepub, publish'

for arg in sys.argv:
    print(arg)
print(sys.argv)
print(sys.argv[1])
