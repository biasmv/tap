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

Column Types
--------------------------------------------------------------------------------

Table columns have a specific type, e.g. string, float etc. Each cell in a column
must either be of that type or set to not available (None). As a result, a float 
column can't contain string values. The following column types exist:

========== ============
long name  abbreviation
========== ============
string     s
float      f
int        i
bool       b
========== ============


When adding new data to the table, values are automatically coerced (forced) to 
the column type. When coercing fails, a :exc:`ValueError` is thrown.

Specifying Column Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The column types can be specified when initialing a new table. For convenience, 
several different formats are supported, which allow to specify the column types 
as strings, or list using long, or abbreviated forms.  The following 5 examples 
initialise an empty table with a string, float, int and bool column each. 

.. code-block:: python

  # abbreviated, compact form
  tab = Tab(['x', 'y', 'z', 'u'], 'sfib')

  # abbreviated, separated by coma
  tab = Tab(['x', 'y', 'z', 'u'], 's, f, i, b')

  # extended separated by coma
  tab = Tab(['x', 'y', 'z', 'u'], 'string, float, int, bool')


  # list abbreviated
  tab = Tab(['x', 'y', 'z', 'u'], ['s', 'f', 'i', 'b'])

  # list extended
  tab = Tab(['x', 'y', 'z', 'u'], ['string', 'float', 'int', 'bool'])


Guessing Column Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the lazy, the table supports guessing the column type from data when 
initialising a new table. The detection of column types tries to convert each 
value to a particular type, e.g. int. When the type conversion is not successful
for any value, the column type is set to string. As a special case, when the data
arrays are empty, the array types are set to string.

.. code-block:: python

  # initialises a table with an bool and int column
  t = Tab(['x','y'], x='True False False'.split(), y='1 NA 3'.split())
  print t.col_types # bool int

The Tab class
--------------------------------------------------------------------------------


.. autoclass:: tap.Tab
  :members:
  :undoc-members: SUPPORTED_TYPES

.. autofunction:: tap.merge
