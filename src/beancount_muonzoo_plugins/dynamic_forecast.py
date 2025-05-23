#!/usr/bin/env python3

"""Dynamic Forecast -- simple plugin to compute postings based on the account states on the date of the transaction.

This plugin tracks balances (inventories) in all accounts referenced and makes
them available in a context for evaluating postings of the transaction.

Recurring transactions are based on the earlier beancount plugin, `forecast.py`.

The plugin effectively computes a merge sort of pending recurring transactions and the existing entries.

"""

import ast
import datetime
import re
import inspect

from pprint import pformat

from beancount_muonzoo_plugins.util.parse_config_string import parse as parse_config_string

from collections import namedtuple, deque
from dateutil import rrule
from dateutil.parser import parse as dateutil_parse

from itertools import pairwise

from typing import NamedTuple, List, Set, Tuple

from beancount.core import realization
from beancount.core import getters
from beancount.core import account, amount
from beancount.parser.printer import format_entry

from beancount.core.data import (
    Entries,
    Transaction,
    Event,
)

from beancount.core.amount import Amount
from beancount.core.number import D

import logging

__flag_char = "%"
__plugin_name__ = "dynamic_forecast"
__plugins__ = (__plugin_name__,)

__bal_acc = "bal_acc_"
__event = "event_"
__expr = "expr_"

logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.DEBUG)
logger.info("TESTING")
logger.terminator = "\n\n"

LoanModelError = namedtuple("LoanModelError", "source message entry")

pf = lambda obj: pformat(
    obj, width=72, compact=False, indent=2, sort_dicts=False, underscore_numbers=True
)

# deque[Transactions]


class Config(NamedTuple):
    """Capture the config dict passed to the plugin."""

    debug: bool = False
    """ Is debugging on or not? """

    debug_level: int = None
    """ The python logging level."""

    debug_sets: Set[str] = set()
    """ A list of comma separated 'flags' that enable specific logging statements. """


def clean_ctx(ctx_dict):
    new_ctx = dict()
    for k, v in ctx_dict.items():
        # logger.debug(f'{k=} : {type(ctx[k])=}')
        if not (inspect.isfunction(v) or k.startswith("__")):
            new_ctx[k] = v if isinstance(v, str) else str(v)
    return new_ctx


def ordered_insert(iterable, item, relop):
    """
    For all `x` in `iterable`, traverse and insert `item` at the first location `relop` is false.

    - `x` : each element from `iterable` in turn.
    - `iterable` : a mutable iterable in which to insert `item`
    - `relop` a binary function that compares two elements of type of `item` and `x`.

    """
    # relop(item, x) changes to false
    i = 0
    while i < len(iterable):
        if not relop(iterable[i], item):
            break
        i += 1
    iterable.insert(i, item)


def location_string(meta):
    return "{f:s}:{l:d}".format(f=meta.get("filename", "<file>"), l=meta.get("lineno"))


def compute_amount(expr, context, meta):
    """Evaluate expr inside context"""
    tree = ast.parse(expr.strip(), mode="eval")
    co = compile(tree, location_string(meta), mode="eval")
    return eval(co, context)


def get_currency_units(inventory, currency):
    """Extract a specific commodity amount from inventory."""
    return inventory.get_currency_units(currency)


def round_to_places(amount, places):
    return Amount(amount.number.quantize(D(10) ** -places), amount.currency)


def is_metakey_expr(key):
    """True when expr_<value> or expr"""
    return (key.startswith(__expr) and len(key) > len(__expr)) or key == __expr[:-1]


def expr_varname(key):
    return key[len(__expr) :] if len(key) > len(__expr) else "expr"


