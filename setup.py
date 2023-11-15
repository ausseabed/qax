import codecs
import os
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# ------------------------------------------------------------------
#                         HELPER FUNCTIONS

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


# ------------------------------------------------------------------
#                          POPULATE SETUP

setup(
    name="hyo2.qax",
    license="LGPLv3 license",
    use_scm_version=True,
    packages=find_packages(
        exclude=[
            "*.tests",
            "*.tests.*",
            "tests.*",
            "tests",
            "*.test*",
        ]),
    package_data={
        "": [
            "media/*.png", "media/*.ico", "media/*.icns", "media/*.txt",
            "config/*.json", "media/LICENSE", "schemas/**/*.json",
            "**/*.qml"],
    },
    zip_safe=False,
    setup_requires=[
        "setuptools",
        "wheel",
        "setuptools_scm",
    ],
    install_requires=[
        "jsonschema",
    ],
    extras_require={
        "QCTools": ["hyo2.qc"],
        "Mate": ["hyo2.mate"],
    },
    python_requires='>=3.5',
    entry_points={
        "gui_scripts": [
            'qax = hyo2.qax.app.gui:gui',
        ],
        "console_scripts": [
        ],
    },
    test_suite="tests",

    description="A package to perform quality assurance on ocean mapping data.",
    long_description=(read("README.md") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read("HISTORY.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read("AUTHORS.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read(os.path.join("docs", "developer_guide_how_to_contribute.rst"))),
    url="https://github.com/ausseabed/qax",
    classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Office/Business :: Office Suites',
    ],
    keywords="hydrography ocean mapping survey data quality",
    author="Giuseppe Masetti(UNH,CCOM); Tyanne Faulkes(NOAA,OCS)",
    author_email="gmasetti@ccom.unh.edu; tyanne.faulkes@noaa.gov",
)
