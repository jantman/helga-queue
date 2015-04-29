helga-queue
========================

.. image:: https://pypip.in/v/helga-queue/badge.png
   :target: https://crate.io/packages/helga-queue

.. image:: https://pypip.in/d/helga-queue/badge.png
   :target: https://crate.io/packages/helga-queue

.. image:: https://landscape.io/github/jantman/helga-queue/master/landscape.svg
   :target: https://landscape.io/github/jantman/helga-queue/master
   :alt: Code Health

.. image:: https://secure.travis-ci.org/jantman/helga-queue.png?branch=master
   :target: http://travis-ci.org/jantman/helga-queue
   :alt: travis-ci for master branch

.. image:: https://codecov.io/github/jantman/helga-queue/coverage.svg?branch=master
   :target: https://codecov.io/github/jantman/helga-queue?branch=master
   :alt: coverage report for master branch

.. image:: http://www.repostatus.org/badges/0.1.0/abandoned.svg
   :alt: Project Status: Abandoned - Initial development has started, but there has not yet been a stable, usable release; the project has been abandoned and the author(s) do not intend on continuing development.
   :target: http://www.repostatus.org/#abandoned

A simple `helga <https://github.com/shaunduncan/helga>`_ IRC bot plugin to let you manage a short queue (FIFO) of strings (eg. todo items).

**Status:** I started work on this, and then switched to using `Trello <http://trello.com>`_ for the same purpose. Some basic commands
are finished, but I don't intend on continuing work any time in the near future. Sorry.

Requirements
------------

* Python 2.6 or 2.7 (Helga requirement)
* `helga <https://github.com/shaunduncan/helga>`_ with DB configured and working.

Installation
------------

See `Installing Plugins <http://helga.readthedocs.org/en/latest/plugins.html#installing-plugins>`_ in the Helga docs.

Usage
-----

This needs to be filled in. For now, ``helga queue help``.

Bugs and Feature Requests
-------------------------

Bug reports and feature requests are happily accepted via the `GitHub Issue Tracker <https://github.com/jantman/helga-queue/issues>`_. Pull requests are
welcome. Issues that don't have an accompanying pull request will be worked on
as my time and priority allows.

Development
===========

To install for development:

1. Fork the `helga-queue <https://github.com/jantman/helga-queue>`_ repository on GitHub
2. Create a new branch off of master in your fork.

.. code-block:: bash

    $ virtualenv helga-queue
    $ cd helga-queue && source bin/activate
    $ pip install -e git+git@github.com:YOURNAME/helga-queue.git@BRANCHNAME#egg=helga-queue
    $ cd src/helga-queue

The git clone you're now in will probably be checked out to a specific commit,
so you may want to ``git checkout BRANCHNAME``.

Guidelines
----------

* pep8 compliant with some exceptions (see pytest.ini)
* 100% test coverage with pytest (with valid tests)

Testing
-------

Testing is done via `pytest <http://pytest.org/latest/>`_, driven by `tox <http://tox.testrun.org/>`_.

* testing is as simple as:

  * ``pip install tox``
  * ``tox``

* If you want to see code coverage: ``tox -e cov``

  * this produces two coverage reports - a summary on STDOUT and a full report in the ``htmlcov/`` directory

* If you want to pass additional arguments to pytest, add them to the tox command line after "--". i.e., for verbose pytext output on py27 tests: ``tox -e py27 -- -v``

Release Checklist
-----------------

1. Open an issue for the release; cut a branch off master for that issue.
2. Confirm that there are CHANGES.rst entries for all major changes.
3. Ensure that Travis tests passing in all environments.
4. Ensure that test coverage is no less than the last release (ideally, 100%).
5. Increment the version number in helga-queue/version.py and add version and release date to CHANGES.rst, then push to GitHub.
6. Confirm that README.rst renders correctly on GitHub.
7. Upload package to testpypi, confirm that README.rst renders correctly.

   * Make sure your ~/.pypirc file is correct
   * ``python setup.py register -r https://testpypi.python.org/pypi``
   * ``python setup.py sdist upload -r https://testpypi.python.org/pypi``
   * Check that the README renders at https://testpypi.python.org/pypi/helga-queue

8. Create a pull request for the release to be merge into master. Upon successful Travis build, merge it.
9. Tag the release in Git, push tag to GitHub:

   * tag the release. for now the message is quite simple: ``git tag -a vX.Y.Z -m 'X.Y.Z released YYYY-MM-DD'``
   * push the tag to GitHub: ``git push origin vX.Y.Z``

11. Upload package to live pypi:

    * ``python setup.py sdist upload``

10. make sure any GH issues fixed in the release were closed.
