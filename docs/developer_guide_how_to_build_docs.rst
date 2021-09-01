How to build the documentation
------------------------------


Requirements
^^^^^^^^^^^^

The documentation is built using ``sphinx``, so you need to have it:

* ``pip install sphinx sphinx-autobuild myst-parser``


First-time creation of documentation template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just once for each project, you can create the documentation template as follows:

* ``mkdir docs``
* ``cd docs``
* ``sphinx-quickstart``


Generate the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

To create the html:

* ``make html``

To create the pdf, you first need to install a latex distribution, then:

* ``make latexpdf``
