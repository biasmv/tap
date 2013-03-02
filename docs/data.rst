Handling of Tabular Data
================================================================================

.. module:: tap
  :synopsis: painless tabular data management for python
  
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
This document gives an overview of data handling with the :mod:`tap` module.


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


Adding and Removing Data from a Table
--------------------------------------------------------------------------------

The following methods allow to add and remove data in a row and column-wise
manner.

.. automethod:: tap.Tab.add_row
.. automethod:: tap.Tab.add_col
.. automethod:: tap.Tab.remove_col
.. automethod:: tap.Tab.rename_col


Combining Tables
--------------------------------------------------------------------------------

.. automethod:: tap.Tab.extend
.. autofunction:: tap.merge


Accessing data
--------------------------------------------------------------------------------

The data in a table can be iterated row and column-wise. 

.. automethod:: tap.Tab.zip
.. automethod:: tap.Tab.zip_non_null
.. automethod:: tap.Tab.filter
.. automethod:: tap.Tab.search_col_names
