#!/usr/bin/env python3

import logging
import pandas as pd
import dotenv
import os

# --- ENV ----------------------------------------------------------------------------------------+

dotenv.load_dotenv(dotenv_path="/home/apollo/Code/domain/.venv/.env")

GODADDY_API_KEY: str = os.getenv("GODADDY_API_KEY", default=None)
GODADDY_API_SECRET: str = os.getenv("GODADDY_API_SECRET", default=None)

OTE_GODADDY_API_KEY: str = os.getenv("OTE_GODADDY_API_KEY", default=None)
OTE_GODADDY_API_SECRET: str = os.getenv("OTE_GODADDY_API_SECRET", default=None)


# --- Global -------------------------------------------------------------------------------------+

VERBOSE: bool               # set logging stream level to global logging level, else logging.FATAL.
LOGLEVEL: int               # global logging level - applies for all streams.
SILENT: bool                # set logging stream to None. No output on sys.stdout.
CHECK_AVAILABILITY: bool    # If search for a domain, and True, will check its availability.
OPEN_AVAILABLE_LINKS: bool  # Open available domains on webbrowser.
GREP: str | None            # Grep search of stdout result.

GREP_FOUND: bool | None = None

LOGGER: logging.Logger      # main logger object

DATAFRAME: pd.DataFrame

# --- Paths --------------------------------------------------------------------------------------+

DOWNLOADS_DIR: str = "/home/apollo/Downloads"
DOTDATA_DIR: str = "/home/apollo/Code/domain/.data"
CACHE_FILE: str = "/home/apollo/Code/dotcom/log/.cache.json"

# --- Key Board Map for the Typos Generator ------------------------------------------------------+

NEIGHBORINGLETTERS: dict = {
    'a': ['q', 'w', 's', 'z'],
    'b': ['v', 'g', 'h', 'n'],
    'c': ['x', 'd', 'f', 'v'],
    'd': ['s', 'e', 'r', 'f', 'c', 'x'],
    'e': ['r', 'd', 's', 'w'],
    'f': ['d', 'r', 't', 'g', 'v', 'c'],
    'g': ['f', 't', 'y', 'h', 'b', 'v'],
    'h': ['n', 'b', 'g', 'y', 'u', 'j'],
    'i': ['o', 'k', 'j', 'u'],
    'j': ['h', 'u', 'i', 'k', 'm', 'n'],
    'k': ['j', 'i', 'o', 'l', 'm'],
    'l': ['k', 'o', 'p'],
    'm': ['n', 'j', 'k'],
    'n': ['b', 'h', 'j', 'm'],
    'o': ['i', 'k', 'l', 'p'],
    'p': ['o', 'l'],
    'q': ['a', 'w'],
    'r': ['e', 'd', 'f', 't'],
    's': ['a', 'z', 'x', 'd', 'e', 'w'],
    't': ['r', 'f', 'g', 'y'],
    'u': ['y', 'h', 'j', 'i'],
    'v': ['c', 'f', 'g', 'b'],
    'w': ['q', 'a', 's', 'd', 'e'],
    'x': ['z', 's', 'd', 'c'],
    'y': ['t', 'g', 'h', 'u'],
    'z': ['a', 's', 'x'],
}

NEIGHBORINGNUMPADDIGITS: dict = {
    '0': ['1', '2'],
    '1': ['4', '5', '2', '0'],
    '2': ['0', '1', '4', '5', '6', '3'],
    '3': ['2', '5', '6'],
    '4': ['7', '8', '5', '2', '1'],
    '5': ['7', '8', '9', '4', '6', '1', '2', '3'],
    '6': ['9', '8', '5', '2', '3'],
    '7': ['8', '5', '4'],
    '8': ['7', '4', '5', '6', '9'],
    '9': ['8', '5', '6']
}

VISUALLYSIMILARDIGITS: dict = {
    '0': ['6', '8', '9'],
    '1': ['7'],
    '2': ['7'],
    '3': ['5', '8', '9'],
    '4': ['9'],
    '5': ['3', '8'],
    '6': ['0', '8'],
    '7': ['1', '2'],
    '8': ['0', '3', '5', '6'],
    '9': ['0', '3', '4']
}