def process_computed_entry(real_root, event_map, dynamic_transaction):
    logger.info(f"{dynamic_transaction.date=} {dynamic_transaction.narration=}")

    # build context for evaluation - supply add/sub/mul/div/D/R as functions

    op_ctx = dict(
        add=amount.add,
        sub=amount.sub,
        mul=amount.mul,
        div=amount.div,
        gcu=get_currency_units,
        R=round_to_places,
        D=D,
    )

    calc_ctx = dict()

    ltm = dynamic_transaction.meta
    # new_meta will get all metadata EXCEPT items that are used to evaluate the value
    # all bal_acc_ and event_ fields along with expr will be suppressed.

    new_meta = dict()

    for meta_key in ltm:
        if meta_key.startswith(__bal_acc):
            varname = meta_key[len(__bal_acc) :]
            acct = ltm[meta_key]
            real_account = realization.get(real_root, acct)

            assert real_account is not None, "Missing {}".format(acct)

            subtree_balance = realization.compute_balance(real_account, leaf_only=False)
            logger.debug(f"{subtree_balance=}")

            assert varname not in calc_ctx
            calc_ctx[varname] = subtree_balance
        elif meta_key.startswith(__event):
            varname = meta_key[len(__event) :]
            event_name = ltm[meta_key]
            assert event_name in event_map
            event_value = event_map[event_name]
            assert varname not in calc_ctx
            calc_ctx[varname] = event_value
        elif not is_metakey_expr(meta_key):
            # copy all other metadata
            new_meta[meta_key] = ltm[meta_key]

    for key in [_ for _ in ltm.keys() if is_metakey_expr(_)]:
        result = compute_amount(ltm[key], op_ctx | calc_ctx, ltm)
        varname = expr_varname(key)
        assert varname not in calc_ctx
        calc_ctx[varname] = result
        logger.debug(f"expression: {varname} ({key}) = {result}")

    # find the posting(s) with 'expr' metadata and compute result

    postings = []
    for posting in dynamic_transaction.postings:
        expr = posting.meta.get(__expr[:-1], None)
        if expr is not None:
            logger.debug(f"{posting.account=} {expr=}")
            result = compute_amount(expr, op_ctx | calc_ctx, ltm)
            logger.debug(f"{posting.account=} {result=}")
            postings.append(posting._replace(units=result))
        else:
            logger.debug(f"no metadata {posting=}")
            postings.append(posting)

    return dynamic_transaction._replace(
        meta=new_meta | clean_ctx(calc_ctx), postings=postings
    )


def update_balances(real_root, entry):
    for posting in entry.postings:
        real_account = realization.get(real_root, posting.account)

        # The account will have been created only if we're meant to track it.
        if real_account is not None:
            # Note: Always allow negative lots for the purpose of balancing.
            # This error should show up somewhere else than here.
            real_account.balance.add_position(posting)


def log_entry(prefix: str, entry, level: int = logging.DEBUG):
    for line in format_entry(entry).split("\n"):
        logger.log(level, "{prefix}: {line}".format(prefix=prefix, line=line))


