.. _how-to-contribute-label:

How to contribute
-----------------

.. index::
    single: open source
    single: contribution
    single: code of conduct
    single: PEP; 8
    single: PEP; 257
    single: documentation
    single: compatibility
    single: history

Every open source project lives from the generous help by contributors that sacrifice their time and this is no different.

To make participation as pleasant as possible, this project adheres to the `Code of Conduct`_ by the Python Software Foundation.

Here are a few hints and rules to get you started:

- Add yourself to the AUTHORS.txt_ file in an alphabetical fashion. Every contribution is valuable and shall be credited.
- If your change is noteworthy, add an entry to the changelog_.
- No contribution is too small; please submit as many fixes for typos and grammar bloopers as you can!
- Don't *ever* break backward compatibility.
- *Always* add tests and docs for your code. This is a hard rule; patches with missing tests or documentation won't be merged.
  If a feature is not tested or documented, it does not exist.
- Obey `PEP 8`_ and `PEP 257`_.
- Write `good commit messages`_.
- Ideally, `collapse`_ your commits, i.e. make your pull requests just one commit.

.. note::
   If you have something great but aren't sure whether it adheres -- or even can adhere -- to the rules above: **please submit a pull request anyway**!
   In the best case, we can mold it into something, in the worst case the pull request gets politely closed.
   There's absolutely nothing to fear.

Thank you for considering to contribute! If you have any question or concerns, feel free to reach out to us (see :ref:`credits-label`).

.. _`Code of Conduct`: http://www.python.org/psf/codeofconduct/
.. _AUTHORS.txt: https://github.com/hydroffice/hyo_qax/raw/master/AUTHORS.rst
.. _changelog: https://github.com/hydroffice/hyo_qax/raw/master/HISTORY.rst
.. _`PEP 8`: http://www.python.org/dev/peps/pep-0008/
.. _`PEP 257`: http://www.python.org/dev/peps/pep-0257/
.. _collapse: https://www.mercurial-scm.org/wiki/RebaseExtension
.. _`good commit messages`: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
