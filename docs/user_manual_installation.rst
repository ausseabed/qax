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
Start by installing `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ (on Windows) and and then establishing an environment to install necessary dependencies (eg NumPy, GDAL, hyo2.mate) via the `conda-environment.yaml` file, followed by  QAX itself.
The following command sequence is suggested: ::

    conda create -y -n qax python=3.11
    conda env update --file conda-environment.yaml
    conda activate qax

Install and run QAX
*********************

Install the qax package::

    cd qax
    pip install .

QAX can then be run with the following command::

    python hyo2\qax\app\__main__.py



Build your own executable from source
-----------------------------------------
There are 3 steps

#. Follow the above process to create QAX environment
#. Use `pyinstaller` to generate a redistributable directory of the dependencies included in the conda env
#. Use Inno Setup to build an msi install file from the redistributable directory contents

::


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
