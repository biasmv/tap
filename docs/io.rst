:mod:`~tap` - Importing and Exporting Tabular Data
===============================================================================

.. currentmodule: tap

The :class:`Tab` class supports importing and exporting of tabular data from 
various sources. Import is achieved through the :func:`load` function, export 
through the table's :meth:`Tab.save` method. 


**Example:**

.. code-block:: python

  # load data from comma separated value file using ',' as the separator
  tab = tap.load('data.csv', sep=',')


.. autofunction:: tap.load


.. automethod:: tap.Tab.save