VISUALLYSIMILARCHARS: dict = {
    '0': ['6', '8', '9', 'o', 'D', 'O', 'U'],
    '1': ['7', 'I'],
    '2': ['7', 'Q', 'Z'],
    '3': ['5', '8', '9'],
    '4': ['9', 'U'],
    '5': ['3', '8', 'S'],
    '6': ['0', '8', 'b', 'G'],
    '7': ['1', '2', 'T', 'Z'],
    '8': ['0', '3', '5', '6', 'B', 'S'],
    '9': ['0', '3', '4', 'g', 'q'],
    'b': ['6'],
    'c': ['e'],
    'e': ['c'],
    'g': ['9', 'q'],
    'i': ['I'],
    'm': ['n'],
    'n': ['m', 'p'],
    'o': ['0'],
    'p': ['n'],
    'q': ['9', 'g'],
    'u': ['v'],
    'v': ['u'],
    'y': ['z'],
    'z': ['y'],
    'B': ['8', 'P'],
    'C': ['G'],
    'D': ['0', 'O'],
    'E': ['F'],
    'F': ['7', 'E', 'R'],
    'G': ['6', 'C'],
    'I': ['1', 'i', 'L', 'T'],
    'L': ['I'],
    'M': ['N'],
    'N': ['M'],
    'O': ['0', 'D', 'U'],
    'P': ['B'],
    'Q': ['2'],
    'S': ['5', '8'],
    'T': ['I', '7'],
    'U': ['0', '4', 'O', 'V'],
    'V': ['U', 'W'],
    'W': ['U'],
    'X': ['Y'],
    'Y': ['5', 'X'],
    'Z': ['2', '7']
}

# --- Terminal Colors ----------------------------------------------------------------------------+
# Reset
RESET: str = "\033[0m"

# Styles
BOLD: str = "\033[1m"
DIM: str = "\033[2m"
UNDERLINED: str = "\033[4m"
BLINK: str = "\033[5m"
REVERSE: str = "\033[7m"
HIDDEN: str = "\033[8m"

# Foreground / Text Colors
BLACK: str = "\033[30m"
RED: str = "\033[31m"
GREEN: str = "\033[32m"
YELLOW: str = "\033[33m"
BLUE: str = "\033[34m"
MAGENTA: str = "\033[35m"
CYAN: str = "\033[36m"
WHITE: str = "\033[37m"

# Bright Foreground Colors
BRIGHT_BLACK: str = "\033[90m"
BRIGHT_RED: str = "\033[91m"
BRIGHT_GREEN: str = "\033[92m"
BRIGHT_YELLOW: str = "\033[93m"
BRIGHT_BLUE: str = "\033[94m"
BRIGHT_MAGENTA: str = "\033[95m"
BRIGHT_CYAN: str = "\033[96m"
BRIGHT_WHITE: str = "\033[97m"

# Background Colors
BG_BLACK: str = "\033[40m"
BG_RED: str = "\033[41m"
BG_GREEN: str = "\033[42m"
BG_YELLOW: str = "\033[43m"
BG_BLUE: str = "\033[44m"
BG_MAGENTA: str = "\033[45m"
BG_CYAN: str = "\033[46m"
BG_WHITE: str = "\033[47m"

# Bright Background Colors
BG_BRIGHT_BLACK: str = "\033[100m"
BG_BRIGHT_RED: str = "\033[101m"
BG_BRIGHT_GREEN: str = "\033[102m"
BG_BRIGHT_YELLOW: str = "\033[103m"
BG_BRIGHT_BLUE: str = "\033[104m"
BG_BRIGHT_MAGENTA: str = "\033[105m"
BG_BRIGHT_CYAN: str = "\033[106m"
BG_BRIGHT_WHITE: str = "\033[107m"

__all__: list = [var for var in globals().keys() if not var.startswith("_")]