'''
Unit tests for Tab class

Author: Tobias Schmidt
'''

import os
import unittest
import glob

HAS_NUMPY=True
HAS_SCIPY=True
HAS_MPL=True
HAS_PIL=True
try:
  import numpy as np
except ImportError:
  HAS_NUMPY=False
  print "Could not find numpy: ignoring some table class unit tests"

try:
  import scipy.stats.mstats
except ImportError:
  HAS_SCIPY=False
  print "Could not find scipy.stats.mstats: ignoring some table class unit tests"
  
try:
  import matplotlib
  matplotlib.use('Agg')
except ImportError:
  HAS_MPL=False
  print "Could not find matplotlib: ignoring some table class unit tests"
  
try:
  import Image
  import ImageChops
except ImportError:
  HAS_PIL=False
  print "Could not find python imagine library: ignoring some table class unit tests"

from tap import *
import fixtures
import helper

class TestTabBase(helper.TabTestCase):

  def testAllowsTosearch_col_names(self):
    tab = fixtures.create_test_table()
    self.assertEquals(tab.search_col_names('d$'), ['second', 'third'])
    self.assertEquals(tab.search_col_names('(first|third)'), ['first','third'])

  def testProvidesDirectAccessToColumns(self):
    tab = Tab(['x', 'two'], 'ii')
    tab.add_row([1,2])
    self.assertEqual([1], list(tab.x))
    self.assertEqual([2], list(tab.two))
    self.assertRaises(AttributeError, tab.__getattr__, 'one')
  def testzip(self):
    tab=Tab(['col1', 'col2', 'col3', 'col4'], 'sssi')
    tab.add_row(['a', 'b', 'c', 1])
    tab.add_row(['x', 'y', 'z', 2])
    z=tab.zip('col1', 'col3')
    self.assertEqual(len(z), 2)
    self.assertEqual(z[0][0], 'a')
    self.assertEqual(z[0][1], 'c')
    self.assertEqual(z[1][0], 'x')
    self.assertEqual(z[1][1], 'z')
    z=tab.zip('col3', 'col1')
    self.assertEqual(len(z), 2)
    self.assertEqual(z[0][0], 'c')
    self.assertEqual(z[0][1], 'a')
    self.assertEqual(z[1][0], 'z')
    self.assertEqual(z[1][1], 'x')
    z=tab.zip('col1', 'col1')
    self.assertEqual(len(z), 2)
    self.assertEqual(z[0][0], 'a')
    self.assertEqual(z[0][1], 'a')
    self.assertEqual(z[1][0], 'x')
    self.assertEqual(z[1][1], 'x')
    z=tab.zip('col1', 'col4')
    self.assertEquals(type(z[0][0]),str)
    self.assertEquals(type(z[1][0]),str)
    self.assertEquals(type(z[0][1]),int)
    self.assertEquals(type(z[1][1]),int)
    self.assertRaises(ValueError, tab.zip, 'col5', 'col3')
  def testpercentiles(self):
    tab = Tab(['nums'], 'i')
    self.assertEqual(tab.percentiles('nums', [0,100]), [None, None])
    self.assertRaises(ValueError, tab.percentiles, 'nums', [101])
    self.assertRaises(ValueError, tab.percentiles, 'nums', [-1])
    for i in (35,15,50,40,20):
      tab.add_row([i])
    self.assertEqual(tab.percentiles('nums', [0,30,40,100]), [15,20,35,50])
  def test_default_initialises_to_empty_table(self):
    tab = Tab()
    self.compare_col_count(tab, 0)
    self.compare_row_count(tab, 0)
    self.assertRaises(ValueError, tab.col_index, 'a')
    
  def testTabInitSingleColEmpty(self):
    '''
    empty table with one float column:
    
     x 
    ---
    
    '''
    tab = Tab(['x'], 'f')
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 0)
    self.compare_col_names(tab, ['x'])
    self.compare_col_types(tab, 'x', 'f')
    
  def testTabInitMultiColEmpty(self):
    '''
    empty table with multiple column with different types:
    
     x  y  z  a 
    ------------
    
    '''
    tab = Tab(['x','y','z','a'], 'sfbi')
    self.compare_col_count(tab, 4)
    self.compare_row_count(tab, 0)
    self.compare_col_names(tab, ['x','y','z','a'])
    self.compare_col_types(tab, ['x','y','z','a'], 'sfbi')
    self.compare_col_types(tab, ['x','y','z','a'], ['string','float','bool','int'])
      
  def testTabInitSingleColSingleValueNonEmpty(self):
    '''
    table with one column and one row:
    
       x   
    -------
      5.000

    '''
    tab = Tab(['x'], 'f', x=5)
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 1)
    self.compare_col_names(tab, ['x'])
    self.compare_col_types(tab, 'x', 'f')
    
  def testTabInitMultiColSingleValueNonEmpty(self):
    '''
    table with three columns and one row:
    
       x      a      z   
    ---------------------
      5.000 False   1.425
    
    '''
    tab = Tab(['x','a','z'], 'fbf', x=5, z=1.425, a=False)
    self.compare_col_count(tab, 3)
    self.compare_row_count(tab, 1)
    self.compare_col_names(tab, ['x','a','z'])
    self.compare_col_types(tab, ['z','x','a'], 'ffb')
    self.compare_data_from_dict(tab, {'x': [5], 'z': [1.425], 'a': [False]})
    
  def testTabInitMultiColSingleValueAndNoneNonEmpty(self):
    '''
    table with three columns and one row with two None values:
    
       x    a1  zzz 
    ----------------
      5.000 NA   NA 
    '''
    tab = Tab(['x','a1','zzz'], 'fbf', x=5)
    self.compare_col_count(tab, 3)
    self.compare_row_count(tab, 1)
    self.compare_col_names(tab, ['x','a1','zzz'])
    self.compare_col_types(tab, ['zzz','x','a1'], 'ffb')
    self.compare_data_from_dict(tab, {'x': [5], 'zzz': [None], 'a1': [None]})
  
  def testTabInitSingleColMultiValueNonEmpty(self):
    '''
    table with one column and five row:
    
       x   
    -------
      0.000
      1.000
      2.000
      3.000
      4.000

    '''
    tab = Tab(['x'], 'f', x=range(5))
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 5)
    self.compare_col_names(tab, ['x'])
    self.compare_col_types(tab, 'x', 'f')
    
  def testTabfilterColNamesTypes(self):
    """
    make sure the col_names and col_types are copied. 
    We don't want them to be referenced to the original table.
    This leads to strange surprises.
    """
    t = Tab(['a', 'b'], 'ii')
    t.add_row([1,2])
    t.add_row([2,3])
    t.add_row([2,3])
    t.add_row([3,3])
    t.add_row([4,3])
    t.add_row([5,3])
    filt = t.filter(a=2)
    filt.add_col('c', 'i')
    self.assertEqual(len(t.col_names), 2)
    self.assertEqual(len(t.col_types), 2)

  def testTabInitMultiColMultiValueNonEmpty(self):
    '''
    table with two column and four rows:
    
      foo     bar
    ---------------
      i         10
      love      11
      unit      12
      tests     13

    '''
    
    tab = Tab(['foo', 'bar'], 'si', bar=range(10,14), foo=['i','love','unit','tests'])
    self.compare_col_count(tab, 2)
    self.compare_row_count(tab, 4)
    self.compare_col_names(tab, ['foo','bar'])
    self.compare_col_types(tab, ['foo', 'bar'], 'si')
    self.compare_data_from_dict(tab, {'bar': [10,11,12,13], 'foo': ['i','love','unit','tests']})
    
  def testTabInitMultiColMissingMultiValue(self):
    '''
    test if error is raised when creating rows with missing data
    '''
    
    self.assertRaises(ValueError, Tab, ['foo', 'bar'], 'si',
                      bar=range(10,14), foo=['i','love','tests'])
    
    
  def testTabInitMultiColMultiValueAndNoneNonEmpty(self):
    '''
    table with two column and four rows with None values:
    
      foo     bar
    ---------------
      i         NA
      love      NA
      unit      NA
      tests     NA

    '''
    tab = Tab(['foo', 'bar'], 'si', foo=['i','love','unit','tests'])
    self.compare_col_count(tab, 2)
    self.compare_row_count(tab, 4)
    self.compare_col_names(tab, ['foo','bar'])
    self.compare_col_types(tab, ['foo', 'bar'], 'si')
    self.compare_data_from_dict(tab, {'bar': [None,None,None,None], 'foo': ['i','love','unit','tests']})
  
  def testTabAddSingleCol(self):
    '''
    init empty table, add one empty column:
    
     first 
    -------
    
    '''
    tab = Tab()
    self.compare_col_count(tab, 0)
    self.compare_row_count(tab, 0)
    tab.add_col('first', 'string')
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 0)
    self.compare_col_names(tab, ['first'])
    self.compare_col_types(tab, 'first', 's')
    
  def testTabAddSingleRow(self):
    '''
    init table with one col, add one row:
    
     first 
    -------
          2
    '''
    tab = Tab(['first'],'i')
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 0)
    tab.add_row([2], overwrite=None)
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 1)
    self.compare_col_names(tab, ['first'])
    self.compare_col_types(tab, 'first', 'i')
    self.compare_data_from_dict(tab, {'first': [2]})
    
  def testTabAddSingleColSingleRow(self):
    '''
    init empty table, add one col, add one row:
    
     first 
    -------
          2
    '''
    tab = Tab()
    tab.add_col('first', 'int')
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 0)
    tab.add_row([2], overwrite=None)
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 1)
    self.compare_col_names(tab, ['first'])
    self.compare_col_types(tab, 'first', 'i')
    self.compare_data_from_dict(tab, {'first': [2]})
  
  def testTabAddSingleColWithRow(self):
    '''
    init table with two cols, add row with data, add third column:
    
     first  second  third 
    ----------------------
     x            3  3.141

    '''
    tab = Tab(['first','second'],'si')
    self.compare_col_count(tab, 2)
    self.compare_row_count(tab, 0)
    self.compare_col_types(tab, ['first','second'], 'si')
    tab.add_row(['x',3], overwrite=None)
    self.compare_col_count(tab, 2)
    self.compare_row_count(tab, 1)
    tab.add_col('third', 'float', 3.141)
    self.compare_col_count(tab, 3)
    self.compare_row_count(tab, 1)
    self.compare_col_types(tab, ['first','third','second'], 'sfi')
    self.compare_data_from_dict(tab, {'second': [3], 'first': ['x'], 'third': [3.141]})
    
  def testTabAddMultiColMultiRow(self):
    '''
    init empty table add three cols, add three rows with data:
    
      first  second  third 
    ----------------------
     x            3  1.000
     foo          6  2.200
     bar          9  3.300

    '''
    tab = Tab()
    tab.add_col('first', 'string')
    tab.add_col('second', 'int')
    tab.add_col('third', 'float')
    self.compare_col_count(tab, 3)
    self.compare_row_count(tab, 0)
    self.compare_col_types(tab, ['first','second', 'third'], 'sif')
    tab.add_row(['x',3, 1.0], overwrite=None)
    tab.add_row(['foo',6, 2.2], overwrite=None)
    tab.add_row(['bar',9, 3.3], overwrite=None)
    self.compare_col_count(tab, 3)
    self.compare_row_count(tab, 3)
    self.compare_data_from_dict(tab, {'second': [3,6,9], 'first': ['x','foo','bar'], 'third': [1,2.2,3.3]})

  def testTabAddMultiColMultiRowFromDict(self):
    '''
    init empty table add three cols, add three rows with data:
    
      first  second  third 
    ----------------------
     x            3  1.000
     foo          6  2.200
     bar          9  3.300

    '''
    tab = Tab()
    tab.add_col('first', 'string')
    tab.add_col('second', 'int')
    tab.add_col('aaa', 'float')
    self.compare_col_count(tab, 3)
    self.compare_row_count(tab, 0)
    self.compare_col_types(tab, ['first','second', 'aaa'], 'sif')
    tab.add_row({'first':'x','second':3, 'aaa':1.0}, overwrite=None)
    tab.add_row({'aaa':2.2, 'second':6, 'first':'foo'}, overwrite=None)
    tab.add_row({'second':9, 'aaa':3.3, 'first':'bar'}, overwrite=None)
    self.compare_col_count(tab, 3)
    self.compare_row_count(tab, 3)
    self.compare_data_from_dict(tab, {'second': [3,6,9], 'first': ['x','foo','bar'], 'aaa': [1,2.2,3.3]})
    
  def testTabAddMultiRowMultiCol(self):
    '''
    init empty table add one col, add three rows with data,
    add one col without data, add one col with data:
    
      first  second  third 
    ----------------------
     x        NA     3.141
     foo      NA     3.141
     bar      NA     3.141

    '''
    tab = Tab()
    tab.add_col('first', 'string')
    self.compare_col_count(tab, 1)
    self.compare_row_count(tab, 0)
    self.compare_col_types(tab, ['first'], 's')
    tab.add_row(['x'], overwrite=None)
    tab.add_row(['foo'], overwrite=None)
    tab.add_row(['bar'], overwrite=None)
    tab.add_col('second', 'int')
    tab.add_col('third', 'float', 3.141)
    self.compare_col_count(tab, 3)
    self.compare_row_count(tab, 3)
    self.compare_data_from_dict(tab, {'second': [None,None,None],
                                   'first': ['x','foo','bar'],
                                   'third': [3.141, 3.141, 3.141]})

  def testAddMultiRowFromDict(self):
    tab = Tab(['x','y','z'], 'fff')
    data = {'x': [1.2, 1.5], 'z': [1.6, 2.4]}
    tab.add_row(data)
    self.compare_data_from_dict(tab, {'x': [1.2, 1.5],
                                   'y': [None, None],
                                   'z': [1.6, 2.4]})

    data = {'y': [5.1, 3.4, 1.5]}
    tab.add_row(data)
    self.compare_data_from_dict(tab, {'x': [1.2, 1.5, None, None, None],
                                   'y': [None, None, 5.1, 3.4, 1.5],
                                   'z': [1.6, 2.4, None, None, None]})

    # must raise since length of data is not the same
    data = {'x': [1.2, 1.5], 'y': 1.2, 'z': [1.6, 2.4]}
    self.assertRaises(ValueError, tab.add_row, data)

    # must raise since length of data is not the same
    data = {'x': [1.2, 1.5], 'y': [1.2], 'z': [1.6, 2.4]}
    self.assertRaises(ValueError, tab.add_row, data)

    # overwrite certain rows
    data = {'x': [1.2, 1.9], 'z': [7.9, 3.5]}
    tab.add_row(data, overwrite='x')
    self.compare_data_from_dict(tab, {'x': [1.2, 1.5, None, None, None, 1.9],
                                   'y': [None, None, 5.1, 3.4, 1.5, None],
                                   'z': [7.9, 2.4, None, None, None, 3.5]})

  def testadd_rowFromDictWithOverwrite(self):
    '''
    add rows from dictionary with overwrite (i.e. overwrite third row with additional data)
    
      x     foo   bar 
    ------------------
     row1  True      1
     row2    NA      2
     row3  False     3
     
    '''
    tab = Tab()
    tab.add_col('x', 'string')
    tab.add_col('foo', 'bool')
    tab.add_col('bar', 'int')
    tab.add_row(['row1',True, 1])
    tab.add_row(['row2',None, 2])
    tab.add_row(['row3',False, None])
    self.compare_data_from_dict(tab, {'x': ['row1', 'row2', 'row3'],
                                   'foo': [True, None, False],
                                   'bar': [1, 2, None]})
    tab.add_row({'x':'row3', 'bar':3}, overwrite='x')
    self.compare_data_from_dict(tab, {'x': ['row1', 'row2', 'row3'],
                                   'foo': [True, None, False],
                                   'bar': [1, 2, 3]})
    
  def testadd_rowFromListWithOverwrite(self):
    '''
    add rows from list with overwrite (i.e. overwrite third row with additional data)
    
      x     foo   bar 
    ------------------
     row1  True      1
     row2    NA      2
     row3  True      3
     
    '''
    
    tab = Tab()
    tab.add_col('x', 'string')
    tab.add_col('foo', 'bool')
    tab.add_col('bar', 'int')
    tab.add_row(['row1',True, 1])
    tab.add_row(['row2',None, 2])
    tab.add_row(['row3',False, None])
    self.compare_data_from_dict(tab, {'x': ['row1', 'row2', 'row3'],
                                   'foo': [True, None, False],
                                   'bar': [1, 2, None]})
    tab.add_row(['row3', True, 3], overwrite='x')
    self.compare_data_from_dict(tab, {'x': ['row1', 'row2', 'row3'],
                                   'foo': [True, None, True],
                                   'bar': [1, 2, 3]})

  def testRaiseErrorOnWrongDataLengthadd_col(self):
    tab = Tab()
    tab.add_col('a','f',[4.2,4.2,4.2])
    self.assertRaises(ValueError, tab.add_col, 'b', 'f', [4.2,4.2])

  def testRaiseErrorColNameAlreadyExists(self):
    tab = Tab()
    tab.add_col('awesome','f')
    self.assertRaises(ValueError, tab.add_col, 'awesome', 'f')

  def testRaiseErrorOnWrongColumnTypes(self):
    # wrong columns types in init
    self.assertRaises(ValueError, Tab, ['bla','bli'], 'ab')
    
    tab = Tab()
    # wrong column types in add_col
    self.assertRaises(ValueError, tab.add_col, 'bla', 'a')
    
  def testParseColumnTypes(self):
    types = Tab._parse_col_types(['i','f','s','b'])
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Tab._parse_col_types(['int','float','string','bool'])
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Tab._parse_col_types(['i','float','s','bool'])
    self.assertEquals(types, ['int','float','string','bool'])

    types = Tab._parse_col_types(['i','fLOAT','S','bool'])
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Tab._parse_col_types('ifsb')
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Tab._parse_col_types('int,float,string,bool')
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Tab._parse_col_types('int,f,s,bool')
    self.assertEquals(types, ['int','float','string','bool'])
    
    types = Tab._parse_col_types('INT,F,s,bOOL')
    self.assertEquals(types, ['int','float','string','bool'])

    types = Tab._parse_col_types('boOl')
    self.assertEquals(types, ['bool'])
    
    types = Tab._parse_col_types('S')
    self.assertEquals(types, ['string'])
    
    types = Tab._parse_col_types(['i'])
    self.assertEquals(types, ['int'])
    
    types = Tab._parse_col_types(['FLOAT'])
    self.assertEquals(types, ['float'])

    self.assertRaises(ValueError, Tab._parse_col_types, 'bfstring')
    self.assertRaises(ValueError, Tab._parse_col_types, ['b,f,string'])
    self.assertRaises(ValueError, Tab._parse_col_types, 'bi2')
    self.assertRaises(ValueError, Tab._parse_col_types, ['b',2,'string'])
    self.assertRaises(ValueError, Tab._parse_col_types, [['b'],['f','string']])
    self.assertRaises(ValueError, Tab._parse_col_types, 'a')
    self.assertRaises(ValueError, Tab._parse_col_types, 'foo')
    self.assertRaises(ValueError, Tab._parse_col_types, ['a'])
    self.assertRaises(ValueError, Tab._parse_col_types, ['foo'])
  
  def testShortLongColumnTypes(self):
    tab = Tab(['x','y','z','a'],['i','f','s','b'])
    self.compare_col_types(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Tab(['x','y','z','a'],['int','float','string','bool'])
    self.compare_col_types(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Tab(['x','y','z','a'],['i','float','s','bool'])
    self.compare_col_types(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Tab(['x','y','z','a'],['i','fLOAT','S','bool'])
    self.compare_col_types(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Tab(['x','y','z','a'],'ifsb')
    self.compare_col_types(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Tab(['x','y','z','a'],'int,float,string,bool')
    self.compare_col_types(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Tab(['x','y','z','a'],'int,f,s,bool')
    self.compare_col_types(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Tab(['x','y','z','a'],'INT,F,s,bOOL')
    self.compare_col_types(tab, ['x','y','z','a'], 'ifsb')
    
    tab = Tab(['x'], 'boOl')
    self.compare_col_types(tab, ['x'], 'b')
    tab = Tab(['x'], 'B')
    self.compare_col_types(tab, ['x'], 'b')
    tab = Tab(['x'], ['b'])
    self.compare_col_types(tab, ['x'], 'b')
    tab = Tab(['x'], ['Bool'])
    self.compare_col_types(tab, ['x'], 'b')
    
    self.assertRaises(ValueError, Tab, ['x','y','z'], 'bfstring')
    self.assertRaises(ValueError, Tab, ['x','y','z'], ['b,f,string'])
    self.assertRaises(ValueError, Tab, ['x','y','z'], 'bi2')
    self.assertRaises(ValueError, Tab, ['x','y','z'], ['b',2,'string'])
    self.assertRaises(ValueError, Tab, ['x','y','z'], [['b'],['f','string']])
    self.assertRaises(ValueError, Tab, ['x'], 'a')
    self.assertRaises(ValueError, Tab, ['x'], 'foo')
    self.assertRaises(ValueError, Tab, ['x'], ['a'])
    self.assertRaises(ValueError, Tab, ['x'], ['foo'])
    
  def testremove_col(self):
    tab = fixtures.create_test_table()
    self.compare_data_from_dict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    tab.remove_col("second")
    self.compare_data_from_dict(tab, {'first': ['x','foo',None], 'third': [None,2.2,3.3]})
    
    # raise error when column is unknown
    tab = fixtures.create_test_table()
    self.assertRaises(ValueError, tab.remove_col, "unknown col")
    
  def testsortTab(self):
    tab = fixtures.create_test_table()
    self.compare_data_from_dict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    tab.sort('first', '-')
    self.compare_data_from_dict(tab, {'first': [None,'foo','x'], 'second': [9,None,3], 'third': [3.3,2.2,None]})
    tab.sort('first', '+')
    self.compare_data_from_dict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    tab.sort('third', '+')
    self.compare_data_from_dict(tab, {'first': [None,'foo','x'], 'second': [9,None,3], 'third': [3.3,2.2,None]})


  def testmergeTab(self):
    '''
    merge the following two tables:
    
    x     y           x     u   
    -------           -------
    1 |  10           1 | 100
    2 |  15           3 | 200
    3 |  20           4 | 400  
    
    to get (only_matching=False):
    
    x      y     u
    ---------------
    1 |   10 |  100
    2 |   15 |   NA
    3 |   20 |  200
    4 |   NA |  400
    
    or (only_matching=True):
    
    x      y     u
    ---------------
    1 |   10 |  100
    3 |   20 |  200
    
    '''
    tab1 = Tab(['x','y'],['int','int'])
    tab1.add_row([1,10])
    tab1.add_row([2,15])
    tab1.add_row([3,20])
    
    tab2 = Tab(['x','u'],['int','int'])
    tab2.add_row([1,100])
    tab2.add_row([3,200])
    tab2.add_row([4,400])
    
    tab_merged = merge(tab1, tab2, 'x', only_matching=False)
    tab_merged.sort('x', order='-')
    self.compare_data_from_dict(tab_merged, {'x': [1,2,3,4], 'y': [10,15,20,None], 'u': [100,None,200,400]})
    
    tab_merged = merge(tab1, tab2, 'x', only_matching=True)
    tab_merged.sort('x', order='-')
    self.compare_data_from_dict(tab_merged, {'x': [1,3], 'y': [10,20], 'u': [100,200]})
    
  def testfilterTab(self):
    tab = fixtures.create_test_table()
    tab.add_row(['foo',1,5.15])
    tab.add_row(['foo',0,1])
    tab.add_row(['foo',1,12])
    
    # filter on one column
    tab_filtered = tab.filter(first='foo')
    self.compare_data_from_dict(tab_filtered, {'first':['foo','foo','foo','foo'],
                                            'second':[None,1,0,1],
                                            'third':[2.2,5.15,1.0,12.0]})
    
    # filter on multiple columns
    tab_filtered = tab.filter(first='foo',second=1)
    self.compare_data_from_dict(tab_filtered, {'first':['foo','foo'],
                                            'second':[1,1],
                                            'third':[5.15,12.0]})
    
    # raise Error when using non existing column name for filtering
    self.assertRaises(ValueError,tab.filter,first='foo',nonexisting=1)
    
  def testminTab(self):
    tab = fixtures.create_test_table()
    tab.add_col('fourth','bool',[True,True,False])

    self.assertEquals(tab.min('first'),'foo')
    self.assertEquals(tab.min('second'),3)
    self.assertAlmostEquals(tab.min('third'),2.2)
    self.assertEquals(tab.min('fourth'),False)
    self.assertRaises(ValueError,tab.min,'fifth')
    
    self.assertEquals(tab.min_idx('first'),1)
    self.assertEquals(tab.min_idx('second'),0)
    self.assertAlmostEquals(tab.min_idx('third'),1)
    self.assertEquals(tab.min_idx('fourth'),2)
    self.assertRaises(ValueError,tab.min_idx,'fifth')
    
    self.assertEquals(tab.min_row('first'),['foo', None, 2.20, True])
    self.assertEquals(tab.min_row('second'),['x', 3, None, True])
    self.assertEquals(tab.min_row('third'),['foo', None, 2.20, True])
    self.assertEquals(tab.min_row('fourth'),[None, 9, 3.3, False])
    self.assertRaises(ValueError,tab.min_row,'fifth')
    
  def testmaxTab(self):
    tab = fixtures.create_test_table()
    tab.add_col('fourth','bool',[False,True,True])
    
    self.assertEquals(tab.max('first'),'x')
    self.assertEquals(tab.max('second'),9)
    self.assertAlmostEquals(tab.max('third'),3.3)
    self.assertEquals(tab.max('fourth'),True)
    self.assertRaises(ValueError,tab.max,'fifth')
    
    self.assertEquals(tab.max_idx('first'),0)
    self.assertEquals(tab.max_idx('second'),2)
    self.assertAlmostEquals(tab.max_idx('third'),2)
    self.assertEquals(tab.max_idx('fourth'),1)
    self.assertRaises(ValueError,tab.max_idx,'fifth')
    
    self.assertEquals(tab.max_row('first'),['x', 3, None, False])
    self.assertEquals(tab.max_row('second'),[None, 9, 3.3, True])
    self.assertEquals(tab.max_row('third'),[None, 9, 3.3, True])
    self.assertEquals(tab.max_row('fourth'),['foo', None, 2.2, True])
    self.assertRaises(ValueError,tab.max_row,'fifth')
    
  def testsumTab(self):
    tab = fixtures.create_test_table()
    tab.add_col('fourth','bool',[False,True,False])
    tab.add_col('fifth','string',['foo','bar',None])
    
    self.assertRaises(TypeError,tab.sum,'first')
    self.assertEquals(tab.sum('second'),12)
    self.assertAlmostEquals(tab.sum('third'),5.5)
    self.assertEquals(tab.sum('fourth'),1)
    self.assertRaises(TypeError,tab.sum,'fifth')
    self.assertRaises(ValueError,tab.sum,'sixth')
    
  def testmedianTab(self):
    tab = fixtures.create_test_table()
    tab.add_col('fourth','bool',[False,True,False])
    tab.add_col('fifth','string',['foo','bar',None])
    
    self.assertRaises(TypeError,tab.median,'first')
    self.assertEquals(tab.median('second'),6.0)
    self.assertAlmostEquals(tab.median('third'),2.75)
    self.assertEquals(tab.median('fourth'),False)
    self.assertRaises(TypeError,tab.median,'fifth')
    self.assertRaises(ValueError,tab.median,'sixth')
    
  def testmeanTab(self):
    tab = fixtures.create_test_table()
    tab.add_col('fourth','bool',[False,True,False])
    tab.add_col('fifth','string',['foo','bar',None])
    
    self.assertRaises(TypeError,tab.mean,'first')
    self.assertAlmostEquals(tab.mean('second'),6.0)
    self.assertAlmostEquals(tab.mean('third'),2.75)
    self.assertAlmostEquals(tab.mean('fourth'),0.33333333)
    self.assertRaises(TypeError,tab.mean,'fifth')
    self.assertRaises(ValueError,tab.mean,'sixth')
    
  def testrow_meanTab(self):
    '''
      first  second  third fourth
    -----------------------------
     x            3     NA      1
     foo         NA  2.200      2
     NA           9  3.300      3
     NA          NA     NA     NA
    '''
    tab = fixtures.create_test_table()
    tab.add_col('fourth','float',[1,2,3])
    tab.add_row([None, None, None, None])
    
    self.assertRaises(TypeError, tab.row_mean, 'mean', ['first', 'second'])
    tab.row_mean('mean', ['third', 'second', 'fourth'])
    self.compare_data_from_dict(tab, {'mean': [2,2.1,5.1,None],
                                   'first': ['x','foo',None,None],
                                   'second': [3,None,9,None],
                                   'third': [None,2.2,3.3,None],
                                   'fourth': [1,2,3,None]})
    
    
  def teststd_devTab(self):
    tab = fixtures.create_test_table()
    tab.add_col('fourth','bool',[False,True,False])
    tab.add_col('fifth','string',['foo','bar',None])
    
    self.assertRaises(TypeError,tab.std_dev,'first')
    self.assertAlmostEquals(tab.std_dev('second'),3.0)
    self.assertAlmostEquals(tab.std_dev('third'),0.55)
    self.assertAlmostEquals(tab.std_dev('fourth'),0.47140452079)
    self.assertRaises(TypeError,tab.std_dev,'fifth')
    self.assertRaises(ValueError,tab.std_dev,'sixth')
    
  def testcountTab(self):
    tab = fixtures.create_test_table()
    tab.add_col('fourth','bool',[False,True,False])
    
    self.assertEquals(tab.count('first'),2)
    self.assertEquals(tab.count('second'),2)
    self.assertEquals(tab.count('third'),2)
    self.assertEquals(tab.count('fourth'),3)
    self.assertEquals(tab.count('first', ignore_nan=False),3)
    self.assertEquals(tab.count('second', ignore_nan=False),3)
    self.assertEquals(tab.count('third', ignore_nan=False),3)
    self.assertEquals(tab.count('fourth', ignore_nan=False),3)
    self.assertRaises(ValueError,tab.count,'fifth')
    
  def testCalcEnrichment(self):
    enrx_ref = [0.0, 0.041666666666666664, 0.083333333333333329, 0.125, 0.16666666666666666, 0.20833333333333334, 0.25, 0.29166666666666669, 0.33333333333333331, 0.375, 0.41666666666666669, 0.45833333333333331, 0.5, 0.54166666666666663, 0.58333333333333337, 0.625, 0.66666666666666663, 0.70833333333333337, 0.75, 0.79166666666666663, 0.83333333333333337, 0.875, 0.91666666666666663, 0.95833333333333337, 1.0]
    enry_ref = [0.0, 0.16666666666666666, 0.33333333333333331, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.66666666666666663, 0.66666666666666663, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 0.83333333333333337, 1.0, 1.0, 1.0, 1.0]
    
    tab = Tab(['score', 'rmsd', 'classific'], 'ffb',
                score=[2.64,1.11,2.17,0.45,0.15,0.85,1.13,2.90,0.50,1.03,1.46,2.83,1.15,2.04,0.67,1.27,2.22,1.90,0.68,0.36,1.04,2.46,0.91,0.60],
                rmsd=[9.58,1.61,7.48,0.29,1.68,3.52,3.34,8.17,4.31,2.85,6.28,8.78,0.41,6.29,4.89,7.30,4.26,3.51,3.38,0.04,2.21,0.24,7.58,8.40],
                classific=[False,True,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,True,False,False])
    
    enrx,enry = tab.compute_enrichment(score_col='score', score_dir='-',
                                      class_col='rmsd', class_cutoff=2.0,
                                      class_dir='-')
    
    for x,y,refx,refy in zip(enrx,enry,enrx_ref,enry_ref):
      self.assertAlmostEquals(x,refx)
      self.assertAlmostEquals(y,refy)
    
    enrx,enry = tab.compute_enrichment(score_col='score', score_dir='-',
                                      class_col='classific')
    
    for x,y,refx,refy in zip(enrx,enry,enrx_ref,enry_ref):
      self.assertAlmostEquals(x,refx)
      self.assertAlmostEquals(y,refy)
    
    tab.add_col('bad','string','col')
    
    self.assertRaises(TypeError, tab.compute_enrichment, score_col='classific',
                      score_dir='-', class_col='rmsd', class_cutoff=2.0,
                      class_dir='-')
    
    self.assertRaises(TypeError, tab.compute_enrichment, score_col='bad',
                      score_dir='-', class_col='rmsd', class_cutoff=2.0,
                      class_dir='-')
    
    self.assertRaises(TypeError, tab.compute_enrichment, score_col='score',
                      score_dir='-', class_col='bad', class_cutoff=2.0,
                      class_dir='-')
    
    self.assertRaises(ValueError, tab.compute_enrichment, score_col='score',
                      score_dir='x', class_col='rmsd', class_cutoff=2.0,
                      class_dir='-')
    
    self.assertRaises(ValueError, tab.compute_enrichment, score_col='score',
                      score_dir='+', class_col='rmsd', class_cutoff=2.0,
                      class_dir='y')
    
  def testCalcEnrichmentAUCwithNone(self):
    if not HAS_NUMPY:
      return
    tab = Tab(['pred_bfactors','ref_distances'], 'ff',
                ref_distances=[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 2.445, 2.405, 2.361, 2.124, 1.957, 1.897, 1.422, 1.348, 1.247, 1.165, 1.153, 1.011, 0.992, 0.885, 0.852, 0.775, 0.757, 0.755, 0.735, 0.71, 0.656, 0.636, 0.609, 0.607, 0.604, 0.595, 0.572, 0.549, 0.458, 0.438, 0.41, 0.345, 0.304, 0.254, 0.241, 0.227, 2.68, 1.856, 1.312, 0.453],
                pred_bfactors=[1.85000,  2.01000,  2.12000,  2.14000,  2.15000,  2.18000,  2.20000,  2.26000,  2.28000,  2.31000,  2.37000,  2.38000,  2.39000,  2.39000,  2.43000,  2.43000,  2.49000,  2.51000,  2.56000,  2.58000,  2.65000,  2.67000,  2.72000,  2.75000,  2.77000,  2.81000,  2.91000,  2.95000,  3.09000,  3.12000,  3.25000,  3.30000,  3.33000,  3.38000,  3.39000,  3.41000,  3.41000,  3.45000,  3.57000,  3.59000,  3.64000,  3.76000,  3.76000,  3.92000,  3.95000,  3.95000,  4.05000,  4.06000,  4.07000,  4.14000,  4.14000,  4.18000,  4.24000,  4.28000,  4.40000,  4.43000,  4.43000,  4.48000,  4.50000,  4.51000,  4.54000,  4.63000,  4.64000,  4.79000,  4.93000,  5.07000,  5.12000,  5.20000,  5.41000,  5.42000,  5.44000,  5.52000,  5.68000,  5.78000,  5.80000,  5.93000,  6.11000,  6.31000,  6.50000,  6.53000,  6.55000,  6.60000,  6.73000,  6.79000,  6.81000,  7.44000,  8.45000,  8.81000,  9.04000,  9.29000,  9.30000, 10.99000, 11.42000, 12.55000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 99.99000, 99.99000, 99.99000, 99.99000])

    auc = tab.compute_enrichment_auc(score_col='pred_bfactors', class_col='ref_distances')
    self.assertAlmostEqual(auc, 0.50714285714285)

    # when removing all None lines, no true positive is left
    auc = tab.compute_enrichment_auc(score_col='ref_distances', class_col='pred_bfactors')
    self.assertEqual(auc, None)

    # when increasing the cutoff, we have again true positives
    auc = tab.compute_enrichment_auc(score_col='ref_distances', class_col='pred_bfactors', class_cutoff=60)
    self.assertAlmostEqual(auc, 0.52013888888)

  def testCalcEnrichmentAUC(self):
    if not HAS_NUMPY:
      return
    auc_ref = 0.65277777777777779
    tab = Tab(['score', 'rmsd', 'classific'], 'ffb',
                score=[2.64,1.11,2.17,0.45,0.15,0.85,1.13,2.90,0.50,1.03,1.46,2.83,1.15,2.04,0.67,1.27,2.22,1.90,0.68,0.36,1.04,2.46,0.91,0.60],
                rmsd=[9.58,1.61,7.48,0.29,1.68,3.52,3.34,8.17,4.31,2.85,6.28,8.78,0.41,6.29,4.89,7.30,4.26,3.51,3.38,0.04,2.21,0.24,7.58,8.40],
                classific=[False,True,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,True,False,False])
 
    auc = tab.compute_enrichment_auc(score_col='score', score_dir='-',
                                   class_col='rmsd', class_cutoff=2.0,
                                   class_dir='-')
    
    self.assertAlmostEquals(auc, auc_ref)

  def testplot_roc(self):
    if not HAS_MPL or not HAS_PIL:
      return
    tab = Tab(['classific', 'score'], 'bf',
                classific=[True, True, False, True, True, True, False, False, True, False, True, False, True, False, False, False, True, False, True, False],
                score=[0.9, 0.8, 0.7, 0.6, 0.55, 0.54, 0.53, 0.52, 0.51, 0.505, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.30, 0.1])
    pl = tab.plot_roc(score_col='score', score_dir='+',
                     class_col='classific',
                     save=os.path.join("tests/data","roc-out.png"))
    img1 = Image.open(os.path.join("tests/data","roc-out.png"))
    #img2 = Image.open(os.path.join("data","roc.png"))
    #self.CompareImages(img1, img2)

    # no true positives
    tab = Tab(['classific', 'score'], 'bf',
                classific=[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
                score=[0.9, 0.8, 0.7, 0.6, 0.55, 0.54, 0.53, 0.52, 0.51, 0.505, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.30, 0.1])
    pl = tab.plot_roc(score_col='score', score_dir='+',
                     class_col='classific',
                     save=os.path.join("tests/data","roc-out.png"))
    self.assertEquals(pl, None)

  def testplot_rocSameValues(self):
    if not HAS_MPL or not HAS_PIL:
      return
    tab = Tab(['classific', 'score'], 'bf',
                classific=[True, True, False, True, True, True, False, False, True, False, True, False, True, False, False, False, True, False, True, False],
                score=[0.9, 0.8, 0.7, 0.7, 0.7, 0.7, 0.53, 0.52, 0.51, 0.505, 0.4, 0.4, 0.4, 0.4, 0.36, 0.35, 0.34, 0.33, 0.30, 0.1])
    pl = tab.plot_roc(score_col='score', score_dir='+',
                     class_col='classific',
                     save=os.path.join("tests/data","roc-same-val-out.png"))
    img1 = Image.open(os.path.join("tests/data","roc-same-val-out.png"))
    #img2 = Image.open(os.path.join("data","roc-same-val.png"))
    #self.CompareImages(img1, img2)
    #pl.show()

  def testCalcROCAUCwithNone(self):
    if not HAS_NUMPY:
      return
    tab = Tab(['pred_bfactors','ref_distances'], 'ff',
                ref_distances=[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 2.445, 2.405, 2.361, 2.124, 1.957, 1.897, 1.422, 1.348, 1.247, 1.165, 1.153, 1.011, 0.992, 0.885, 0.852, 0.775, 0.757, 0.755, 0.735, 0.71, 0.656, 0.636, 0.609, 0.607, 0.604, 0.595, 0.572, 0.549, 0.458, 0.438, 0.41, 0.345, 0.304, 0.254, 0.241, 0.227, 2.68, 1.856, 1.312, 0.453],
                pred_bfactors=[1.85000,  2.01000,  2.12000,  2.14000,  2.15000,  2.18000,  2.20000,  2.26000,  2.28000,  2.31000,  2.37000,  2.38000,  2.39000,  2.39000,  2.43000,  2.43000,  2.49000,  2.51000,  2.56000,  2.58000,  2.65000,  2.67000,  2.72000,  2.75000,  2.77000,  2.81000,  2.91000,  2.95000,  3.09000,  3.12000,  3.25000,  3.30000,  3.33000,  3.38000,  3.39000,  3.41000,  3.41000,  3.45000,  3.57000,  3.59000,  3.64000,  3.76000,  3.76000,  3.92000,  3.95000,  3.95000,  4.05000,  4.06000,  4.07000,  4.14000,  4.14000,  4.18000,  4.24000,  4.28000,  4.40000,  4.43000,  4.43000,  4.48000,  4.50000,  4.51000,  4.54000,  4.63000,  4.64000,  4.79000,  4.93000,  5.07000,  5.12000,  5.20000,  5.41000,  5.42000,  5.44000,  5.52000,  5.68000,  5.78000,  5.80000,  5.93000,  6.11000,  6.31000,  6.50000,  6.53000,  6.55000,  6.60000,  6.73000,  6.79000,  6.81000,  7.44000,  8.45000,  8.81000,  9.04000,  9.29000,  9.30000, 10.99000, 11.42000, 12.55000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 50.00000, 99.99000, 99.99000, 99.99000, 99.99000])

    auc = tab.compute_roc_auc(score_col='pred_bfactors', class_col='ref_distances')
    self.assertAlmostEqual(auc, 0.55714285714285705)

    # when removing all None lines, no true positive is left
    auc = tab.compute_roc_auc(score_col='ref_distances', class_col='pred_bfactors')
    self.assertEqual(auc, None)

    # when increasing the cutoff, we have again true positives
    auc = tab.compute_roc_auc(score_col='ref_distances', class_col='pred_bfactors', class_cutoff=60)
    self.assertAlmostEqual(auc, 0.701388888888888)

  def testCalcROCAUC(self):
    if not HAS_NUMPY:
      return
    auc_ref = 0.68
    tab = Tab(['classific', 'score'], 'bf',
                classific=[True, True, False, True, True, True, False, False, True, False, True, False, True, False, False, False, True, False, True, False],
                score=[0.9, 0.8, 0.7, 0.6, 0.55, 0.54, 0.53, 0.52, 0.51, 0.505, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.30, 0.1])
    auc = tab.compute_roc_auc(score_col='score', score_dir='+', class_col='classific')
    self.assertAlmostEquals(auc, auc_ref)

    # no true positives
    tab = Tab(['classific', 'score'], 'bf',
                classific=[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
                score=[0.9, 0.8, 0.7, 0.6, 0.55, 0.54, 0.53, 0.52, 0.51, 0.505, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.30, 0.1])
    auc = tab.compute_roc_auc(score_col='score', score_dir='+', class_col='classific')
    self.assertEquals(auc, None)

  def testCalcROCAUCWithCutoff(self):
    if not HAS_NUMPY:
      return
    tab = Tab(['classific', 'score'], 'ff',
                classific=[0.9, 0.8, 0.7, 0.6, 0.55, 0.54, 0.53, 0.52, 0.51, 0.505, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.30, 0.1],
                score=[0.9, 0.8, 0.7, 0.6, 0.55, 0.54, 0.53, 0.52, 0.51, 0.505, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.30, 0.1])
    auc = tab.compute_roc_auc(score_col='score', class_col='classific', class_cutoff=0.5)
    self.assertEquals(auc, 1.0)

    # no true positives
    auc = tab.compute_roc_auc(score_col='score', class_col='classific', class_cutoff=1.0)
    self.assertEquals(auc, None)

  def testCalcROCFromFile(self):
    if not HAS_NUMPY:
      return
    tab = load(os.path.join('tests/data','roc_table.dat'))
    auc = tab.compute_roc_auc(score_col='prediction', class_col='reference', class_cutoff=0.4)
    self.assertEquals(auc, 1.0)
      

  def testCalcROCAUCSameValues(self):
    if not HAS_NUMPY:
      return
    auc_ref = 0.685
    tab = Tab(['classific', 'score'], 'bf',
                classific=[True, True, False, True, True, True, False, False, True, False, True, False, True, False, False, False, True, False, True, False],
                score=[0.9, 0.8, 0.7, 0.7, 0.7, 0.7, 0.53, 0.52, 0.51, 0.505, 0.4, 0.4, 0.4, 0.4, 0.36, 0.35, 0.34, 0.33, 0.30, 0.1])
    auc = tab.compute_roc_auc(score_col='score', score_dir='+', class_col='classific')
    self.assertAlmostEquals(auc, auc_ref)

  def testCalcMCC(self):
    tab = Tab(['score', 'rmsd', 'class_rmsd', 'class_score', 'class_wrong'], 'ffbbb',
                score=      [2.64, 1.11, 2.17, 0.45,0.15,0.85, 1.13, 2.90, 0.50, 1.03, 1.46, 2.83, 1.15, 2.04, 0.67, 1.27, 2.22, 1.90, 0.68, 0.36,1.04, 2.46, 0.91,0.60],
                rmsd=[9.58,1.61,7.48,0.29,1.68,3.52,3.34,8.17,4.31,2.85,6.28,8.78,0.41,6.29,4.89,7.30,4.26,3.51,3.38,0.04,2.21,0.24,7.58,8.40],
                class_rmsd= [False,True, False,True,True,False,False,False,False,False,False,False,True, False,False,False,False,False,False,True,False,True,False,False],
                class_score=[False,False,False,True,True,True, False,False,True, False,False,False,False,False,True, False,False,False,True, True,False,False,True,True],
                class_wrong=[False,False,False,False,False,False, False,False,False, False,False,False,False,False,False, False,False,False,False, False,False,False,False,False])
    
    mcc = tab.compute_mcc(score_col='score', score_dir='-', class_col='rmsd', class_dir='-', score_cutoff=1.0, class_cutoff=2.0)
    self.assertAlmostEquals(mcc, 0.1490711984)
    mcc = tab.compute_mcc(score_col='class_score', class_col='class_rmsd')
    self.assertAlmostEquals(mcc, 0.1490711984)
    mcc = tab.compute_mcc(score_col='score', score_dir='+', class_col='rmsd', class_dir='+', score_cutoff=1.0, class_cutoff=2.0)
    self.assertAlmostEquals(mcc, 0.1490711984)
    mcc = tab.compute_mcc(score_col='score', score_dir='-', class_col='rmsd', class_dir='+', score_cutoff=1.0, class_cutoff=2.0)
    self.assertAlmostEquals(mcc, -0.1490711984)
    mcc = tab.compute_mcc(score_col='score', score_dir='+', class_col='rmsd', class_dir='-', score_cutoff=1.0, class_cutoff=2.0)
    self.assertAlmostEquals(mcc, -0.1490711984)
    mcc = tab.compute_mcc(score_col='class_wrong', class_col='class_rmsd')
    self.assertEquals(mcc,None)
    

  def testCalcMCCPreclassified(self):
    tab = Tab(['reference', 'prediction1', 'prediction2'],'bbb',
                reference=  [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True,  False, False, True,  False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, True, False, False, True,  False, False, True,  False, False, False, False, False, False, False, False, False, False, True, False, False, True, False, False, False, False, False, False, False, False],
                prediction1=[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True,  False, True, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, True, False, True,  False, False, False, False, False, False],
                prediction2=[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True,  False, False, True,  False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, True, False, False, True,  False, True,  True,  False, False, False, False, False, False, False, False, False, False, True, False, False, True, False, False, False, True,  False, False, False, False])
    mcc = tab.compute_mcc(score_col='prediction1', class_col='reference')
    self.assertAlmostEquals(mcc, 0.538389277)
    mcc = tab.compute_mcc(score_col='prediction2', class_col='reference')
    self.assertAlmostEquals(mcc, 0.882089673321)

  def testTabAsNumpyMatrix(self):
    if not HAS_NUMPY:
      return

    '''
    checks numpy matrix 
    
      first  second  third  fourth
    -------------------------------
     x            3     NA  True
     foo         NA  2.200  False
     NA           9  3.300  False
    '''
    
    tab = fixtures.create_test_table()
    tab.add_col('fourth','b',[True, False, False])
    m = tab.get_numpy_matrix('second')
    mc = np.matrix([[3],[None],[9]])
    self.assertTrue(np.all(m==mc))
    mc = np.matrix([[3],[None],[10]])
    self.assertFalse(np.all(m==mc))
    m = tab.get_numpy_matrix('third')
    mc = np.matrix([[None],[2.200],[3.300]])
    self.assertTrue(np.all(m==mc))
    m = tab.get_numpy_matrix('second','third')
    mc = np.matrix([[3, None],[None, 2.200],[9, 3.300]])
    self.assertTrue(np.all(m==mc))
    m = tab.get_numpy_matrix('third','second')
    mc = np.matrix([[None, 3],[2.200, None],[3.300, 9]])
    self.assertTrue(np.all(m==mc))

    self.assertRaises(TypeError, tab.get_numpy_matrix, 'fourth')
    self.assertRaises(TypeError, tab.get_numpy_matrix, 'first')
    self.assertRaises(RuntimeError, tab.get_numpy_matrix)
    
  def test_can_calculate_optimal_prefactors(self):
    if not HAS_NUMPY:
      return
    tab = Tab(['a','b','c','d','e','f'],
                'ffffff',
                a=[1,2,3,4,5,6,7,8,9],
                b=[2,3,4,5,6,7,8,9,10],
                c=[1,3,2,4,5,6,8,7,9],
                d=[0.1,0.1,0.1,0.2,0.3,0.3,0.4,0.5,0.8],
                e=[1,1,1,1,1,1,1,1,1],
                f=[9,9,9,9,9,9,9,9,9])
    
    pref = tab.optimal_prefactors('c','a','b')
    self.assertAlmostEquals(pref[0],0.799999999)
    self.assertAlmostEquals(pref[1],0.166666666666)
    
    pref = tab.optimal_prefactors('c','b','a')
    self.assertAlmostEquals(pref[0],0.166666666666)
    self.assertAlmostEquals(pref[1],0.799999999)
    
    pref = tab.optimal_prefactors('c','b','a',weights='e')
    self.assertAlmostEquals(pref[0],0.166666666666)
    self.assertAlmostEquals(pref[1],0.799999999)
    
    pref = tab.optimal_prefactors('c','b','a',weights='f')
    self.assertAlmostEquals(pref[0],0.166666666666)
    self.assertAlmostEquals(pref[1],0.799999999)
    
    pref = tab.optimal_prefactors('c','a','b',weights='d')
    self.assertAlmostEquals(pref[0],0.6078825445851)
    self.assertAlmostEquals(pref[1],0.3394613806088)
    
    self.assertRaises(RuntimeError, tab.optimal_prefactors, 'c','a','b',weight='d')
    self.assertRaises(RuntimeError, tab.optimal_prefactors, 'c',weights='d')

  def test_can_smooth_columns_with_gaussians(self):
    tab = Tab(['a','b','c','d','e','f'],'fffffi',
                a=[0.5,1.0,2.0,3.0,2.5,1.0,0.5,2.3,1.0],
                b=[0.5,1.0,2.0,3.0,2.5,1.0,0.5,2.3,1.0],
                c=[0.5,1.0,2.0,3.0,2.5,1.0,0.5,2.3,1.0],
                d=[0.5,1.0,2.0,3.0,2.5,1.0,0.5,2.3,1.0],
                e=[0.5,1.0,2.0,3.0,2.5,1.0,0.5,2.3,1.0],
                f=[2,6,5,3,8,7,4,4,4])

    tab.gaussian_smooth('a')
    tab.gaussian_smooth('b', std=2.0)
    tab.gaussian_smooth('c', padding='wrap')
    tab.gaussian_smooth('d', padding='constant')
    tab.gaussian_smooth('e', padding='constant',c=3.0)
    tab.gaussian_smooth('f')

    ref_list=[]

    ref_list.append([0.74729766,1.20875404,1.93459464,2.39849076,2.11504816,
                     1.42457403,1.20524937,1.41025075,1.3557406])
    ref_list.append([1.23447249,1.41295267,1.65198705,1.79959835,1.78131778,
                     1.64501718,1.49728102,1.40589715,1.37147629])
    ref_list.append([0.9315564,1.24131027,1.93698455,2.39855767,2.11504816,
                     1.42450711,1.20285946,1.37769451,1.17148186])
    ref_list.append([0.5630556,1.17705895,1.93224488,2.39842384,2.11504816,
                     1.4244402,1.2005097,1.34599942,0.9872398 ])
    ref_list.append([1.46464039,1.35272941,1.94594196,2.39882533,2.11504816,
                     1.42484169,1.21420677,1.52166988,1.88882459])
    ref_list.append([3,4,4,5,6,6,4,4,4])

    tab_list=[[],[],[],[],[],[]]
    
    for row in tab.rows:
      for i,v in enumerate(row):
        tab_list[i].append(v)

    for i in range(len(ref_list[0])):
      self.assertAlmostEquals(tab_list[0][i],ref_list[0][i])
      self.assertAlmostEquals(tab_list[1][i],ref_list[1][i])
      self.assertAlmostEquals(tab_list[2][i],ref_list[2][i])
      self.assertAlmostEquals(tab_list[3][i],ref_list[3][i])
      self.assertAlmostEquals(tab_list[4][i],ref_list[4][i])
      self.assertAlmostEquals(tab_list[5][i],ref_list[5][i])
     

  def test_table_is_empty(self):
    tab = Tab()
    self.assertTrue(tab.empty())
    self.assertTrue(tab.empty(ignore_nan=False))
    self.assertRaises(ValueError, tab.empty, 'a')
    
    # empty table
    tab = Tab(['a','b','c'], 'fff')
    self.assertTrue(tab.empty())
    self.assertTrue(tab.empty('a'))
    self.assertTrue(tab.empty('b'))
    self.assertTrue(tab.empty('c'))
    self.assertTrue(tab.empty(ignore_nan=False))
    self.assertTrue(tab.empty('a', ignore_nan=False))
    self.assertTrue(tab.empty('b', ignore_nan=False))
    self.assertTrue(tab.empty('c', ignore_nan=False))
    self.assertRaises(ValueError, tab.empty, 'd')
    
    # fill row with NAN values
    tab.add_row([None,None,None])
    self.assertTrue(tab.empty())
    self.assertTrue(tab.empty('a'))
    self.assertTrue(tab.empty('b'))
    self.assertTrue(tab.empty('c'))
    self.assertFalse(tab.empty(ignore_nan=False))
    self.assertFalse(tab.empty('a', ignore_nan=False))
    self.assertFalse(tab.empty('b', ignore_nan=False))
    self.assertFalse(tab.empty('c', ignore_nan=False))
    
    # fill some values into column 'c' only
    tab.add_row([None,None,1.0])
    self.assertFalse(tab.empty())
    self.assertTrue(tab.empty('a'))
    self.assertTrue(tab.empty('b'))
    self.assertFalse(tab.empty('c'))
    self.assertFalse(tab.empty('a', ignore_nan=False))
    self.assertFalse(tab.empty('b', ignore_nan=False))
    self.assertFalse(tab.empty('c', ignore_nan=False))
    
    # fill some values into all columns
    tab.add_row([2.0,3.0,1.0])
    self.assertFalse(tab.empty())
    self.assertFalse(tab.empty('a'))
    self.assertFalse(tab.empty('b'))
    self.assertFalse(tab.empty('c'))
    self.assertFalse(tab.empty('a', ignore_nan=False))
    self.assertFalse(tab.empty('b', ignore_nan=False))
    self.assertFalse(tab.empty('c', ignore_nan=False))
    
  def testUnique(self):
    tab = fixtures.create_test_table()
    tab.add_row(['foo',4, 3.3])
    tab.add_row([None,5, 6.3])
    self.assertEquals(tab.get_unique('first'), ['x','foo'])
    self.assertEquals(tab.get_unique('first', ignore_nan=False), ['x','foo', None])
    self.assertEquals(tab.get_unique('second'), [3,9,4,5])
    self.assertEquals(tab.get_unique('second', ignore_nan=False), [3,None,9,4,5])
    self.assertEquals(tab.get_unique('third'), [2.2, 3.3, 6.3])
    self.assertEquals(tab.get_unique('third', ignore_nan=False), [None, 2.2, 3.3, 6.3])
    
  def testcorrel(self):
    tab = fixtures.create_test_table()
    self.assertEquals(tab.correl('second','third'), None)
    tab.add_row(['foo',4, 3.3])
    tab.add_row([None,5, 6.3])
    tab.add_row([None,8, 2])
    self.assertAlmostEquals(tab.correl('second','third'), -0.4954982578)
    
  def testspearman_correl(self):
    if not HAS_SCIPY:
      return
    tab = fixtures.create_test_table()
    self.assertEquals(tab.spearman_correl('second','third'), None)
    tab.add_row(['foo',4, 3.3])
    tab.add_row([None,5, 6.3])
    tab.add_row([None,8, 2])
    self.assertAlmostEquals(tab.spearman_correl('second','third'), -0.316227766)
    
  def testextend(self):
    '''
     first  second  third 
    ----------------------
     x            3     NA
     foo         NA  2.200
     NA           9  3.300
    '''
    
    # simple extend of the same table
    tab = fixtures.create_test_table()
    self.compare_data_from_dict(tab, {'first': ['x','foo',None],
                                   'second': [3,None,9],
                                   'third': [None,2.2,3.3]})
    
    tab.extend(tab)
    self.compare_data_from_dict(tab, {'first': ['x','foo',None,'x','foo',None],
                                   'second': [3,None,9,3,None,9],
                                   'third': [None,2.2,3.3,None,2.2,3.3]})
    
    # simple extend of different tables with the same data
    tab = fixtures.create_test_table()
    tab2 = fixtures.create_test_table()
    tab.extend(tab2)
    self.compare_data_from_dict(tab, {'first': ['x','foo',None,'x','foo',None],
                                   'second': [3,None,9,3,None,9],
                                   'third': [None,2.2,3.3,None,2.2,3.3]})
    self.compare_data_from_dict(tab2, {'first': ['x','foo',None],
                                    'second': [3,None,9],
                                    'third': [None,2.2,3.3]})
    
    # add additional columns to current table
    tab = fixtures.create_test_table()
    tab2 = fixtures.create_test_table()
    tab2.add_col('foo','i',[1,2,3])
    tab.extend(tab2)
    self.compare_data_from_dict(tab, {'first': ['x','foo',None,'x','foo',None],
                                   'second': [3,None,9,3,None,9],
                                   'third': [None,2.2,3.3,None,2.2,3.3],
                                   'foo': [None,None,None,1,2,3]})     
    
    # different order of the data
    tab = fixtures.create_test_table()
    tab2 = Tab(['third','second','first'],
                  'fis',
                  third=[None,2.2,3.3],
                  first=['x','foo',None],
                  second=[3, None, 9])
    self.compare_data_from_dict(tab2, {'first': ['x','foo',None],
                                    'second': [3,None,9],
                                    'third': [None,2.2,3.3]})
    tab.extend(tab2)
    self.compare_data_from_dict(tab, {'first': ['x','foo',None,'x','foo',None],
                                   'second': [3,None,9,3,None,9],
                                   'third': [None,2.2,3.3,None,2.2,3.3]})
    
    # with overwrite (additional column)
    tab = fixtures.create_test_table()
    tab2 = fixtures.create_test_table()
    tab2.add_col('foo','i',[1,2,3])
    tab.extend(tab2, overwrite='first')
    self.compare_data_from_dict(tab, {'first': ['x','foo',None],
                                   'second': [3,None,9],
                                   'third': [None,2.2,3.3],
                                   'foo': [1,2,3]})
    
    # with overwrite (no matching value)
    tab = fixtures.create_test_table()
    tab2 = Tab(['third','second','first'],
                  'fis',
                  third=[None,2.2,3.3],
                  first=['a','bar','bla'],
                  second=[3, None, 9])
    tab.extend(tab2, overwrite='first')
    self.compare_data_from_dict(tab, {'first': ['x','foo',None,'a','bar','bla'],
                                   'second': [3,None,9,3,None,9],
                                   'third': [None,2.2,3.3,None,2.2,3.3]})
    
    # with overwrite (with matching values)
    tab = fixtures.create_test_table()
    tab2 = Tab(['third','second','first'],
                  'fis',
                  third=[None,2.2,3.4],
                  first=['a','bar','bla'],
                  second=[3, None, 9])
    tab.extend(tab2, overwrite='third')
    self.compare_data_from_dict(tab, {'first': ['a','bar',None,'bla'],
                                   'second': [3,None,9,9],
                                   'third': [None,2.2,3.3,3.4]})
    
    # cannot extend if types are different
    tab = Tab('aaa','s',a=['a','b'])
    tab2 = Tab('aaa','i',a=[1,2])
    self.assertRaises(TypeError, tab.extend, tab2)
    
if __name__ == "__main__":
  from ost import testutils
  testutils.RunTests()
