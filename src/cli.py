#!/usr/bin/env python3

import click
import sys
import os
import webbrowser
import time
import json

from . import const as c
from . import utils as u

@click.group(invoke_without_command=True)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Set stream log level to the global value.",
)
@click.option(
    "-s",
    "--silent",
    is_flag=True,
    help="No log will be outputed on sys.stdout.",
)
@click.option(
    "-l",
    "--loglevel",
    default="DEBUG",
    show_default=True,
    type=click.Choice(
        ["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG",
         "critical", "fatal", "error", "warning", "warn", "info", "debug"]
    ),
    show_choices=False,
    help="Set global log level.",
)
@click.option(
    "-c",
    "--check-availability",
    is_flag=True,
    help="Chek domain availability with GoDaddy's API"
)
@click.option(
    "-o",
    "--open-available-links",
    is_flag=True,
    help="Open avaiable domains on webbrowser."
    )
@click.option(
    "-g",
    "--grep",
    type=str,
    default=None,
    help="Grep string value on typo result"
    )
@click.option(
    "-t",
    "--testrun",
    is_flag=True,
    help="[DEBUG] Run test functions.",
)
@click.option(
    "-C",
    "--cached",
    is_flag=True,
    help="Performs a cached search that skips previously \
    processed results and saves new findings to a cache file located in the log directory."
)
@click.option(
    "--clear-cache",
    is_flag=True,
    help="Clear cache, daily use recommended, since domain ownership can variel."
)
@click.version_option("alpha", prog_name="domain finder")
def maincli(
    verbose,
    silent,
    loglevel,
    check_availability,
    open_available_links,
    grep,
    testrun,
    cached,
    clear_cache,
) -> None:
    """Steam engine for search and generation of valuables domains.\n
    [DEBUG] -t / --testrun is a debug feature for running especific functions, only use it if you know what you are doing.\n
    """

    if clear_cache:
        with open(c.CACHE_FILE, "w") as file:
            json.dump({}, file)


    c.VERBOSE = verbose
    c.LOGLEVEL = u.get_loglevl(loglevel.upper())
    c.SILENT = silent
    c.CHECK_AVAILABILITY = check_availability
    c.OPEN_AVAILABLE_LINKS = open_available_links
    c.GREP = grep
    c.CACHED = cached

    u.init_log_conf()  # set c.LOGGER

    c.LOGGER.debug(f"conf: {c.VERBOSE=} {c.LOGLEVEL=} {c.SILENT=}")


    if not testrun:   # [DEBUG] Test run block.
        return

    start = time.time()
    c.LOGGER.info(f"Initializing test.")
    print()

    # --- TEST FUNCTION GOES HERE ------------------------+
    # ----------------------------------------------------+

    print()
    c.LOGGER.info(f"Test finished in: {round(time.time() - start, 2)}s")


@maincli.command()
@click.option(
    "-l",
    "--long",
    is_flag=True,
    help="Use a long listing format"
)
def ls(long: bool) -> None:
    raise NotImplementedError


@maincli.command()
@click.argument( 
    "domain", 
    type=str, 
    required=True, 
)
@click.argument(
    "tld", 
    type=str, 
    default="com", 
    required=False, 
)
@click.option(
    "--filter",
    is_flag=False,
    default=None,
    help="Filter rarity level. --filter=A1"
)
def typo(domain: str, tld: str, filter: str | None) -> None:

    from .typo import generate_typos
    from .godaddy import godaddy_search_link

    for t in generate_typos(domain, tld, filter):
        t.update({"link": godaddy_search_link(t["domain"])})

        if c.OPEN_AVAILABLE_LINKS and t.get("available"):
            webbrowser.open(t.get("link", "http://8.8.8.8/"))

        string: str = u.format_response(t)

        if c.GREP and c.GREP not in string:
            continue

        if t.get("available") == "AVAILABLE":
            c.LOGGER.info(string)
            if not c.VERBOSE: print(string)
        else:
            c.LOGGER.debug(string)
            if not c.VERBOSE: print(string)


