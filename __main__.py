#!/usr/bin/env python3

from sys import version_info
from .src.cli import maincli

if __name__ == "__main__" and version_info >= (3, 9):
    maincli()