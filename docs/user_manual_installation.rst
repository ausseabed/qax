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
    :target: https://github.com/ausseabed/hyo2_qax/releases.html
    :width: 100px
    :align: center
    :alt: QAX logo
    :figclass: align-center

    The QAX logo.

If you are on Windows, you can easily install QAX from the latest executable package installer found `here <https://github.com/ausseabed/hyo2_qax/releases.html>`_.

.. note::
    This is the recomended install method for anyone just wanting to use the QAX application

Create your own environment and run QAX from source
-----------------------------------------------------
There are 3 steps

#. Establish conda environment that is able to run QAX
#. Clone code repositories and install unbundled
#. Install unbundled module for QAX

Establish conda environment that is able to run QAX
******************************************************
Start by installing `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ (on Windows) and installing necessary dependencies (numpy, gdal, hyo2.abc, hyo2.mate) and  QAX itself.
The following command sequence is suggested:
::
    conda create -y -n qax python=3.7
    conda activate qax
    
    conda install -y -c conda-forge git
    cd <directory where qax environment was created>
    git clone https://github.com/ausseabed/hyo2_qax
    cd .\hyo2_qax
    conda install -y -c conda-forge --file requirements_conda.txt
    conda install -y -c conda-forge --no-deps cartopy
    conda install -y -c conda-forge  --no-deps pyproj
    pip install -r requirements.txt
    pip install --no-deps git+git://github.com/hydroffice/hyo2_abc.git@master#egg=hyo2.abc
    
Clone code repositories you want to contribute to and install unbundled
*************************************************************************
You need to remove from the requirements.txt file any modules you want to install unbundled.  
As an example if you wanted to contribute to mate plugin then remove it from the requirements.txt file and after that install requirements according to requirements.txt
::
    pip install -r requirements.txt
    
You then need to install the modules you wish to contibute to unbundled, as per the example
::
    git clone https:\\github.com\ausseabed\mate
    pip install -e .\mate\
    
Do the above for all modules you want to install unbundled, e.g. pyall, pygsf, qajson etc.

Clone code repositories and install unbundled
***************************************************
Clone QAX and install unbundled
::
    git clone https:\\github.com\ausseabed\qax
    pip install .\qax\

Build your own executable from source
-----------------------------------------
There are 3 steps

#. Establish conda environment that is able to run QAX
#. Use `pyinstaller` to generate a redistributable directory of the dependencies included in the conda env
#. Use Inno Setup to build an msi install file from the redistributable directory contents

Establish conda environment that is able to run QAX
*******************************************************
Start by installing `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ (on Windows) and installing necessary dependencies (numpy, gdal, hyo2.abc, hyo2.mate) and  QAX itself. *pyinstaller will also need to be installed in this environment.*
The following command sequence is suggested:
:: 
    conda create -y -n qax python=3.7
    conda activate qax
    
    conda install -y pip
    conda install -y -c conda-forge --file requirements_conda.txt
    conda install -y -c conda-forge --no-deps cartopy
    pip install -r requirements.txt
    pip install pypiwin32
    conda install -y -c conda-forge  --no-deps pyproj
    
    pip install --no-deps git+git://github.com/hydroffice/hyo2_abc.git@master#egg=hyo2.abc

    pip install .

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