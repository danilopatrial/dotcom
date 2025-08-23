#!/usr/bin/env python3

from __future__ import annotations

import pandas as pd
import sys
import logging
import glob
import os
import shutil
import datetime
import re
import typing
import time
import webbrowser
import itertools
import json
import string

from pathlib import Path
from datetime import datetime

from . import const as c
from . import utils as u
from . import godaddy


"https://medium.com/@georg.vetter.privat/how-to-build-a-typo-generator-from-scratch-in-python-ace485aac18b"


def _swap_letters(word: str) -> list[str]:
    "swap every letter of a word pairwise. Example: Word, oWrd, Wrod, Wodr"

    swap_list = []
    for idx, letter in enumerate(word):
        swap_list.append(word[:idx] + word[idx + 1] + word[idx] + word[idx + 2 :])
        if idx + 2 == len(word):
            break
    return swap_list


def _double_letter(word: str) -> list[str]:
    "double every letter in the word: Example: WWord, Woord, Worrd, Wordd"

    double_letter_list = []
    for idx, letter in enumerate(word):
        double_letter_list.append(word[:idx] + letter + word[idx:])
    return double_letter_list


def _one_out(word: str) -> list[str]:
    "Remove on every possible position one letter from the input word. Example: ord, Wrd, Wod, Wor"

    one_out = []
    for idx in range(len(word)):
        one_out.append(word[:idx] + word[idx + 1 :])
    return one_out


def _replace_with_neighbor(word: str, neighbors: dict) -> list[str]:
    "replace every letter in the word with every possible neighbor on a german keyboard"

    neighbor_replaced_words = []
    for idx, letter in enumerate(word):
        for neighbor in neighbors.get(letter.lower(), letter):
            neighbor_replaced_words.append(word[:idx] + neighbor + word[idx + 1 :])

    return neighbor_replaced_words


def _b4_after_with_neighbor(word: str, neighbors: dict) -> list[str]:
    "place before and after every letter in the word every possible neighbor on a german keyboard"

    neighbor_replaced_words = []
    for idx, letter in enumerate(word):
        for neighbor in neighbors.get(letter.lower(), letter):
            neighbor_replaced_words.append(word[:idx] + neighbor + word[idx:])
            neighbor_replaced_words.append(word[: idx + 1] + neighbor + word[idx + 1 :])

    return neighbor_replaced_words


# --- Cached availability, if wanted. ----------------------------+

if os.path.exists(c.CACHE_FILE):
    with open(c.CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}


def save_cache():
    with open(c.CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def _check_cached_availability(typo: str, tld: str) -> dict:
    domain = f"{typo}.{tld}"

    if c.CACHED and domain in cache:
        return cache[domain]

    result = {}
    if c.CHECK_AVAILABILITY:
        api_response: dict = godaddy.check_domain_availability(domain)
        if api_response.get("error", False):
            raise u.APIRequestError(api_response)
        result.update(api_response)
        cache[domain] = result
        if c.CACHED:
            save_cache()
        time.sleep(1)

    return result


def generate_typos(domain: str, tld: str, filter: str | None) -> typing.Iterator[dict]:
    domain = domain.lower()

    typo_groups = {
        "A1": (_replace_with_neighbor, {"neighbors": c.NEIGHBORINGLETTERS}),
        "A2": (_replace_with_neighbor, {"neighbors": c.NEIGHBORINGNUMPADDIGITS}),
        "B1": (_one_out, {}),
        "B2": (_swap_letters, {}),
        "B3": (_double_letter, {}),
        "C1": (_replace_with_neighbor, {"neighbors": c.VISUALLYSIMILARCHARS}),
        "C2": (_replace_with_neighbor, {"neighbors": c.VISUALLYSIMILARDIGITS}),
        "D1": (_b4_after_with_neighbor, {"neighbors": c.NEIGHBORINGLETTERS}),
        "D2": (_b4_after_with_neighbor, {"neighbors": c.NEIGHBORINGNUMPADDIGITS}),
    }

    filter = filter.upper() if filter else None

    for key, (func, kwargs) in typo_groups.items():
        group = key[0]  # A, B, C, D
        if filter is None or filter == group or filter == key:
            for typo in func(domain, **kwargs):
                result = _check_cached_availability(typo, tld)
                result.update({"freq": f"[{key}]"})
                yield result
