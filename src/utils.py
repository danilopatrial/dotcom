#!/usr/bin/env python3

import logging
import os
import pandas as pd
import re
import typing
import json
import time
import sys
import webbrowser

from . import const as c
from . import godaddy


def get_loglevl(loglevel_str: str) -> int:
    return {
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "WARN": logging.WARN,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }.get(loglevel_str.upper(), logging.DEBUG)


def clear_stdout() -> None:
    os.system("cls" if os.name == "nt" else "clear")


class colorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[0m",
        logging.INFO: "\033[0m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.FATAL: "\033[31m",
        logging.CRITICAL: "\033[31m",
    }
    RESET = "\033[0m"

    def format(self, record):
        log_fmt = "%(levelname)s - %(message)s"
        formatter = logging.Formatter(log_fmt)

        msg = formatter.format(record)
        color = self.COLORS.get(record.levelno, "")
        return f"{color}{msg}{self.RESET}"


def init_log_conf() -> None:
    os.makedirs("/home/apollo/Code/dotcom/log", exist_ok=True)

    c.LOGGER = logging.getLogger("main")
    c.LOGGER.setLevel(c.LOGLEVEL)

    if not c.SILENT:
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(c.LOGLEVEL if c.VERBOSE else logging.ERROR)
        stdout_handler.setFormatter(colorFormatter())
        c.LOGGER.addHandler(stdout_handler)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(
        "/home/apollo/Code/dotcom/log/main.log", mode="w"
    )
    file_handler.setLevel(c.LOGLEVEL)
    file_handler.setFormatter(formatter)
    c.LOGGER.addHandler(file_handler)


def format_response(response_dict: dict) -> str:

    if response_dict.get("error", False):
        return response_dict

    if response_dict.get("available", None) is not None:
        response_dict["available_str"] = (
            "AVAILABLE" if response_dict["available"] == True else "NOT AVAILABLE"
        )

    linke_re = r"https?:\/\/[^\s]+"
    currency_re = r"\d+(?:\.\d+)?"
    availabe_re = r"^(AVAILABLE|NOT AVAILABLE)$"
    brakets_re = r"\[([a-zA-Z0-9-]+)\]"
    domain_re = r"\b[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+\b"

    linkcolor = lambda s: f"{c.DIM}{s}{c.RESET}"
    currencycolor = lambda s: f"{c.YELLOW}{s}{c.RESET}"
    availablecolor = lambda s: (
        f"{c.GREEN}{s}{c.RESET}" if s == "AVAILABLE" else f"{c.RED}{s}{c.RESET}"
    )
    braketscolor = lambda s: f"{c.DIM}{s}{c.RESET}"
    domaincolor = lambda s: f"{c.CYAN}{s}{c.RESET}"

    link = raw_link = currency = available = brakets = domain = None
    other_args = []

    for k, v in response_dict.items():
        if not isinstance(v, str):
            v = str(v)

        if re.match(linke_re, v):
            raw_link = v
            link = linkcolor(v)
        elif re.match(currency_re, v) and v.isdigit():
            currency = f"US$ {int(v):,.2f}"
            currency = currencycolor(currency)
        elif re.match(availabe_re, v):
            available = availablecolor(v)
        elif re.match(brakets_re, v):
            brakets = braketscolor(v)
        elif re.match(domain_re, v):
            domain = domaincolor(v)
        else:
            other_args.append(f"{k}={v}")

    string: str = " - ".join(
        [a for a in (brakets, domain, available, currency, *other_args, link) if a]
    )

    return string


def stripcolors(s: str) -> str:
    """
    Remove ANSI color codes from a string for logging or plain output.
    """
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", s)


class APIRequestError(Exception): ...


# --- Cached availability, if wanted. ----------------------------+

if os.path.exists(c.CACHE_FILE):
    with open(c.CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}


def _save_cache():
    with open(c.CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def check_cached_availability(domain: str, tld: str) -> dict:
    domain = f"{domain}.{tld}"

    if c.CACHED and domain in cache:
        return cache[domain]

    result = {"domain": domain}
    if c.CHECK_AVAILABILITY:
        api_response: dict = godaddy.check_domain_availability(domain)
        if api_response.get("error", False):
            raise APIRequestError(api_response)
        result.update(api_response)
        cache[domain] = result
        if c.CACHED:
            _save_cache()
        time.sleep(1)

    return result


def final(t: dict) -> None:
    t.update({"link": godaddy.godaddy_search_link(t.get("domain", None))})

    if c.OPEN_AVAILABLE_LINKS and t.get("available"):
        webbrowser.open(t.get("link", "http://8.8.8.8/"))

    string: str = format_response(t)

    if c.GREP and c.GREP not in string:
        return

    if t.get("available") == "AVAILABLE":
        c.LOGGER.info(string)
        if not c.VERBOSE and not c.SILENT:
            print(string)
    else:
        c.LOGGER.debug(string)
        if not c.VERBOSE and not c.SILENT:
            print(string)