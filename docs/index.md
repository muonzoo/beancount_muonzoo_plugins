# Overview

## Plugins

* `loan_model` - Compute Recurring Transactions with Expression Evaluation Support.
* `metadata_spray` - add metadata to directives using pattern matching.

## Project layout

    src/beancount_muonzoo_plugins/ # plugins
        loan_model.py              # `loan_model`
        metadata_spray.py          # `metadata_spray` plugin
        *_test.py                  # unittests for same
    mkdocs.yml                     # The configuration file.
    docs/
        index.md                   # The documentation homepage.
        ...                        # Other markdown pages, images and other files.
