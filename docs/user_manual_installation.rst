Installation
============

.. index:: requirements
.. index:: dependencies

.. role:: bash(code)
   :language: bash

Installation latest executable installer package (.exe)
----------------------------------------------------------

.. index:: QAX

.. _QAX_logo:
.. figure:: _static/qax.png
    :target: https://github.com/ausseabed/qax/releases.html
    :width: 100px
    :align: center
    :alt: QAX logo
    :figclass: align-center

    The QAX logo.

If you are on Windows, you can easily install QAX from the latest executable package installer
found `here <https://github.com/ausseabed/qax/releases>`_.

.. note::
    This is the recomended install method for anyone just wanting to use the QAX application

Create your own environment and run QAX from source
-----------------------------------------------------
There are 3 steps

#. Create conda environment and install the necessary dependencies needed to run QAX
#. Clone (or download) code repositories for QAX plugins and other dependencies
#. Install and run QAX

Create conda environment for QAX
******************************************************
Start by installing `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ (on Windows) and installing necessary dependencies (NumPy, GDAL, hyo2.abc, hyo2.mate) and  QAX itself.
The following command sequence is suggested: ::

    conda create -y -n qax python=3.10
    conda activate qax
    
    conda install -y -c conda-forge certifi
    conda install -y -c conda-forge --file requirements_conda.txt
    conda install -y -c conda-forge --no-deps cartopy
    conda install -y -c conda-forge --no-deps pyproj=3.4.0

    pip install -r requirements.txt

If running on Windows the following package needs to be installed::

    pip install pypiwin32


Clone (or download) code repositories for QAX plugins
*******************************************************

Clone (or download) each of the following repositories:

* https://github.com/ausseabed/qajson
* https://github.com/ausseabed/pyall
* https://github.com/ausseabed/pygsf
* https://github.com/ausseabed/mate
* https://github.com/ausseabed/mbes-grid-checks
* https://github.com/ausseabed/finder-grid-checks
* https://github.com/hydroffice/hyo2_abc
* https://github.com/ausseabed/kmall

Note: It is recomended that each of these repositories be stored at the same
directory structure level as the qax repository.


Install each of the cloned repositories into the `qax` environment. Use the
`-e` argument to have these installed in an editable mode as this better supports
development workflows::

    cd qajson
    pip install -e .
    cd ..

    cd pyall
    pip install .
    cd ..

    cd pygsf
    pip install .
    cd ..

    cd mate
    pip install -e .
    cd ..

    cd mbes-grid-checks
    pip install -e .
    cd ..

    cd finder-grid-checks
    pip install -e .
    cd ..

    cd hyo2_abc
    pip install .
    cd ..

    cd kmall
    pip install .
    cd ..

Install and run QAX
*********************

Install the qax package::

    cd qax
    pip install -e .

QAX can then be run with the following command::

    python hyo2\qax\app\__main__.py



Build your own executable from source
-----------------------------------------
There are 3 steps

#. Follow the above process to create QAX environment
#. Use `pyinstaller` to generate a redistributable directory of the dependencies included in the conda env
#. Use Inno Setup to build an msi install file from the redistributable directory contents

::


Install pyinstaller
*********************

    pip install pyinstaller

Use `pyinstaller` to generate a redistributable directory of the dependencies included in the conda env
**********************************************************************************************************
Run the spec file from this directory.

::

    pyinstaller install/cli.spec

This will produce a `dist` and `build` directory. The dist directory is the 'redistributable directory'.

Use Inno Setup to build an msi install file from the redistributable directory contents
*****************************************************************************************
Run the iss file from this directory.

::

    "c:\Program Files (x86)\Inno Setup 6\ISCC.exe" qax.iss

This will produce an `Output` directory containing a single setup file.
