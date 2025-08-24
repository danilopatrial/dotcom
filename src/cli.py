#!/usr/bin/env python3

import click
import sys
import os
import webbrowser
import time
import json

from . import const as c
from . import utils as u
from . import godaddy


@click.group(invoke_without_command=True)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose mode. Sets the stream log level to the global log level.",
)
@click.option(
    "-s",
    "--silent",
    is_flag=True,
    help="Suppress all log output to stdout."
    )
@click.option(
    "-l",
    "--loglevel",
    default="DEBUG",
    show_default=True,
    type=click.Choice(
        [
            "CRITICAL",
            "FATAL",
            "ERROR",
            "WARNING",
            "WARN",
            "INFO",
            "DEBUG",
            "critical",
            "fatal",
            "error",
            "warning",
            "warn",
            "info",
            "debug",
        ]
    ),
    show_choices=False,
    help="Set the global log level.",
)
@click.option(
    "-c",
    "--check-availability",
    is_flag=True,
    help="Check domain availability using GoDaddy's API.",
)
@click.option(
    "-o",
    "--open-available-links",
    is_flag=True,
    help="Automatically open available domains in the default web browser.",
)
@click.option(
    "-g",
    "--grep",
    type=str,
    default=None,
    help="Filter typo results by a specific substring.",
)
@click.option(
    "-C",
    "--cached",
    is_flag=True,
    help="Enable cached mode: skips domains previously checked and stores new results in a cache file located in the log directory.",
)
@click.option(
    "--clear-cache",
    is_flag=True,
    help="Clear the local cache. Recommended for daily use since domain availability can change frequently.",
)
@click.option(
    "-t", "--testrun", is_flag=True, help="[DEBUG] Run internal test functions."
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
            json.dump({}, file, indent=4)

    c.VERBOSE = verbose
    c.LOGLEVEL = u.get_loglevl(loglevel)
    c.SILENT = silent
    c.CHECK_AVAILABILITY = check_availability
    c.OPEN_AVAILABLE_LINKS = open_available_links
    c.GREP = grep
    c.CACHED = cached

    u.init_log_conf()  # set c.LOGGER

    c.LOGGER.debug(
        f"conf: {c.VERBOSE=} {c.LOGLEVEL=} {c.SILENT=} {c.CHECK_AVAILABILITY=} {c.OPEN_AVAILABLE_LINKS=} {c.GREP} {c.CACHED}"
    )

    if not testrun:  # [DEBUG] Test run block.
        return

    start = time.time()
    c.LOGGER.info(f"Initializing test.")
    if not c.SILENT: print()

    # --- TEST FUNCTION GOES HERE ------------------------+
    # ----------------------------------------------------+

    if not c.SILENT: print()
    c.LOGGER.info(f"Test finished in: {round(time.time() - start, 2)}s")


@maincli.command(name="ls-domains")
@click.option("-l", "--long", is_flag=True, help="Use a long listing format")
def ls(long: bool) -> None:
    """List information about registered domains.
    Sort entries alphabetically if --sort is not specified."""
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
    "--filter", is_flag=False, default=None, help="Filter rarity level. --filter=A1"
)
def typo(domain: str, tld: str, filter: str | None) -> None:
    """Generate possible typos for a given domain."""

    from .typo import generate_typos
    from .godaddy import godaddy_search_link

    for t in generate_typos(domain, tld, filter):
        u.final(t)


@maincli.command()
@click.option(
    "--file",
    "file_path",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a file containing domain names."
)
@click.argument("names", nargs=-1)
@click.option(
    "--tld",
    default="com",
    type=str,
    show_default=True,
    help="Domain TLD, exclusive dot. --tld=me"
)
def run(file_path: str | None, names: tuple[str], tld: str) -> None:
    """Run through domain set list."""
    if file_path:
        click.echo(f"Reading domains from file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        if not names:
            click.echo("Error: You must provide either --file or names.", err=True)
            raise click.Abort()
        domains = list(names)

    for domain in domains:
        result: dict = {"domain": f"{domain}.{tld}"}
        result.update(u.check_cached_availability(domain, tld))
        u.final(result)