def dynamic_forecast(
    entries: Entries, unused_options_map, config_string: str, *args
) -> Tuple[Entries, List[NamedTuple]]:
    """
    An example dynamic posting computation plugin that allows postings to be
    computed based on balances at a point in time.

    Args:
      entries: a list of entry instances - as per beancount
      config_string: a dict as str with the required configuration:
        debug : bool or comma-separated keys
        debug_level : logging levels
        debug_sets : a comma separated list of special debug sections

    Returns:
      A tuple of entries and errors.

    """

    # get config items to add to each loan metadata
    cdict = parse_config_string(config_string)

    debug_setting = cdict["debug"]
    if debug_setting is None:
        cdict["debug"] = False
        logger.disabled = True
    elif isinstance(debug_setting, bool):
        pass
    elif "," in debug_setting:
        cdict["debug"] = True
        cdict["debug_sets"] = set(debug_setting.split(","))

    cdict["debug_level"] = logging.getLevelName(cdict.get("debug_level", logging.INFO))

    C = Config(**cdict)

    if C.debug:
        fh = logging.FileHandler(f"{__plugin_name__}.log", mode="w")
        formatter = logging.Formatter(
            "; %(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(levelname)s - %(msg)s"
        )
        fh.setFormatter(formatter)
        fh.setLevel(C.debug_level)
        logger.addHandler(fh)

    logger.info(f"{C=}")

    # Filter out loan entries from the list of valid entries.
    through_entries = []
    pending_entries = deque()
    errors = []
    logger.debug(f"{len(entries)=}")
    real_root = realization.RealAccount("")

    # Figure out the set of accounts for which we need to compute a running
    # inventory balance.
    balance_sources = {
        entry.meta.get(metakey)
        for entry in entries
        if isinstance(entry, Transaction) and entry.flag == __flag_char
        for metakey in entry.meta
        if metakey.startswith(__bal_acc)
    }

    logger.debug(f"{balance_sources=}")
    # Add all children accounts of an asserted account to be calculated as well,
    # and pre-create these accounts, and only those (we're just being tight to
    # make sure).

    balance_match_list = [account.parent_matcher(account_) for account_ in balance_sources]

    for account_ in getters.get_accounts(entries):
        if account_ in balance_sources or any(
            match(account_) for match in balance_match_list
        ):
            realization.get_or_create(real_root, account_)

    last_date = None
    event_map = dict()

    # iterate over all the entries, update our event dict, balance tracking, etc
    # our plugin does 3 things:
    # 1. tracks events (so we can reference them)
    # 2. tracks balances for accounts marked in any of the plugin transactions
    # 3. computes the legs of the transactions by building a context dict base on the metadata
    #
    # - the first expense account type with 0 CUR as amount (CUR is returned from evaluation)
    #   receives the expr amount, the first OTHER posting with value 0 CUR gets -val as the amount
    #

    for entry in entries:
        if True:
            if last_date is None:
                last_date = entry.date

            # pending entries has a copy of the plugin transaction with the appropriate date
            # for each repetition wanted.
            #
            # TODO: consider refactoring so that it stops automatically when a balance expression
            # is true...
            while len(pending_entries) > 0 and pending_entries[0].date <= last_date:
                dynamic_transaction = pending_entries.popleft()
                assert dynamic_transaction.date <= last_date
                try:
                    txn = process_computed_entry(real_root, event_map, dynamic_transaction)
                    update_balances(real_root, txn)
                    through_entries.append(txn)
                except:  # noqa: E722
                    raise
                # TODO: add generic exception handlers (from beancount_plugin_utils)
                # except:
                #    errors.append(
                #        LoanModelError(
                #            dynamic_transaction.meta, "Computation Error:", dynamic_transaction
                #        )
                #    )

            if isinstance(entry, Event):
                # TODO: track all events running value is sufficient
                log_entry("EVENT", entry)
                event_map[entry.type] = entry.description
                through_entries.append(entry)
                continue
            elif isinstance(entry, Transaction) and entry.flag == __flag_char:
                # pull up the work from below
                match = re.search(
                    r"(^.*)\[(MONTHLY|YEARLY|WEEKLY|DAILY)"
                    r"(\s+SKIP\s+([1-9][0-9]*)\s+TIME.?)"
                    r"?(\s+REPEAT\s+([1-9][0-9]*)\s+TIME.?)"
                    r"?(\s+UNTIL\s+([0-9\-]+))?\]",
                    entry.narration,
                )
                if not match:
                    # no repetition?  just use the transaction and continue
                    through_entries.append(entry)
                    log_entry("no repetition detected -- regularizing", entry)
                    continue
                dynamic_narration = match.group(1).strip()
                dynamic_interval = (
                    rrule.YEARLY
                    if match.group(2).strip() == "YEARLY"
                    else (
                        rrule.WEEKLY
                        if match.group(2).strip() == "WEEKLY"
                        else (
                            rrule.DAILY
                            if match.group(2).strip() == "DAILY"
                            else rrule.MONTHLY
                        )
                    )
                )

                dynamic_periodicity = {"dtstart": entry.date}

                if match.group(6):  # e.g., [MONTHLY REPEAT 3 TIMES]:
                    dynamic_periodicity["count"] = int(match.group(6))
                elif match.group(8):  # e.g., [MONTHLY UNTIL 2020-01-01]:
                    dynamic_periodicity["until"] = datetime.datetime.strptime(
                        match.group(8), "%Y-%m-%d"
                    ).date()
                else:
                    # e.g., [MONTHLY]
                    dynamic_periodicity["until"] = datetime.date(
                        datetime.date.today().year, 12, 31
                    )

                if match.group(4):
                    # SKIP
                    dynamic_periodicity["interval"] = int(match.group(4)) + 1

                logger.debug(f"{dynamic_periodicity=}")

                # Generate a new entry for each loan date.
                dynamic_dates = [
                    dt.date() for dt in rrule.rrule(dynamic_interval, **dynamic_periodicity)
                ]
                logger.debug(f"{dynamic_dates=}")
                slen = len(pending_entries)
                for dynamic_date in dynamic_dates:
                    # Push these onto a queue that we merge sort from when the date increases or is seen.
                    # Keep these in  sorted order for certain. (Use some kind of sorted hash_map / ordered list).
                    dynamic_entry = entry._replace(
                        date=dynamic_date, narration=dynamic_narration
                    )
                    logger.info(f"pushing {dynamic_entry.date} {dynamic_entry.narration}")
                    # TODO: Append and compute the interest charges instead
                    # TODO: Event - track the appropriate rate.

                    ordered_insert(
                        pending_entries, dynamic_entry, lambda a, b: a.date < b.date
                    )
                assert len(pending_entries) - slen == len(dynamic_dates)
                assert all(a.date <= b.date for a, b in pairwise(pending_entries))

                logger.info(f"{len(pending_entries)=}")
                # Make sure the new entries inserted are sorted.
            else:
                if isinstance(entry, Transaction):
                    update_balances(real_root, entry)
                if "passthrough" in C.debug_sets:
                    log_entry("passthrough", entry)
                through_entries.append(entry)
            last_date = entry.date
        logger.debug(f"{len(pending_entries)=}")

    # Drain the swamp
    while len(pending_entries) > 0:
        dynamic_transaction = pending_entries.popleft()
        try:
            txn = process_computed_entry(real_root, event_map, dynamic_transaction)
            update_balances(real_root, txn)
            log_entry("processing remaining queue items", txn, level=logging.DEBUG)
            through_entries.append(txn)
        except:
            raise
            errors.append(
                LoanModelError(
                    dynamic_transaction.meta, "Computation Error: ", dynamic_transaction
                )
            )

    return (through_entries, errors)
