# Overview

## Plugins

* [`dynamic_forecast`](dynamic_forecast.md) - Compute Recurring Transactions with Expression Evaluation Support.
* [`metadata_spray`](metadata_spray.md) - add metadata to directives using pattern matching.

## Project layout

    src/beancount_muonzoo_plugins/ # plugins
        dynamic_forecast.py        # Dynamically Compute Postings
        metadata_spray.py          # `metadata_spray` plugin
        *_test.py                  # unittests for same
    mkdocs.yml                     # The configuration file.
    docs/
        index.md                   # The documentation homepage.
        ...                        # Other markdown pages, images and other files.
