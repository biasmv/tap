.. tap documentation master file, created by
   sphinx-quickstart on Sat Feb  9 09:35:28 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:mod:`tap` - Painless Tabular Datamangement for Python
===================================================================================

.. module:: tap
  :synopsis: painless tabular data management for python
  
This module defines the table class that provides convenient functionality to
work with tabular data. It features functions to calculate statistical moments,
e.g. mean, standard deviations as well as functionality to plot the data using
matplotlib.

Contents:

.. toctree::
   :maxdepth: 2

   data
   stats
   plot
   io


The tap API at a glance
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
:meth:`~tap.Tab.zip_non_null`           extract multiple columns at once, ignoring none
:meth:`~tap.Tab.search_col_names`       search for matching column names
:meth:`~tap.Tab.empty`                  check whether table/column is empty
:meth:`~tap.Tab.get_unique`             get unique values of a column
:meth:`~tap.Tab.has_col`                check for existence of column

**Input/Output**
:meth:`~tap.Tab.save`                   save a table to a file
:func:`~tap.load`                       load a table from a file
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
:meth:`~tap.Tab.optimal_prefactors`     compute optimal coefficients for linear combination of columns
:meth:`~tap.Tab.stats`                  get various statistics on a column
:meth:`~tap.Tab.paired_t_test`          perform paired t-test on two columns

**Plot**
:meth:`~tap.Tab.plot`                   Plot data in 1, 2 or 3 dimensions
:meth:`~tap.Tab.plot_histogram`         Plot data as histogram
:meth:`~tap.Tab.plot_roc`               Plot receiver operating characteristics (ROC)
:meth:`~tap.Tab.plot_enrichment`        Plot enrichment
:meth:`~tap.Tab.plot_hexbin`            Hexagonal density plot
:meth:`~tap.Tab.plot_bar`               Bar plot
======================================= ============================================

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

