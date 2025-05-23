"""from beangulp..."""

from decimal import Decimal
from os import path
from typing import Iterator, Sequence, Optional, Dict
import datetime
import decimal
import hashlib
import os
import re

import click
import dateutil.parser


def getmdate(filepath: str) -> datetime.date:
    """Return file modification date."""
    mtime = path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(mtime).date()


def logger(verbosity: int = 0, err: bool = False):
    """Convenient logging method factory."""
    color = False if os.getenv("TERM", "") in ("", "dumb") else None

    def log(msg, level=0, err=err, **kwargs):
        if level <= verbosity:
            click.secho(msg, color=color, err=err, **kwargs)

    return log


def walk(paths: Sequence[str]) -> Iterator[str]:
    """Yield all the files under paths.

    Takes a sequence of file or directory paths. Directories are
    traversed with os.walk() and complete file paths are returned
    joining filenames to the root directory path. Other elements of
    the list are assumed to be file paths and returned unchanged.

    Args:
      paths: List of filesystems paths.

    Yields:
      Filesystem paths of all the files under paths.

    """
    for file_or_dir in paths:
        if path.isdir(file_or_dir):
            for root, dirs, files in os.walk(file_or_dir):
                for filename in sorted(files):
                    yield path.join(root, filename)
            continue
        yield file_or_dir


def sha1sum(filepath: str) -> str:
    """Compute hash of the file at filepath."""
    with open(filepath, "rb") as fd:
        return hashlib.sha1(fd.read()).hexdigest()


def is_mimetype(filepath: str, mimetype: str) -> bool:
    return mimetype == "text/csv" and filepath.lower().endswith(".csv")


def search_file_regexp(
    filepath: str,
    *regexps: str,
    nbytes: Optional[int] = None,
    encoding: Optional[str] = None,
) -> bool:
    """Check if the header of the file matches the given regexp."""
    with open(filepath, encoding=encoding) as infile:
        # Note: Don't convert just to match on the contents.
        contents = infile.read(nbytes)
        return any(re.search(regexp, contents) for regexp in regexps)


def parse_amount(string: str) -> decimal.Decimal:
    """Convert an amount with parens and dollar sign to Decimal."""
    if string is None:
        return Decimal(0)
    string = string.strip()
    if not string:
        return Decimal(0)
    match = re.match(r"\((.*)\)", string)
    if match:
        string = match.group(1)
        sign = -1
    else:
        sign = 1
    cstring = string.strip(" $").replace(",", "")
    try:
        return Decimal(cstring) * sign
    except decimal.InvalidOperation as exc:
        raise decimal.InvalidOperation(f"Invalid conversion of {cstring!r}") from exc


def parse_date_liberally(date_string, parse_kwargs_dict=None) -> datetime.date:
    """Parse arbitrary strings to dates.

    This function is intended to support liberal inputs, so that we can use it
    in accepting user-specified dates on command-line scripts.

    Args:
      string: A string to parse.
      parse_kwargs_dict: Dict of kwargs to pass to dateutil parser.
    Returns:
      A datetime.date object.
    """
    # At the moment, rely on the most excellent dateutil.
    if parse_kwargs_dict is None:
        parse_kwargs_dict = {}
    return dateutil.parser.parse(date_string, **parse_kwargs_dict).date()


def validate_accounts(required_accounts: Dict[str, str], provided_accounts: Dict[str, str]):
    """Check a dict of provided account names against a specification of required ones.

    Args:
      required_accounts: A dict of declarations of required values.
      provided_accounts: A config dict of actual values on an importer.
    Raises:
      ValueError: If the configuration is invalid.
    """
    # Note: As an extension, we could provide the existing ledger and try to
    # validate the non-template names against the list of accounts declared in
    # it.

    provided_keys = set(provided_accounts)
    required_keys = set(required_accounts)

    for key in required_keys - provided_keys:
        raise ValueError(
            f"Missing value from user configuration: '{key}'; against {{required_keys}}"
        )

    for key in provided_keys - required_keys:
        raise ValueError(
            f"Unknown value in user configuration: '{key}'; against {required_keys}"
        )

    for account in provided_accounts.values():
        if not isinstance(account, str):
            raise ValueError(f"Invalid value for account or currency: '{account}'")
