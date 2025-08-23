#!/usr/bin/env python3

import logging
import os
import pandas as pd
import re
import typing
import sys

from . import const as _c


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


class _ColorFormatter(logging.Formatter):
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

    _c.LOGGER = logging.getLogger("main")
    _c.LOGGER.setLevel(_c.LOGLEVEL)

    if not _c.SILENT:
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(_c.LOGLEVEL if _c.VERBOSE else logging.ERROR)
        stdout_handler.setFormatter(_ColorFormatter())
        _c.LOGGER.addHandler(stdout_handler)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(
        "/home/apollo/Code/dotcom/log/main.log", mode="w"
    )
    file_handler.setLevel(_c.LOGLEVEL)
    file_handler.setFormatter(formatter)
    _c.LOGGER.addHandler(file_handler)


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

    link_color = lambda s: f"{_c.DIM}{s}{_c.RESET}"
    currency_color = lambda s: f"{_c.YELLOW}{s}{_c.RESET}"
    available_color = lambda s: (
        f"{_c.GREEN}{s}{_c.RESET}" if s == "AVAILABLE" else f"{_c.RED}{s}{_c.RESET}"
    )
    brakets_color = lambda s: f"{_c.DIM}{s}{_c.RESET}"
    domain_color = lambda s: f"{_c.CYAN}{s}{_c.RESET}"

    link = raw_link = currency = AVAILABLE = brakets = domain = None
    other_args = []

    for k, v in response_dict.items():
        if not isinstance(v, str):
            v = str(v)

        if re.match(linke_re, v):
            raw_link = v
            link = link_color(v)
        elif re.match(currency_re, v) and v.isdigit():
            currency = f"US$ {int(v):,.2f}"
            currency = currency_color(currency)
        elif re.match(availabe_re, v):
            available = available_color(v)
        elif re.match(brakets_re, v):
            brakets = brakets_color(v)
        elif re.match(domain_re, v):
            domain = domain_color(v)
        else:
            other_args.append(f"{k}={v}")

    string: str = " - ".join(
        [a for a in (brakets, domain, available, currency, *other_args, link) if a]
    )

    return string


def strip_colors(s: str) -> str:
    """
    Remove ANSI color codes from a string for logging or plain output.
    """
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", s)


class APIRequestError(Exception): ...
