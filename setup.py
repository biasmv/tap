import os
from setuptools import setup

LONG_DESCRIPTION="""tap provides simple and intuitive interface to 
deal with tabular data from text files. It offers functionality to
manipulate, sort and visualise the data in a comprehensive manner.

It is targeted at users who would like to analyse data from CSV or
other text files. 
"""
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "tap",
    version = "1.0.0",
    author = "Tobias Schmidt, Marco Biasini",
    author_email = "tobias@isntwork.org, marco@isntwork.org",
    description = ("painless tabular data management for Python"),
    license = "BSD",
    keywords = "table, statistics data analysis, plotting, visualisation",
    url = "http://isntwork.org/tap",
    packages=[ 'tap' ],
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Intended Audience :: Science/Research",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
    ],
)
