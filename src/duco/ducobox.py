#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools_scm import get_version

__version__ = get_version()


class DucoBox(object):
    '''Class for holding a DucoBox object'''

    def __init__(self):
        '''Initializer for a DucoBox'''
        self.nodes = []


class DucoNode(object):
    '''Class for holding a DucoBox node object'''

    def __init__(self):
        '''Initializer for a Duco Node'''
        pass


def main():
    print("Nothing yet")


if __name__ == '__main__':
    main()
