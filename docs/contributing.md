# Contributing

> quotes might be useful
> but I'm not sure why

This is a collection of loosely related
[`beancount`](https://furius.ca/beancount) plugins that I have pulled together
based on a variety of community sources and inspiration. While I've tried to
credit where due; it may be incomplete. If you find something that needs
correction, please let me know with an issue on the [issue
tracker](https://github.com/muonzoo/beancount_muonzoo_plugins/issues).

## About

This document provides a set of best practices for open source contributions -
bug reports, code submissions / pull requests, etc.

This document is a derivation of [contribution-guide.org](https://contribution-guide.org)'s [guideline document](https://github.com/bitprophet/contribution-guide.org/blob/main/index.rst)
which is itself open source. Feedback & suggestions for improvement are welcome.

---- 

## Submitting bugs

### Due diligence

Before submitting a bug, please do the following:

* Perform **basic troubleshooting** steps:

    * **Make sure you're on the latest version.** If you're not on the most
      recent version, your problem may have been solved already! Upgrading is
      always the best first step.
    * **Try older versions.** If you're already *on* the latest release, try
      rolling back a few minor versions (e.g. if on 1.7, try 1.5 or 1.6) and
      see if the problem goes away. This will help the devs narrow down when
      the problem first arose in the commit log.
    * **Try switching up dependency versions.** If the software in question has
      dependencies (other libraries, etc) try upgrading/downgrading those as
      well.

* **Search the [issue
  tracker](https://github.com/muonzoo/beancount_muonzoo_plugins/issues)** to
  make sure it's not a known issue.
* If you find a pre-existing issue, review the conversation and consider adding
  additional context, test cases or platform information that would help with
  resolution of the issue. eg) everyone has reported and issue on MacOS but
  you're also experiencing it on Linux.

## What to put in your bug report

Make sure your report gets the attention it deserves: bug reports with missing
information may be ignored or punted back to you, delaying a fix. The below
constitutes a bare minimum; more info is almost always better:

* **What operating system are you on?** Windows? (10? 11? is it 64-bit?)
  macOS? (Catalina/10.15? Ventura/13.6? Intel or ARM/Apple Silicon?) Linux?
  (Which distro? Which version *of* that distro?) Again, more detail is better.
* **What version of the core programming language interpreter/compiler are you
  using?** For example, if it's a Python project, are you using (C)Python
  3.7.10? PyPy 3.10?
* **Which version or versions of the software are you using?** Ideally, you
  followed the advice above and have ruled out (or verified that the problem
  exists in) a few different versions.
* **How did you install the runtime and software?** Operating system packages?
  pyenv? from source? Something like Conda, or a virtualenv?
* **How can the developers recreate the bug on their end?** If possible,
  include a copy of your code, the command you used to invoke it, and the full
  output of your run (if applicable.)

    * A common tactic is to pare down your code until a simple (but still
      bug-causing) "base case" remains. Not only can this help you identify
      problems which aren't real bugs, but it means the developer can get to
      fixing the bug faster.

## Contributing changes


### Licensing of contributed material

> Your contribution will be licensed as the rest of the project.

Keep in mind as you contribute, that code, docs and other material submitted to
open source projects are usually considered licensed under the same terms
as the rest of the work.

The details vary from project to project, but from the perspective of this
document's authors:

- Anything submitted to a project falls under the licensing terms in the
  repository's top level ``LICENSE`` file.

    - For example, if a project's ``LICENSE`` is BSD-based, contributors should
      be comfortable with their work potentially being distributed in binary
      form without the original source code.

- Per-file copyright/license headers are typically extraneous and undesirable.
  Please don't add your own copyright headers to new files unless the project's
  license actually requires them!

    - Not least because even a new file created by one individual (who often
      feels compelled to put their personal copyright notice at the top) will
      inherently end up contributed to by dozens of others over time, making a
      per-file header outdated/misleading.

### Version control branching

> One branch, one change.

* Always **make a new branch** for your work, no matter how small. This makes
  it easy for others to take just that one set of changes from your repository,
  in case you have multiple unrelated changes floating around.

    * A corollary: **don't submit unrelated changes in the same branch/pull
      request**! The maintainer shouldn't have to reject your awesome bugfix
      because the feature you put in with it needs more review.

* **Base your new branch off of the appropriate branch** on the main
  repository:

    * **Bug fixes** should be based on the branch named after the **oldest
      supported release line** the bug affects.

        * E.g. if a feature was introduced in 1.1, the latest release line is
          1.3, and a bug is found in that feature - make your branch based on
          1.1.  The maintainer will then forward-port it to 1.3 and main.
        * Bug fixes requiring large changes to the code or which have a chance
          of being otherwise disruptive, may need to base off of **main**
          instead. This is a judgement call -- ask the devs!

    * **New features** should branch off of **the 'main' branch**.

        * Note that depending on how long it takes for the dev team to merge
          your patch, the copy of ``main`` you worked off of may get out of
          date! If you find yourself 'bumping' a pull request that's been
          sidelined for a while, **make sure you rebase or merge to latest
          main** to ensure a speedier resolution.

## Code formatting

> TL;DR -  We use `ruff format` as configured in [`pyproject.toml`](https://github.com/muonzoo/beancount_muonzoo_plugins/pyproject.toml).

* **Follow the style you see used in the primary repository**! Consistency with
  the rest of the project always trumps other considerations. It doesn't matter
  if you have your own style or if the rest of the code breaks with the greater
  community - just follow along.
* Python projects usually follow the `PEP-8
  <http://www.python.org/dev/peps/pep-0008/>`_ guidelines (though many have
  minor deviations depending on the lead maintainers' preferences.)

Documentation isn't optional
----------------------------

It's not! Patches without documentation will be returned to sender.  By
"documentation" we mean:

* **Docstrings** (for Python; or API-doc-friendly comments for other languages)
  must be created or updated for public API functions/methods/etc. (This step
  is optional for some bugfixes.)

    * Don't forget to include `versionadded
      <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionadded>`_/`versionchanged
      <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionchanged>`_ ReST
      directives at the bottom of any new or changed Python docstrings!

        * Use ``versionadded`` for truly new API members -- new methods,
          functions, classes or modules.
        * Use ``versionchanged`` when adding/removing new function/method
          arguments, or whenever behavior changes.

* New features should ideally include updates to **prose documentation**,
  including useful example code snippets.
* All submissions should have a **changelog entry** crediting the contributor
  and/or any individuals instrumental in identifying the problem.

Tests aren't optional
---------------------

Any bugfix that doesn't include a test proving the existence of the bug being
fixed, may be suspect.  Ditto for new features that can't prove they actually
work.

We've found that test-first development really helps make features better
architected and identifies potential edge cases earlier instead of later.
Writing tests before the implementation is strongly encouraged.

Full example
------------

Here's an example workflow for a project ``theproject`` hosted on Github, which
is currently in version 1.3.x. Your username is ``yourname`` and you're
submitting a basic bugfix. (This workflow only changes slightly if the project
is hosted at Bitbucket, self-hosted, or etc.)

Preparing your Fork
^^^^^^^^^^^^^^^^^^^

1. Click 'Fork' on Github, creating e.g. ``yourname/theproject``.
2. Clone your project: ``git clone git@github.com:yourname/theproject``.
3. ``cd theproject``
4. `Create and activate a virtual environment <https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments>`_.
5. Install the development requirements: ``pip install -r dev-requirements.txt``.
6. Create a branch: ``git checkout -b foo-the-bars 1.3``.

Making your Changes
^^^^^^^^^^^^^^^^^^^

1. Add changelog entry crediting yourself.
2. Write tests expecting the correct/fixed functionality; make sure they fail.
3. Hack, hack, hack.
4. Run tests again, making sure they pass.
5. Commit your changes: ``git commit -m "Foo the bars"``

Creating Pull Requests
^^^^^^^^^^^^^^^^^^^^^^

1. Push your commit to get it back up to your fork: ``git push origin HEAD``
2. Visit Github, click handy "Pull request" button that it will make upon
   noticing your new branch.
3. In the description field, write down issue number (if submitting code fixing
   an existing issue) or describe the issue + your fix (if submitting a wholly
   new bugfix).
4. Hit 'submit'! And please be patient - the maintainers will get to you when
   they can.
