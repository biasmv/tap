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
  tab=Tab.load(...)

  # get column index for col 'foo'
  idx=tab.get_col_index('foo')

  # iterate over all rows
  for row in tab.rows:
    # print complete row
    print row

    # print value for column 'foo'
    print row[idx]

  # iterate over all rows of selected columns
  for foo, bar in tab.zip('foo','bar'):
    print foo, bar


Functions You Might be Interested In
--------------------------------------------------------------------------------

======================================= ============================================
**Adding/Removing/Reordering data**
:meth:`~tap.Tab.add_row`                add a row to the table
:meth:`~tap.Tab.add_col`                add a column to the table
:meth:`~tap.Tab.remove_col`             remove a column from the table
:meth:`~tap.Tab.rename_col`             rename a column
:meth:`~tap.Tab.extend`                 append a table to the end of another table
:meth:`~tap.merge`                      merge two tables together
:meth:`~tap.Tab.sort`                   sort table by column
:meth:`~tap.Tab.filter`                 filter table by values
:meth:`~tap.Tab.zip`                    extract multiple columns at once
:meth:`~tap.Tab.seach_col_names`        search for matching column names

**Input/Output**
:meth:`~tap.Tab.save`                   save a table to a file
:meth:`~tap.Tab.load`                   load a table from a file
:meth:`~tap.Tab.to_string`              convert a table to a string for printing

**Simple Math**
:meth:`~tap.Tab.min`                    compute the minimum of a column
:meth:`~tap.Tab.max`                    compute the maximum of a column
:meth:`~tap.Tab.sum`                    compute the sum of a column
:meth:`~tap.Tab.mean`                   compute the mean of a column
:meth:`~tap.Tab.row_mean`               compute the mean for each row
:meth:`~tap.Tab.median`                 compute the median of a column
:meth:`~tap.Tab.std_dev`                compute the standard deviation of a column
:meth:`~tap.Tab.count`                  compute the number of items in a column

**More Sophisticated Math**
:meth:`~tap.Tab.correl`                 compute Pearson's correlation coefficient
:meth:`~tap.Tab.spearman_correl`        compute Spearman's rank correlation coefficient
:meth:`~tap.Tab.compute_mcc`            compute Matthew's correlation coefficient
:meth:`~tap.Tab.compute_roc`            compute receiver operating characteristics (ROC)
:meth:`~tap.Tab.compute_enrichment`     compute enrichment
:meth:`~tap.Tab.get_optimal_prefactors` compute optimal coefficients for linear combination of columns

**Plot**
:meth:`~tap.Tab.plot`                   Plot data in 1, 2 or 3 dimensions
:meth:`~tap.Tab.plot_histogram`         Plot data as histogram
:meth:`~tap.Tab.plot_roc`               Plot receiver operating characteristics (ROC)
:meth:`~tap.Tab.plot_enrichment`        Plot enrichment
:meth:`~tap.Tab.plot_hexbin`            Hexagonal density plot
:meth:`~tap.Tab.plot_bar`               Bar plot


======================================= ============================================

The Tab class
--------------------------------------------------------------------------------


.. autoclass:: tap.Tab
  :members:
  :undoc-members: SUPPORTED_TYPES

.. autofunction:: tap.merge
