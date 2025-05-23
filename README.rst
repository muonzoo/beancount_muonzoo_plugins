.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/beancount_muonzoo.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/beancount_muonzoo
    .. image:: https://readthedocs.org/projects/beancount_muonzoo/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://beancount_muonzoo.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/beancount_muonzoo/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/beancount_muonzoo
    .. image:: https://img.shields.io/pypi/v/beancount_muonzoo.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/beancount_muonzoo/
    .. image:: https://img.shields.io/conda/vn/conda-forge/beancount_muonzoo.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/beancount_muonzoo
    .. image:: https://pepy.tech/badge/beancount_muonzoo/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/beancount_muonzoo
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/beancount_muonzoo

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

=================
beancount_muonzoo
=================


Amortize
--------

Split a transaction over a period of time.


Tax Reporting
-------------

Quick [plugin](beancount_muonzoo_plugins/tax_reporting/) to help break out expenses by various tax categories when
they may be multipurpose (eg home expenses that can be recovered on a tax return).

===========
Importers
===========

Simple importers for a variety of vendors etc.

This holds quick importers I've hacked together for places that I find useful.

At this point the only importer here is the Andrews & Arnold json importer.

1. [A&A Importer](AAImporter/)


## Use

The importer expects that both the PDF and JSON files are present.
It will attempt to create document directives for the PDFs from the JSON.



A longer description of your project goes here...


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.1.4. For details and usage
information on PyScaffold see https://pyscaffold.org/.
