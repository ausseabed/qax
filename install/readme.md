# Install package instructions
The contents of this directory include build files necessary to generate a
standalone installation package (msi) for QAX. There are three steps;

1. Establish conda environment that is able to run QAX
2. Use `pyinstaller` to generate a redistributable directory of the dependencies included in the conda env
3. Use Inno Setup to build an msi install file from the redistributable directory contents.


## Step 1: Conda environment
Not particularly well covered. Suggest starting with miniconda (on Windows) and installing necessary dependencies (numpy, gdal, hyo2.abc, hyo2.mate) and  QAX itself. *pyinstaller will also need to be installed in this environment.*

Move on to step 2 when qax runs in this environment.

The following command sequence should work, maybe.

    conda create -y -n qax python=3.10
    conda activate qax
    conda env update --file conda-environment.yaml

    pip install .

    pip install pyinstaller



## Step 2: pyinstaller

**NOTE:** The spec file will require some modification to point at the epsg file required by the proj library. Ideally this would be handled by the hook file.

Run the spec file from this directory.

    pyinstaller install/cli.spec

This will produce a `dist` and `build` directory. The dist directory is the 'redistributable directory'.


## Step 3: Inno Setup
Run the iss file from this directory.

    "c:\Program Files (x86)\Inno Setup 6\ISCC.exe" qax.iss

This will produce an `Output` directory containing a single setup file.
