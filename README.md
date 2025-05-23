TODO: decide unittest or pytest
TODO: fix up tests.
TODO: remove unused code

# Plugins for Beancount

## Tax Reporting

Quick [plugin](beancount_muonzoo_plugins/tax_reporting/) to help break out expenses by various tax categories when
they may be multipurpose (eg home expenses that can be recovered on a tax return).

# Importers

Simple importers for a variety of vendors etc.

This holds quick importers I've hacked together for places that I find useful.

At this point the only importer here is the Andrews & Arnold json importer.

1. [A&A Importer](AAImporter/)


## Use

The importer expects that both the PDF and JSON files are present.
It will attempt to create document directives for the PDFs from the JSON.

## Installation

`pip install beancount-muonzoo-importers`

## Running

1. Add to the list of installed importers in your import config
1. Check using `bean-identify` that the json files are noticed.


# TODO

## GSU Importer

Appears pretty broken - not generating the vesting transaction but needs comparison to historic records and
add some accounting of the taxes and recording them properly.

Likely makes sense to just make new GSU importers by clonging this and date-range limiting them in the 'claim' functionality.
Hacky but it will work. They are all going away when v3 ships anyway.

