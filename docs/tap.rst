:mod:`~tap` - Working with tabular data
================================================================================

.. module:: tap
  :synopsis: Working with tabular data
  
This module defines the table class that provides convenient functionality to
work with tabular data. It features functions to calculate statistical moments,
e.g. mean, standard deviations as well as functionality to plot the data using
matplotlib.

Basic Usage
--------------------------------------------------------------------------------

Populate table with data:

.. code-block:: python

  from tap import *

  # create table with two columns, x and y both of float type
  tab=Tab(['x', 'y'], 'ff')
  for x in range(1000):
    tab.add_row([x, x**2])

  # create a plot
  plt=tab.plot('x', 'y', save='x-vs-y.png')

Iterating over table items:

.. code-block:: python

  # load table from file
  tab=load(...)

  # iterate over all rows
  for row in tab.rows:
    # print complete row
    print row

  for f in tab.foo:
    print f
  # iterate over all rows of selected columns
  for foo, bar in tab.zip('foo','bar'):
    print foo, bar




The Tab class
--------------------------------------------------------------------------------


.. autoclass:: tap.Tab
  :members:
  :undoc-members: SUPPORTED_TYPES

.. autofunction:: tap.merge
