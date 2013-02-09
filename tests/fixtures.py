from tap import Tab

def create_test_table():
  '''
  creates a table with some test data
  
    first  second  third 
  ----------------------
    x            3     NA
    foo         NA  2.200
    NA           9  3.300

  '''
  tab = Tab()
  tab.add_col('first', 'string')
  tab.add_col('second', 'int')
  tab.add_col('third', 'float')
  tab.add_row(['x',3, None], overwrite=None)
  tab.add_row(['foo',None, 2.2], overwrite=None)
  tab.add_row([None,9, 3.3], overwrite=None)
  return tab

