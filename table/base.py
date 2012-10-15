import csv
import re
import math
import itertools
import operator
import cPickle
from stutil import median, mean, std_dev, correl
import typeutil



class BinaryColExpr:
  def __init__(self, op, lhs, rhs):
    self.op=op
    self.lhs=lhs
    self.rhs=rhs
    if typeutil.is_scalar(lhs):
      self.lhs=itertools.cyle([self.lhs])
    if typeutil.is_scalar(rhs):
      self.rhs=itertools.cycle([self.rhs])
  def __iter__(self):
    for l, r in zip(self.lhs, self.rhs):
      if l!=None and r!=None:
        yield self.op(l, r)
      else:
        yield None
  def __add__(self, rhs):
    return BinaryColExpr(operator.add, self, rhs)

  def __sub__(self, rhs):
    return BinaryColExpr(operator.sub, self, rhs)

  def __mul__(self, rhs):
    return BinaryColExpr(operator.mul, self, rhs)

  def __div__(self, rhs):
    return BinaryColExpr(operator.div, self, rhs)

class TableCol:
  def __init__(self, table, col):
    self._table=table
    if type(col)==str:
      self.col_index=self._table.col_index(col)
    else:
      self.col_index=col

  def __iter__(self):
    for row in self._table.rows:
      yield row[self.col_index]

  def __len__(self):
    return len(self._table.rows)

  def __getitem__(self, index):
    return self._table.rows[index][self.col_index]

  def __setitem__(self, index, value):
    self._table.rows[index][self.col_index]=value
  
  def __add__(self, rhs):
    return BinaryColExpr(operator.add, self, rhs)

  def __sub__(self, rhs):
    return BinaryColExpr(operator.sub, self, rhs)

  def __mul__(self, rhs):
    return BinaryColExpr(operator.mul, self, rhs)

  def __div__(self, rhs):
    return BinaryColExpr(operator.div, self, rhs)


class Table(object):
  """
  
  The table class provides convenient access to data in tabular form. An empty 
  table can be easily constructed as follows
  
  .. code-block:: python
  
    tab=Table()
    
  If you want to add columns directly when creating the table, column names
  and *column types* can be specified as follows
  
  .. code-block:: python
  
    tab=Table(['nameX','nameY','nameZ'], 'sfb')
    
  this will create three columns called nameX, nameY and nameZ of type string,
  float and bool, respectively. There will be no data in the table and thus,
  the table will not contain any rows.
  
  The following *column types* are supported:
  
  ======= ========
  name     abbrev
  ======= ========
  string     s
  float      f
  int        i
  bool       b
  ======= ========
  
  If you want to add data to the table in addition, use the following:
  
  .. code-block:: python
  
    tab=Table(['nameX','nameY','nameZ'],
              'sfb',
              nameX=['a','b','c'],
              nameY=[0.1, 1.2, 3.414],
              nameZ=[True, False, False])
              
  if values for one column is left out, they will be filled with NA, but if
  values are specified, all values must be specified (i.e. same number of
  values per column)
    
  """

  SUPPORTED_TYPES=('int', 'float', 'bool', 'string',)
  
  
  def __init__(self, col_names=None, col_types=None, **kwargs):
    self.col_names=col_names
    self.comment=''
    self.name=''
    
    self.col_types = self._parse_col_types(col_types)
    self.rows=[]    
    if len(kwargs)>=0:
      if not col_names:
        self.col_names=[v for v in kwargs.keys()]
      if not self.col_types:
        self.col_types=['string' for u in range(len(self.col_names))]
      if len(kwargs)>0:
        self._add_rows_from_dict(kwargs)

  def __getattr__(self, col_name):
    # pickling doesn't call the standard __init__ defined above and thus
    # col_names might not be defined. This leads to infinite recursions.
    # Protect against it by checking that col_names is contained in 
    # __dict__
    if 'col_names' not in self.__dict__ or col_name not in self.col_names:
      raise AttributeError(col_name)
    return TableCol(self, col_name)

  @staticmethod
  def _parse_col_types(types, exp_num=None):
    if types==None:
      return None
    
    short2long = {'s' : 'string', 'i': 'int', 'b' : 'bool', 'f' : 'float'}
    allowed_short = short2long.keys()
    allowed_long = short2long.values()
    
    type_list = []
    
    # string type
    if typeutil.is_scalar(types):
      if type(types)==str:
        types = types.lower()
        
        # single value
        if types in allowed_long:
          type_list.append(types)
        elif types in allowed_short:
          type_list.append(short2long[types])
        
        # comma separated list of long or short types
        elif types.find(',')!=-1:
          for t in types.split(','):
            if t in allowed_long:
              type_list.append(t)
            elif t in allowed_short:
              type_list.append(short2long[t])
            else:
              raise ValueError('Unknown type %s in types %s'%(t,types))
        
        # string of short types
        else:
          for t in types:
            if t in allowed_short:
              type_list.append(short2long[t])
            else:
              raise ValueError('Unknown type %s in types %s'%(t,types))
      
      # non-string type
      else:
        raise ValueError('Col type %s must be string or list'%types)
    
    # list type
    else:
      for t in types:
        # must be string type
        if type(t)==str:
          t = t.lower()
          if t in allowed_long:
            type_list.append(t)
          elif t in allowed_short:
            type_list.append(short2long[t])
          else:
            raise ValueError('Unknown type %s in types %s'%(t,types))
        
        # non-string type
        else:
          raise ValueError('Col type %s must be string or list'%types)
    
    if exp_num:
      if len(type_list)!=exp_num:
        raise ValueError('Parsed number of col types (%i) differs from ' + \
                         'expected (%i) in types %s'%(len(type_list),exp_num,types))
      
    return type_list

  def set_name(self, name):
    '''
    Set name of the table
    :param name: name
    :type name: :class:`str`
    '''
    self.name = name
    
  def get_name(self):
    '''
    Get name of table
    '''
    return self.name

  def rename_col(self, old_name, new_name):
    """
    Rename column *old_name* to *new_name*.

    :param old_name: Name of the old column
    :param new_name: Name of the new column
    :raises: :exc:`ValueError` when *old_name* is not a valid column
    """
    if old_name==new_name:
      return
    self.add_col(new_name, self.col_types[self.col_index(old_name)],
                self[old_name])
    self.remove_col(old_name)

  def col_index(self, col):
    '''
    Returns the column index for the column with the given name.

    :raises: ValueError if no column with the name is found
    '''
    if col not in self.col_names:
      raise ValueError('Table has no column named "%s"' % col)
    return self.col_names.index(col)
  
  def get_col_names(self):
    '''
    Returns a list containing all column names.
    '''
    return self.col_names
  
  def search_col_names(self, regex):
    '''
    Returns a list of column names matching the regex

    :param regex: regex pattern
    :type regex: :class:`str`

    :returns: :class:`list` of column names (:class:`str`)
    '''
    matching_names = []
    for name in self.col_names:
      matches = re.search(regex, name)
      if matches:
        matching_names.append(name)
    return matching_names

  def has_col(self, col):
    '''
    Checks if the column with a given name is present in the table.
    '''
    return col in self.col_names
  
  def __getitem__(self, k):
    if type(k)==int:
      return TableCol(self, self.col_names[k])
    else:
      return TableCol(self, k)

  def __setitem__(self, k, value):
    col_index=k
    if type(k)!=int:
      col_index=self.col_index(k)
    if typeutil.is_scalar(value):
      value=itertools.cycle([value])
    for r, v in zip(self.rows, value):
      r[col_index]=v

  def to_string(self, float_format='%.3f', int_format='%d', rows=None):
    '''
    Convert the table into a string representation.

    The output format can be modified for int and float type columns by
    specifying a formatting string for the parameters 'float_format' and
    'int_format'.

    The option 'rows' specify the range of rows to be printed. The parameter
    must be a type that supports indexing (e.g. a :class:`list`) containing the 
    start and end row *index*, e.g. [start_row_idx, end_row_idx].

    :param float_format: formatting string for float columns
    :type float_format: :class:`str`

    :param int_format: formatting string for int columns
    :type int_format: :class:`str`

    :param rows: iterable containing start and end row *index*
    :type rows: iterable containing :class:`ints <int>`
    '''
    widths=[len(cn) for cn in self.col_names]
    sel_rows=self.rows
    if rows:
      sel_rows=self.rows[rows[0]:rows[1]]
    for row in sel_rows:
      for i, (ty, col) in enumerate(zip(self.col_types, row)):
        if col==None:
          widths[i]=max(widths[i], len('NA'))
        elif ty=='float':
          widths[i]=max(widths[i], len(float_format % col))
        elif ty=='int':
          widths[i]=max(widths[i], len(int_format % col))
        else:
          widths[i]=max(widths[i], len(str(col)))
    s=''
    if self.comment:
      s+=''.join(['# %s\n' % l for l in self.comment.split('\n')])
    total_width=sum(widths)+2*len(widths)
    for width, col_name in zip(widths, self.col_names):
      s+=col_name.center(width+2)
    s+='\n%s\n' % ('-'*total_width)
    for row in sel_rows:
      for width, ty, col in zip(widths, self.col_types, row):
        cs=''
        if col==None:
          cs='NA'.center(width+2)
        elif ty=='float':
          cs=(float_format % col).rjust(width+2)
        elif ty=='int':
          cs=(int_format % col).rjust(width+2)
        else:
          cs=' '+str(col).ljust(width+1)
        s+=cs
      s+='\n'
    return s

  def __str__(self):
    return self.to_string()
  
  def stats(self, col):
     idx  = self.col_index(col)
     text ='''
Statistics for column %(col)s

  Number of Rows         : %(num)d
  Number of Rows Not None: %(num_non_null)d 
  mean                   : %(mean)f
  median                 : %(median)f
  Standard Deviation     : %(stddev)f
  min                    : %(min)f
  max                    : %(max)f
'''
     data = {
       'col' : col,
       'num' : len(self.rows),
       'num_non_null' : self.count(col),
       'median' : self.median(col),
       'mean' : self.mean(col),
       'stddev' : self.std_dev(col),
       'min' : self.min(col),
       'max' : self.max(col),
     }
     return text % data

  def _add_rows_from_dict(self, d, overwrite=None):
    '''
    Add one or more rows from a :class:`dictionary <dict>`.
    
    If *overwrite* is not None and set to an existing column name, the specified 
    column in the table is searched for the first occurrence of a value matching
    the value of the column with the same name in the dictionary. If a matching
    value is found, the row is overwritten with the dictionary. If no matching
    row is found, a new row is appended to the table.

    :param d: dictionary containing the data
    :type d: :class:`dict`

    :param overwrite: column name to overwrite existing row if value in
                      column *overwrite* matches
    :type overwrite: :class:`str`

    :raises: :class:`ValueError` if multiple rows are added but the number of
             data items is different for different columns.
    '''
    # get column indices
    idxs = [self.col_index(k) for k in d.keys()]
    
    # convert scalar values to list
    old_len = None
    for k,v in d.iteritems():
      if typeutil.is_scalar(v):
        v = [v]
        d[k] = v
      if not old_len:
        old_len = len(v)
      elif old_len!=len(v):
        raise ValueError("Cannot add rows: length of data must be equal " + \
                         "for all columns in %s"%str(d))
    
    # convert column based dict to row based dict and create row and add data
    for i,data in enumerate(zip(*d.values())):
      new_row = [None for a in range(len(self.col_names))]
      for idx,v in zip(idxs,data):
        new_row[idx] = typeutil.coerce(v, self.col_types[idx])
        
      # partially overwrite existing row with new data
      if overwrite:
        overwrite_idx = self.col_index(overwrite)
        added = False
        for i,r in enumerate(self.rows):
          if r[overwrite_idx]==new_row[overwrite_idx]:
            for j,e in enumerate(self.rows[i]):
              if new_row[j]==None:
                new_row[j] = e
            self.rows[i] = new_row
            added = True
            break
          
      # if not overwrite or overwrite did not find appropriate row
      if not overwrite or not added:
        self.rows.append(new_row)
      
  def paired_t_test(self, col_a, col_b):
    """
    Two-sided test for the null-hypothesis that two related samples 
    have the same average (expected values)
    
    :param col_a: First column
    :param col_b: Second column

    :returns: P-value  between 0 and 1 that the two columns have the 
       same average. The smaller the value, the less related the two
       columns are.
    """
    from scipy.stats import ttest_rel
    xs = []
    ys = []
    for x, y in self.zip(col_a, col_b):
      if x!=None and y!=None:
        xs.append(x)
        ys.append(y)
    result = ttest_rel(xs, ys)
    return result[1]

  def add_row(self, data, overwrite=None):
    """
    Add a row to the table.
    
    *data* may either be a dictionary or a list-like object:

     - If *data* is a dictionary the keys in the dictionary must match the
       column names. Columns not found in the dict will be initialized to None.
       If the dict contains list-like objects, multiple rows will be added, if
       the number of items in all list-like objects is the same, otherwise a
       :class:`ValueError` is raised.

     - If *data* is a list-like object, the row is initialized from the values
       in *data*. The number of items in *data* must match the number of
       columns in the table. A :class:`ValuerError` is raised otherwise. The
       values are added in the order specified in the list, thus, the order of
       the data must match the columns.
          
    If *overwrite* is not None and set to an existing column name, the specified 
    column in the table is searched for the first occurrence of a value matching
    the value of the column with the same name in the dictionary. If a matching
    value is found, the row is overwritten with the dictionary. If no matching
    row is found, a new row is appended to the table.

    :param data: data to add
    :type data: :class:`dict` or *list-like* object

    :param overwrite: column name to overwrite existing row if value in
                      column *overwrite* matches
    :type overwrite: :class:`str`

    :raises: :class:`ValueError` if *list-like* object is used and number of
             items does *not* match number of columns in table.

    :raises: :class:`ValueError` if *dict* is used and multiple rows are added
             but the number of data items is different for different columns.

    **Example:** add multiple data rows to a subset of columns using a dictionary

    .. code-block:: python

      # create table with three float columns
      tab = Table(['x','y','z'], 'fff')

      # add rows from dict
      data = {'x': [1.2, 1.6], 'z': [1.6, 5.3]}
      tab.add_row(data)
      print tab

      '''
      will produce the table

      ====  ====  ====
      x     y     z
      ====  ====  ====
      1.20  NA    1.60
      1.60  NA    5.30
      ====  ====  ====
      '''

      # overwrite the row with x=1.2 and add row with x=1.9
      data = {'x': [1.2, 1.9], 'z': [7.9, 3.5]}
      tab.add_row(data, overwrite='x')
      print tab

      '''
      will produce the table

      ====  ====  ====
      x     y     z
      ====  ====  ====
      1.20  NA    7.90
      1.60  NA    5.30
      1.90  NA    3.50
      ====  ====  ====
      '''
    """
    if type(data)==dict:
      self._add_rows_from_dict(data, overwrite)
    else:
      if len(data)!=len(self.col_names):
        msg='data array must have %d elements, not %d'
        raise ValueError(msg % (len(self.col_names), len(data)))
      new_row = [typeutil.coerce(v, t) for v, t in zip(data, self.col_types)]
      
      # fully overwrite existing row with new data
      if overwrite:
        overwrite_idx = self.col_index(overwrite)
        added = False
        for i,r in enumerate(self.rows):
          if r[overwrite_idx]==new_row[overwrite_idx]:
            self.rows[i] = new_row
            added = True
            break
      
      # if not overwrite or overwrite did not find appropriate row
      if not overwrite or not added:
        self.rows.append(new_row)

  def remove_col(self, col):
    """
    Remove column with the given name from the table

    :param col: name of column to remove
    :type col: :class:`str`
    """
    idx = self.col_index(col)
    del self.col_names[idx]
    del self.col_types[idx]
    for row in self.rows:
      del row[idx]

  def add_col(self, col_name, col_type, data=None):
    """
    Add a column to the right of the table.
    
    :param col_name: name of new column
    :type col_name: :class:`str`

    :param col_type: type of new column (long versions: *int*, *float*, *bool*,
                     *string* or short versions: *i*, *f*, *b*, *s*)
    :type col_type: :class:`str`

    :param data: data to add to new column.
    :type data: scalar or iterable

    **Example:**

    .. code-block:: python
    
      tab=Table(['x'], 'f', x=range(5))
      tab.add_col('even', 'bool', itertools.cycle([True, False]))
      print tab
    
      '''
      will produce the table

      ====  ====
      x     even
      ====  ====
        0   True
        1   False
        2   True
        3   False
        4   True
      ====  ====
      '''

    If data is a constant instead of an iterable object, it's value
    will be written into each row:

    .. code-block:: python

      tab=Table(['x'], 'f', x=range(5))
      tab.add_col('num', 'i', 1)
      print tab

      '''
      will produce the table

      ====  ====
      x     num
      ====  ====
        0   1
        1   1
        2   1
        3   1
        4   1
      ====  ====
      '''
    
    As a special case, if there are no previous rows, and data is not 
    None, rows are added for every item in data.
    """

    if col_name in self.col_names:
      raise ValueError('Column with name %s already exists'%col_name)

    col_type = self._parse_col_types(col_type, exp_num=1)[0]
    self.col_names.append(col_name)
    self.col_types.append(col_type)

    if len(self.rows)>0:
      if typeutil.is_scalar(data):
        for row in self.rows:
          row.append(data)
      else:
        if hasattr(data, '__len__') and len(data)!=len(self.rows):
          self.col_names.pop()
          self.col_types.pop()
          raise ValueError('Length of data (%i) must correspond to number of '%len(data) +\
                           'existing rows (%i)'%len(self.rows))
        for row, d in zip(self.rows, data):
          row.append(d)

    elif data!=None and len(self.col_names)==1:
      if typeutil.is_scalar(data):
        self.add_row({col_name : data})
      else:
        for v in data:
          self.add_row({col_name : v})

  def filter(self, *args, **kwargs):
    """
    Returns a filtered table only containing rows matching all the predicates 
    in kwargs and args For example,
    
    .. code-block:: python
    
      tab.filter(town='Basel')
    
    will return all the rows where the value of the column "town" is equal to 
    "Basel". Several predicates may be combined, i.e.
    
    .. code-block:: python
    
      tab.filter(town='Basel', male=True)
      
    will return the rows with "town" equal to "Basel" and "male" equal to true.
    args are unary callables returning true if the row should be included in the
    result and false if not.
    """
    filt_tab=Table(list(self.col_names), list(self.col_types))
    for row in self.rows:
      matches=True
      for func in args:
        if not func(row):
          matches=False
          break
      for key, val in kwargs.iteritems():
        if row[self.col_index(key)]!=val:
          matches=False
          break
      if matches:
        filt_tab.add_row(row)
    return filt_tab

  @staticmethod
  def _load_ost(stream_or_filename):
    fieldname_pattern=re.compile(r'(?P<name>[^[]+)(\[(?P<type>\w+)\])?')
    values_pattern=re.compile("([^\" ]+|\"[^\"]*\")+")
    if not hasattr(stream_or_filename, 'read'):
      stream=open(stream_or_filename, 'r')
    else:
      stream=stream_or_filename
    header=False
    num_lines=0
    for line in stream:
      line=line.strip()
      if line.startswith('#'):
        continue
      if len(line)==0:
        continue
      num_lines+=1
      if not header:
        fieldnames=[]
        fieldtypes=[]
        for col in line.split():
          match=fieldname_pattern.match(col)
          if match:
            if match.group('type'):
              fieldtypes.append(match.group('type'))
            else:
              fieldtypes.append('string')
            fieldnames.append(match.group('name'))
        tab=Table(fieldnames, fieldtypes)
        header=True
        continue
      tab.add_row([x.strip('"') for x in values_pattern.findall(line)])
    if num_lines==0:
      raise IOError("Cannot read table from empty stream")
    return tab

  def _guess_col_types(self):
    for col_idx in range(len(self.col_names)):
      self.col_types[col_idx]=typeutil.guess_col_type(self[self.col_names[col_idx]])
    for row in self.rows:
      for idx in range(len(row)):
        row[idx]=typeutil.coerce(row[idx], self.col_types[idx])
        
  @staticmethod
  def _load_csv(stream_or_filename, sep):
    if not hasattr(stream_or_filename, 'read'):
      stream=open(stream_or_filename, 'r')
    else:
      stream=stream_or_filename
    reader=csv.reader(stream, delimiter=sep)
    first=True
    for row in reader:
      if first:
        header=row
        types='s'*len(row)
        tab=Table(header, types)
        first=False
      else:
        tab.add_row(row)
    if first:
      raise IOError('trying to load table from empty CSV stream/file')

    tab._guess_col_types()
    return tab

  @staticmethod
  def _load_pickle(stream_or_filename):
    if not hasattr(stream_or_filename, 'read'):
      stream=open(stream_or_filename, 'rb')
    else:
      stream=stream_or_filename
    return cPickle.load(stream)

  @staticmethod
  def _guess_format(filename):
    try:
      filename = filename.name
    except AttributeError, e:
      pass
    if filename.endswith('.csv'):
      return 'csv'
    elif filename.endswith('.pickle'):
      return 'pickle'
    else:
      return 'ost'
    
    
  @staticmethod
  def load(stream_or_filename, format='auto', sep=','):
    """
    load table from stream or file with given name.

    By default, the file format is set to *auto*, which tries to guess the file
    format from the file extension. The following file extensions are
    recognized:
    
    ============    ======================
    extension       recognized format
    ============    ======================
    .csv            comma separated values
    .pickle         pickled byte stream
    <all others>    ost-specific format
    ============    ======================
    
    Thus, *format* must be specified for reading file with different filename
    extensions.

    The following file formats are understood:

    - ost

      This is an ost-specific, but still human readable file format. The file
      (stream) must start with header line of the form

        col_name1[type1] <col_name2[type2]>...

      The types given in brackets must be one of the data types the
      :class:`Table` class understands. Each following line in the file then must
      contains exactly the same number of data items as listed in the header. The
      data items are automatically converted to the column format. Lines starting
      with a '#' and empty lines are ignored.

    - pickle

      Deserializes the table from a pickled byte stream

    - csv

      Reads the table from comma separated values stream. Since there is no
      explicit type information in the csv file, the column types are guessed,
      using the following simple rules:

      * if all values are either NA/NULL/NONE the type is set to string
      * if all non-null values are convertible to float/int the type is set to
        float/int
      * if all non-null values are true/false/yes/no, the value is set to bool
      * for all other cases, the column type is set to string

    :returns: A new :class:`Table` instance
    """
    format=format.lower()
    if format=='auto':
      format = Table._guess_format(stream_or_filename)
      
    if format=='ost':
      return Table._load_ost(stream_or_filename)
    if format=='csv':
      return Table._load_csv(stream_or_filename, sep=sep)
    if format=='pickle':
      return Table._load_pickle(stream_or_filename)
    raise ValueError('unknown format ""' % format)

  def sort(self, by, order='+'):
    """
    Performs an in-place sort of the table, based on column *by*.

    :param by: column name by which to sort
    :type by: :class:`str`

    :param order: ascending (``-``) or descending (``+``) order
    :type order: :class:`str` (i.e. *+*, *-*)
    """
    sign=-1
    if order=='-':
      sign=1
    key_index=self.col_index(by)
    def _key_cmp(lhs, rhs):
      return sign*cmp(lhs[key_index], rhs[key_index])
    self.rows=sorted(self.rows, _key_cmp)
    
  def get_unique(self, col, ignore_nan=True):
    """
    Extract a list of all unique values from one column

    :param col: column name
    :type col: :class:`str`

    :param ignore_nan: ignore all *None* values
    :type ignore_nan: :class:`bool`
    """
    idx = self.col_index(col)
    seen = {}
    result = []
    for row in self.rows:
      item = row[idx]
      if item!=None or ignore_nan==False:
        if item in seen: continue
        seen[item] = 1
        result.append(item)
    return result
    
  def zip(self, *args):
    """
    Allows to conveniently iterate over a selection of columns, e.g.
    
    .. code-block:: python
    
      tab=Table.load('...')
      for col1, col2 in tab.zip('col1', 'col2'):
        print col1, col2
    
    is a shortcut for
    
    .. code-block:: python
    
      tab=Table.load('...')
      for col1, col2 in zip(tab['col1'], tab['col2']):
        print col1, col2
    """
    return zip(*[self[arg] for arg in args])


  def zip_non_null(self, *args):
    """
    Same as :meth:`zip`, but only returns rows where none of the values 
    is None.
    """
    for vals in self.zip(*args):
      if None not in vals:
        yield vals

  def _max(self, col):
    if len(self.rows)==0:
      return None, None
    idx = self.col_index(col)
    col_type = self.col_types[idx]
    if col_type=='int' or col_type=='float':
      max_val = -float('inf')
    elif col_type=='bool':
      max_val = False
    elif col_type=='string':
      max_val = chr(0)
    max_idx = None
    for i in range(0, len(self.rows)):
      if self.rows[i][idx]>max_val:
        max_val = self.rows[i][idx]
        max_idx = i
    return max_val, max_idx

        
  def max_row(self, col):
    """
    Returns the row containing the cell with the maximal value in col. If 
    several rows have the highest value, only the first one is returned.
    None values are ignored.

    :param col: column name
    :type col: :class:`str`

    :returns: row with maximal col value or None if the table is empty
    """
    val, idx = self._max(col)
    if idx!=None:
      return self.rows[idx]
  
  def max(self, col):
    """
    Returns the maximum value in col. If several rows have the highest value,
    only the first one is returned. None values are ignored.

    :param col: column name
    :type col: :class:`str`
    """
    val, idx = self._max(col)
    return val
  
  def max_idx(self, col):
    """
    Returns the row index of the cell with the maximal value in col. If
    several rows have the highest value, only the first one is returned.
    None values are ignored.

    :param col: column name
    :type col: :class:`str`
    """
    val, idx = self._max(col)
    return idx
  
  def _min(self, col):
    if len(self.rows)==0:
      return None, None
    idx=self.col_index(col)
    col_type = self.col_types[idx]
    if col_type=='int' or col_type=='float':
      min_val=float('inf')
    elif col_type=='bool':
      min_val=True
    elif col_type=='string':
      min_val=chr(255)
    min_idx=None
    for i,row in enumerate(self.rows):
      if row[idx]!=None and row[idx]<min_val:
        min_val=row[idx]
        min_idx=i
    return min_val, min_idx

  def min(self, col):
    """
    Returns the minimal value in col. If several rows have the lowest value,
    only the first one is returned. None values are ignored.

    :param col: column name
    :type col: :class:`str`
    """
    val, idx = self._min(col)
    return val
  
  def min_row(self, col):
    """
    Returns the row containing the cell with the minimal value in col. If 
    several rows have the lowest value, only the first one is returned.
    None values are ignored.

    :param col: column name
    :type col: :class:`str`

    :returns: row with minimal col value or None if the table is empty
    """
    val, idx = self._min(col)
    if idx!=None:
      return self.rows[idx]
  
  def min_idx(self, col):
    """
    Returns the row index of the cell with the minimal value in col. If
    several rows have the lowest value, only the first one is returned.
    None values are ignored.

    :param col: column name
    :type col: :class:`str`
    """
    val, idx = self._min(col)
    return idx
  
  def sum(self, col):
    """
    Returns the sum of the given column. Cells with None are ignored. Returns 
    0.0, if the column doesn't contain any elements. Col must be of numeric
    column type ('float', 'int') or boolean column type.

    :param col: column name
    :type col: :class:`str`

    :raises: :class:`TypeError` if column type is ``string``
    """
    idx = self.col_index(col)
    col_type = self.col_types[idx]
    if col_type!='int' and col_type!='float' and col_type!='bool':
      raise TypeError("sum can only be used on numeric column types")
    s = 0.0
    for r in self.rows:
      if r[idx]!=None:
        s += r[idx] 
    return s 

  def mean(self, col):
    """
    Returns the mean of the given column. Cells with None are ignored. Returns 
    None, if the column doesn't contain any elements. Col must be of numeric
    ('float', 'int') or boolean column type.

    If column type is *bool*, the function returns the ratio of
    number of 'Trues' by total number of elements.

    :param col: column name
    :type col: :class:`str`

    :raises: :class:`TypeError` if column type is ``string``
    """
    idx = self.col_index(col)
    col_type = self.col_types[idx]
    if col_type!='int' and col_type!='float' and col_type!='bool':
      raise TypeError("mean can only be used on numeric or bool column types")
    
    vals=[]
    for v in self[col]:
      if v!=None:
        vals.append(v)
    try:
      return mean(vals)
    except Exception, e:
      print e
      return None
    
  def row_mean(self, mean_col_name, cols):
    """
    Adds a new column of type 'float' with a specified name (*mean_col_name*),
    containing the mean of all specified columns for each row.
    
    Cols are specified by their names and must be of numeric column
    type ('float', 'int') or boolean column type. Cells with None are ignored.
    Adds None if the row doesn't contain any values.
    
    :param mean_col_name: name of new column containing mean values
    :type mean_col_name: :class:`str`

    :param cols: name or list of names of columns to include in computation of
                 mean
    :type cols: :class:`str` or :class:`list` of strings

    :raises: :class:`TypeError` if column type of columns in *col* is ``string``
    
    == Example ==
   
    Staring with the following table:
    
    ==== ==== ====
    x     y    u           
    ==== ==== ====
     1    10  100 
     2    15  None 
     3    20  400 
    ==== ==== ====
    
    the code here adds a column with the name 'mean' to yield the table below:
    
    .. code-block::python
    
      tab.row_mean('mean', ['x', 'u'])
    
    
    ==== ==== ==== ===== 
    x     y    u   mean           
    ==== ==== ==== =====
     1    10  100  50.5 
     2    15  None 2
     3    20  400  201.5 
    ==== ==== ==== =====
      
    """
    
    if typeutil.is_scalar(cols):
      cols = [cols]
    
    cols_idxs = []
    for col in cols:
      idx = self.col_index(col)
      col_type = self.col_types[idx]
      if col_type!='int' and col_type!='float' and col_type!='bool':
        raise TypeError("row_mean can only be used on numeric column types")
      cols_idxs.append(idx)
      
    mean_rows = []
    for row in self.rows:
      vals = []
      for idx in cols_idxs:
        v = row[idx]
        if v!=None:
          vals.append(v)
      try:
        row_mean = mean(vals)
        mean_rows.append(row_mean)
      except Exception, e:
        print e
        mean_rows.append(None)
    
    self.add_col(mean_col_name, 'f', mean_rows)
    
  def percentiles(self, col, nths):
    """
    returns the percentiles of column *col* given in *nths*.

    The percentils are calculated as 
    
    .. code-block:: python

      values[min(len(values), int(round(len(values)*p/100+0.5)-1))]

    where values are the sorted values of *col* not equal to none
    :param: nths: list of percentiles to be calculated. Each percentil is a number
        between 0 and 100.

    :raises: :class:`TypeError` if column type is ``string``
    :returns: List of percentils in the same order as given in *nths*
    """
    idx = self.col_index(col)
    col_type = self.col_types[idx]
    if col_type!='int' and col_type!='float' and col_type!='bool':
      raise TypeError("median can only be used on numeric column types")
    
    for nth in nths:
      if nth < 0 or nth > 100:
        raise ValueError("percentiles must be between 0 and 100")
    vals=[]
    for v in self[col]:
      if v!=None:
        vals.append(v)
    vals=sorted(vals)
    if len(vals)==0:
      return [None]*len(nths)
    percentiles=[]
    
    for nth in nths:
      p=vals[min(len(vals)-1, int(round(len(vals)*nth/100.0+0.5)-1))]
      percentiles.append(p)
    return percentiles

  def median(self, col):
    """
    Returns the median of the given column. Cells with None are ignored. Returns 
    None, if the column doesn't contain any elements. Col must be of numeric
    column type ('float', 'int') or boolean column type.

    :param col: column name
    :type col: :class:`str`

    :raises: :class:`TypeError` if column type is ``string``
    """
    idx = self.col_index(col)
    col_type = self.col_types[idx]
    if col_type!='int' and col_type!='float' and col_type!='bool':
      raise TypeError("median can only be used on numeric column types")
    
    vals=[]
    for v in self[col]:
      if v!=None:
        vals.append(v)
    try:
      return median(vals)
    except:
      return None
    
  def std_dev(self, col):
    """
    Returns the standard deviation of the given column. Cells with None are
    ignored. Returns None, if the column doesn't contain any elements. Col must
    be of numeric column type ('float', 'int') or boolean column type.

    :param col: column name
    :type col: :class:`str`

    :raises: :class:`TypeError` if column type is ``string``
    """
    idx = self.col_index(col)
    col_type = self.col_types[idx]
    if col_type!='int' and col_type!='float' and col_type!='bool':
      raise TypeError("std_dev can only be used on numeric column types")
    
    vals=[]
    for v in self[col]:
      if v!=None:
        vals.append(v)
    try:
      return std_dev(vals)
    except Exception, e:
      print e
      return None

  def count(self, col, ignore_nan=True):
    """
    count the number of cells in column that are not equal to None.

    :param col: column name
    :type col: :class:`str`

    :param ignore_nan: ignore all *None* values
    :type ignore_nan: :class:`bool`
    """
    count=0
    idx=self.col_index(col)
    for r in self.rows:
      if ignore_nan:
        if r[idx]!=None:
          count+=1
      else:
        count+=1
    return count

  def correl(self, col1, col2):
    """
    Calculate the Pearson correlation coefficient between *col1* and *col2*, only
    taking rows into account where both of the values are not equal to *None*.
    If there are not enough data points to calculate a correlation coefficient,
    *None* is returned.

    :param col1: column name for first column
    :type col1: :class:`str`

    :param col2: column name for second column
    :type col2: :class:`str`
    """
    if typeutil.is_string_like(col1) and typeutil.is_string_like(col2):
      col1 = self.col_index(col1)
      col2 = self.col_index(col2)
    vals1, vals2=([],[])
    for v1, v2 in self.zip_non_null(col1, col2):
      vals1.append(v1)
      vals2.append(v2)
    try:
      return correl(vals1, vals2)
    except Exception, e:
      print e
      return None

  def spearman_correl(self, col1, col2):
    """
    Calculate the Spearman correlation coefficient between col1 and col2, only 
    taking rows into account where both of the values are not equal to None. If 
    there are not enough data points to calculate a correlation coefficient, 
    None is returned.
    
    :warning: The function depends on the following module: *scipy.stats.mstats*

    :param col1: column name for first column
    :type col1: :class:`str`

    :param col2: column name for second column
    :type col2: :class:`str`
    """
    try:
      import scipy.stats.mstats
      
      if typeutil.is_string_like(col1) and typeutil.is_string_like(col2):
        col1 = self.col_index(col1)
        col2 = self.col_index(col2)
      vals1, vals2=([],[])
      for v1, v2 in self.zip_non_null(col1, col2):
        vals1.append(v1)
        vals2.append(v2)
      try:
        correl = scipy.stats.mstats.spearmanr(vals1, vals2)[0]
        if scipy.isnan(correl):
          return None
        return correl
      except:
        return None

    except ImportError:
      print "Function needs scipy.stats.mstats, but I could not import it."
      raise
    

  def save(self, stream_or_filename, format='ost', sep=','):
    """
    save the table to stream or filename. The following three file formats
    are supported (for more information on file formats, see :meth:`load`):

    =============   =======================================
    ost             ost-specific format (human readable)
    csv             comma separated values (human readable)
    pickle          pickled byte stream (binary)
    html            HTML table
    context         ConTeXt table
    =============   =======================================

    :param stream_or_filename: filename or stream for writing output
    :type stream_or_filename: :class:`str` or :class:`file`

    :param format: output format (i.e. *ost*, *csv*, *pickle*)
    :type format: :class:`str`

    :raises: :class:`ValueError` if format is unknown
    """
    format=format.lower()
    if format=='ost':
      return self._save_ost(stream_or_filename)
    if format=='csv':
      return self._save_csv(stream_or_filename, sep=sep)
    if format=='pickle':
      return self._save_pickle(stream_or_filename)
    if format=='html':
      return self._save_html(stream_or_filename)
    if format=='context':
      return self._save_context(stream_or_filename)
    raise ValueError('unknown format "%s"' % format)

  def _save_pickle(self, stream):
    if not hasattr(stream, 'write'):
      stream=open(stream, 'wb')
    cPickle.dump(self, stream, cPickle.HIGHEST_PROTOCOL)

  def _save_html(self, stream_or_filename):
    def _escape(s):
      return s.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;')

    file_opened = False
    if not hasattr(stream_or_filename, 'write'):
      stream = open(stream_or_filename, 'w')
      file_opened = True
    else:
      stream = stream_or_filename
    stream.write('<table>') 
    stream.write('<tr>')
    for col_name in self.col_names:
      stream.write('<th>%s</th>' % _escape(col_name)) 
    stream.write('</tr>')
    for row in self.rows:
      stream.write('<tr>')
      for i, col in enumerate(row):
        val = ''
        if col != None:
           if self.col_types[i] == 'float':
             val = '%.3f' % col
           elif self.col_types[i] == 'int':
             val = '%d' % col
           elif self.col_types[i] == 'bool':
             val = col and 'true' or 'false'
           else:
             val  = str(col)
        stream.write('<td>%s</td>' % _escape(val))
      stream.write('</tr>')
    stream.write('</table>')
    if file_opened:
      stream.close()
  def _save_context(self, stream_or_filename):
    file_opened = False
    if not hasattr(stream_or_filename, 'write'):
      stream = open(stream_or_filename, 'w')
      file_opened = True
    else:
      stream = stream_or_filename
    stream.write('\\starttable[') 
    for col_type in self.col_types:
      if col_type =='string':
        stream.write('l|')
      elif col_type=='int':
        stream.write('r|')
      elif col_type =='float':
        stream.write('i3r|')
      else:
        stream.write('l|')
    stream.write(']\n\\HL\n')
    for col_name in self.col_names:
      stream.write('\\NC \\bf %s' % col_name) 
    stream.write(' \\AR\\HL\n')
    for row in self.rows:
      for i, col in enumerate(row):
        val = '---'
        if col != None:
           if self.col_types[i] == 'float':
             val = '%.3f' % col
           elif self.col_types[i] == 'int':
             val = '%d' % col
           elif self.col_types[i] == 'bool':
             val = col and 'true' or 'false'
           else:
             val  = str(col)
        stream.write('\\NC %s' % val)
      stream.write(' \\AR\n')
    stream.write('\\HL\n')
    stream.write('\\stoptable')
    if file_opened:
      stream.close()

  def _save_csv(self, stream, sep):
    if not hasattr(stream, 'write'):
      stream=open(stream, 'wb')

    writer=csv.writer(stream, delimiter=sep)
    writer.writerow(['%s' % n for n in self.col_names])
    for row in self.rows:
      row=list(row)
      for i, c in enumerate(row):
        if c==None:
          row[i]='NA'
      writer.writerow(row)

  def _save_ost(self, stream):
    if hasattr(stream, 'write'):
      writer=csv.writer(stream, delimiter=' ')
    else:
      stream=open(stream, 'w')
      writer=csv.writer(stream, delimiter=' ')
    if self.comment:
      stream.write(''.join(['# %s\n' % l for l in self.comment.split('\n')]))
    writer.writerow(['%s[%s]' % t for t in zip(self.col_names, self.col_types)])
    for row in self.rows:
      row=list(row)
      for i, c in enumerate(row):
        if c==None:
          row[i]='NA'
      writer.writerow(row)
  
     
  def get_numpy_matrix(self, *args):
    '''
    Returns a numpy matrix containing the selected columns from the table as 
    columns in the matrix.
    Only columns of type *int* or *float* are supported. *NA* values in the
    table will be converted to *None* values.

    :param \*args: column names to include in numpy matrix

    :warning: The function depends on *numpy*
    '''
    try:
      import numpy as np
      
      if len(args)==0:
        raise RuntimeError("At least one column must be specified.")
      
      idxs = []
      for arg in args:
        idx = self.col_index(arg)
        col_type = self.col_types[idx]
        if col_type!='int' and col_type!='float':
          raise TypeError("Numpy matrix can only be generated from numeric column types")
        idxs.append(idx)
      m = np.matrix([list(self[i]) for i in idxs]) 
      return m.T
    
    except ImportError:
      print "Function needs numpy, but I could not import it."
      raise
    


  def gaussian_smooth(self, col, std=1.0, na_value=0.0, padding='reflect', c=0.0):

    '''
    In place gaussian smooth of a column in the table with a given standard deviation.
    All nan are set to nan_value before smoothing.

    :param col: column name
    :type col: :class:`str`

    :param std: standard deviation for gaussian kernel
    :type std: `scalar` 

    :param na_value: all na (None) values of the speciefied column are set to na_value before smoothing
    :type na_value: `scalar`

    :param padding: allows to handle padding behaviour see scipy ndimage.gaussian_filter1d documentation for more information. standard is reflect
    :type padding: :class:`str`

    :param c: constant value used for padding if padding mode is constant
    :type c: `scalar`



    :warning: The function depends on *scipy*
    ''' 

    try:
      from scipy import ndimage
      import numpy as np
    except ImportError:
      print "I need scipy.ndimage and numpy, but could not import it"
      raise
      
    idx = self.col_index(col)
    col_type = self.col_types[idx]
    if col_type!='int' and col_type!='float':
      raise TypeError("gaussian_smooth can only be used on numeric column types")

    vals=[]
    for v in self[col]:
      if v!=None:
        vals.append(v)
      else:
        vals.append(na_value)

    
    smoothed_values_ndarray=ndimage.gaussian_filter1d(vals,std, mode=padding, cval=c)

    result=[]

    for v in smoothed_values_ndarray:
      result.append(v)

    self[col]=result


  def optimal_prefactors(self, ref_col, *args, **kwargs):
    '''
    This returns the optimal prefactor values (i.e. a, b, c, ...) for the
    following equation
    
    .. math::
      :label: op1
      
      a*u + b*v + c*w + ... = z
    
    where u, v, w and z are vectors. In matrix notation
    
    .. math::
      :label: op2
      
      A*p = z
    
    where A contains the data from the table (u,v,w,...), p are the prefactors 
    to optimize (a,b,c,...) and z is the vector containing the result of
    equation :eq:`op1`.
    
    The parameter ref_col equals to z in both equations, and \*args are columns
    u, v and w (or A in :eq:`op2`). All columns must be specified by their names.
    
    **Example:**
    
    .. code-block:: python
    
      tab.optimal_prefactors('colC', 'colA', 'colB')
    
    The function returns a list of containing the prefactors a, b, c, ... in 
    the correct order (i.e. same as columns were specified in \*args).
    
    Weighting:
    If the kwarg weights="columX" is specified, the equations are weighted by
    the values in that column. Each row is multiplied by the weight in that row,
    which leads to :eq:`op3`:
    
    .. math::
      :label: op3
      
      weight*a*u + weight*b*v + weight*c*w + ... = weight*z
    
    Weights must be float or int and can have any value. A value of 0 ignores
    this equation, a value of 1 means the same as no weight. If all weights are
    the same for each row, the same result will be obtained as with no weights.
    
    **Example:**
    
    .. code-block:: python
    
      tab.optimal_prefactors('colC', 'colA', 'colB', weights='colD')
    
    '''
    try:
      import numpy as np
  
      if len(args)==0:
        raise RuntimeError("At least one column must be specified.")
      
      b = self.get_numpy_matrix(ref_col)
      a = self.get_numpy_matrix(*args)
      
      if len(kwargs)!=0:
        if kwargs.has_key('weights'):
          w = self.get_numpy_matrix(kwargs['weights'])
          b = np.multiply(b,w)
          a = np.multiply(a,w)
          
        else:
          raise RuntimeError("specified unrecognized kwargs, use weights as key")
      
      k = (a.T*a).I*a.T*b
      return list(np.array(k.T).reshape(-1))
    
    except ImportError:
      print "Function needs numpy, but I could not import it."
      raise

  def compute_enrichment(self, score_col, class_col, score_dir='-', 
                        class_dir='-', class_cutoff=2.0):
    '''
    Computes the enrichment of column *score_col* classified according to
    *class_col*.
    
    For this it is necessary, that the datapoints are classified into positive
    and negative points. This can be done in two ways:
    
     - by using one 'bool' type column (*class_col*) which contains *True* for
       positives and *False* for negatives
       
     - by specifying a classification column (*class_col*), a cutoff value
       (*class_cutoff*) and the classification columns direction (*class_dir*).
       This will generate the classification on the fly

       * if ``class_dir=='-'``: values in the classification column that are less than or equal to class_cutoff will be counted as positives
       * if ``class_dir=='+'``: values in the classification column that are larger than or equal to class_cutoff will be counted as positives

    During the calculation, the table will be sorted according to *score_dir*,
    where a '-' values means smallest values first and therefore, the smaller
    the value, the better.
    
    :warning: If either the value of *class_col* or *score_col* is *None*, the
              data in this row is ignored.
    '''
    
    ALLOWED_DIR = ['+','-']
    
    score_idx = self.col_index(score_col)
    score_type = self.col_types[score_idx]
    if score_type!='int' and score_type!='float':
      raise TypeError("Score column must be numeric type")
    
    class_idx = self.col_index(class_col)
    class_type = self.col_types[class_idx]
    if class_type!='int' and class_type!='float' and class_type!='bool':
      raise TypeError("Classifier column must be numeric or bool type")
    
    if (score_dir not in ALLOWED_DIR) or (class_dir not in ALLOWED_DIR):
      raise ValueError("Direction must be one of %s"%str(ALLOWED_DIR))
    
    self.sort(score_col, score_dir)
    
    x = [0]
    y = [0]
    enr = 0
    old_score_val = None
    i = 0

    for row in self.rows:
      class_val = row[class_idx]
      score_val = row[score_idx]
      if class_val==None or score_val==None:
        continue
      if class_val!=None:
        if old_score_val==None:
          old_score_val = score_val
        if score_val!=old_score_val:
          x.append(i)
          y.append(enr)
          old_score_val = score_val
        i+=1
        if class_type=='bool':
          if class_val==True:
            enr += 1
        else:
          if (class_dir=='-' and class_val<=class_cutoff) or (class_dir=='+' and class_val>=class_cutoff):
            enr += 1
    x.append(i)
    y.append(enr)

    # if no false positives or false negatives values are found return None
    if x[-1]==0 or y[-1]==0:
      return None

    x = [float(v)/x[-1] for v in x]
    y = [float(v)/y[-1] for v in y]
    return x,y
    
  def compute_enrichment_auc(self, score_col, class_col, score_dir='-', 
                           class_dir='-', class_cutoff=2.0):
    '''
    Computes the area under the curve of the enrichment using the trapezoidal
    rule.
    
    For more information about parameters of the enrichment, see
    :meth:`compute_enrichment`.

    :warning: The function depends on *numpy*
    '''
    try:
      import numpy as np
      
      enr = self.compute_enrichment(score_col, class_col, score_dir,
                                          class_dir, class_cutoff)
      
      if enr==None:
        return None
      return np.trapz(enr[1], enr[0])
    except ImportError:
      print "Function needs numpy, but I could not import it."
      raise

  def compute_roc(self, score_col, class_col, score_dir='-',
                 class_dir='-', class_cutoff=2.0):
    '''
    Computes the receiver operating characteristics (ROC) of column *score_col*
    classified according to *class_col*.

    For this it is necessary, that the datapoints are classified into positive
    and negative points. This can be done in two ways:

     - by using one 'bool' column (*class_col*) which contains True for positives
       and False for negatives
     - by using a non-bool column (*class_col*), a cutoff value (*class_cutoff*)
       and the classification columns direction (*class_dir*). This will generate
       the classification on the fly

       - if ``class_dir=='-'``: values in the classification column that are less than or equal to *class_cutoff* will be counted as positives
       - if ``class_dir=='+'``: values in the classification column that are larger than or equal to *class_cutoff* will be counted as positives

    During the calculation, the table will be sorted according to *score_dir*,
    where a '-' values means smallest values first and therefore, the smaller
    the value, the better.

    If *class_col* does not contain any positives (i.e. value is True (if column
    is of type bool) or evaluated to True (if column is of type int or float
    (depending on *class_dir* and *class_cutoff*))) the ROC is not defined and
    the function will return *None*.

    :warning: If either the value of *class_col* or *score_col* is *None*, the
              data in this row is ignored.
    '''

    ALLOWED_DIR = ['+','-']

    score_idx = self.col_index(score_col)
    score_type = self.col_types[score_idx]
    if score_type!='int' and score_type!='float':
      raise TypeError("Score column must be numeric type")

    class_idx = self.col_index(class_col)
    class_type = self.col_types[class_idx]
    if class_type!='int' and class_type!='float' and class_type!='bool':
      raise TypeError("Classifier column must be numeric or bool type")

    if (score_dir not in ALLOWED_DIR) or (class_dir not in ALLOWED_DIR):
      raise ValueError("Direction must be one of %s"%str(ALLOWED_DIR))

    self.sort(score_col, score_dir)

    x = [0]
    y = [0]
    tp = 0
    fp = 0
    old_score_val = None

    for i,row in enumerate(self.rows):
      class_val = row[class_idx]
      score_val = row[score_idx]
      if class_val==None or score_val==None:
        continue
      if class_val!=None:
        if old_score_val==None:
          old_score_val = score_val
        if score_val!=old_score_val:
          x.append(fp)
          y.append(tp)
          old_score_val = score_val
        if class_type=='bool':
          if class_val==True:
            tp += 1
          else:
            fp += 1
        else:
          if (class_dir=='-' and class_val<=class_cutoff) or (class_dir=='+' and class_val>=class_cutoff):
            tp += 1
          else:
            fp += 1
    x.append(fp)
    y.append(tp)
    
    # if no false positives or false negatives values are found return None
    if x[-1]==0 or y[-1]==0:
      return None
    
    x = [float(v)/x[-1] for v in x]
    y = [float(v)/y[-1] for v in y]
    return x,y

  def compute_roc_auc(self, score_col, class_col, score_dir='-',
                    class_dir='-', class_cutoff=2.0):
    '''
    Computes the area under the curve of the receiver operating characteristics
    using the trapezoidal rule.
    
    For more information about parameters of the ROC, see
    :meth:`compute_roc`.

    :warning: The function depends on *numpy*
    '''
    try:
      import numpy as np

      roc = self.compute_roc(score_col, class_col, score_dir,
                            class_dir, class_cutoff)

      if not roc:
        return None
      return np.trapz(roc[1], roc[0])
    except ImportError:
      print "Function needs numpy, but I could not import it."
      raise

  def plot_roc(self, score_col, class_col, score_dir='-',
              class_dir='-', class_cutoff=2.0,
              style='-', title=None, x_title=None, y_title=None,
              clear=True, save=None):
    '''
    Plot an ROC curve using matplotlib.
    
    For more information about parameters of the ROC, see
    :meth:`compute_roc`, and for plotting see :meth:`Plot`.

    :warning: The function depends on *matplotlib*
    '''

    try:
      import matplotlib.pyplot as plt

      roc = self.compute_roc(score_col, class_col, score_dir,
                                   class_dir, class_cutoff)
      
      if not roc:
        return None

      enrx, enry = roc

      if not title:
        title = 'ROC of %s'%score_col

      if not x_title:
        x_title = 'false positive rate'

      if not y_title:
        y_title = 'true positive rate'

      if clear:
        plt.clf()

      plt.plot(enrx, enry, style)

      plt.title(title, size='x-large', fontweight='bold')
      plt.ylabel(y_title, size='x-large')
      plt.xlabel(x_title, size='x-large')

      if save:
        plt.savefig(save)

      return plt
    except ImportError:
      print "Function needs matplotlib, but I could not import it."
      raise
    
  def compute_mcc(self, score_col, class_col, score_dir='-',
                 class_dir='-', score_cutoff=2.0, class_cutoff=2.0):
    '''
    Compute Matthews correlation coefficient (MCC) for one column (*score_col*)
    with the points classified into true positives, false positives, true
    negatives and false negatives according to a specified classification
    column (*class_col*).
    
    The datapoints in *score_col* and *class_col* are classified into
    positive and negative points. This can be done in two ways:
    
     - by using 'bool' columns which contains True for positives and False
       for negatives
       
     - by using 'float' or 'int' columns and specifying a cutoff value and the
       columns direction. This will generate the classification on the fly
       
       * if ``class_dir``/``score_dir=='-'``: values in the classification column that are less than or equal to *class_cutoff*/*score_cutoff* will be counted as positives
       * if ``class_dir``/``score_dir=='+'``: values in the classification column that are larger than or equal to *class_cutoff*/*score_cutoff* will be counted as positives
                                    
    The two possibilities can be used together, i.e. 'bool' type for one column
    and 'float'/'int' type and cutoff/direction for the other column.
    '''
    ALLOWED_DIR = ['+','-']

    score_idx = self.col_index(score_col)
    score_type = self.col_types[score_idx]
    if score_type!='int' and score_type!='float' and score_type!='bool':
      raise TypeError("Score column must be numeric or bool type")

    class_idx = self.col_index(class_col)
    class_type = self.col_types[class_idx]
    if class_type!='int' and class_type!='float' and class_type!='bool':
      raise TypeError("Classifier column must be numeric or bool type")

    if (score_dir not in ALLOWED_DIR) or (class_dir not in ALLOWED_DIR):
      raise ValueError("Direction must be one of %s"%str(ALLOWED_DIR))
     
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    for i,row in enumerate(self.rows):
      class_val = row[class_idx]
      score_val = row[score_idx]
      if class_val!=None:
        if (class_type=='bool' and class_val==True) or (class_type!='bool' and ((class_dir=='-' and class_val<=class_cutoff) or (class_dir=='+' and class_val>=class_cutoff))):
          if (score_type=='bool' and score_val==True) or (score_type!='bool' and ((score_dir=='-' and score_val<=score_cutoff) or (score_dir=='+' and score_val>=score_cutoff))):
            tp += 1
          else:
            fn += 1
        else:
          if (score_type=='bool' and score_val==False) or (score_type!='bool' and ((score_dir=='-' and score_val>score_cutoff) or (score_dir=='+' and score_val<score_cutoff))):
            tn += 1
          else:
            fp += 1

    mcc = None
    msg = None
    if (tp+fn)==0:
      msg = 'factor (tp + fn) is zero'
    elif (tp+fp)==0:
      msg = 'factor (tp + fp) is zero'
    elif (tn+fn)==0:
      msg = 'factor (tn + fn) is zero'
    elif (tn+fp)==0:
      msg = 'factor (tn + fp) is zero'
    
    if msg:
      print "Could not compute MCC: MCC is not defined since %s" % msg
    else:
      mcc = ((tp*tn)-(fp*fn)) / math.sqrt((tp+fn)*(tp+fp)*(tn+fn)*(tn+fp))
    return mcc
    

  def empty(self, col_name=None, ignore_nan=True):
    '''
    Checks if a table is empty.
    
    If no column name is specified, the whole table is checked for being empty,
    whereas if a column name is specified, only this column is checked.
    
    By default, all NAN (or None) values are ignored, and thus, a table
    containing only NAN values is considered as empty. By specifying the 
    option ignore_nan=False, NAN values are counted as 'normal' values.
    '''
    
    # table with no columns and no rows
    if len(self.col_names)==0:
      if col_name:
        raise ValueError('Table has no column named "%s"' % col_name)
      return True
    
    # column name specified
    if col_name:
      if self.count(col_name, ignore_nan=ignore_nan)==0:
        return True
      else:
        return False
      
    # no column name specified -> test whole table
    else:
      for row in self.rows:
        for cell in row:
          if ignore_nan:
            if cell!=None:
              return False
          else:
            return False
    return True
    

  def extend(self, tab, overwrite=None):
    """
    Append each row of *tab* to the current table. The data is appended based
    on the column names, thus the order of the table columns is *not* relevant,
    only the header names.
    
    If there is a column in *tab* that is not present in the current table,
    it is added to the current table and filled with *None* for all the rows
    present in the current table.
    
    If the type of any column in *tab* is not the same as in the current table
    a *TypeError* is raised.
    
    If *overwrite* is not None and set to an existing column name, the specified 
    column in the table is searched for the first occurrence of a value matching
    the value of the column with the same name in the dictionary. If a matching
    value is found, the row is overwritten with the dictionary. If no matching
    row is found, a new row is appended to the table.
    """
    # add column to current table if it doesn't exist
    for name,typ in zip(tab.col_names, tab.col_types):
      if not name in self.col_names:
        self.add_col(name, typ)
    
    # check that column types are the same in current and new table
    for name in self.col_names:
      if name in tab.col_names:
        curr_type = self.col_types[self.col_index(name)]
        new_type = tab.col_types[tab.col_index(name)]
        if curr_type!=new_type:
          raise TypeError('cannot extend table, column %s in new '%name +\
                          'table different type (%s) than in '%new_type +\
                          'current table (%s)'%curr_type)
    
    num_rows = len(tab.rows)
    for i in range(0,num_rows):
      row = tab.rows[i]
      data = dict(zip(tab.col_names,row))
      self.add_row(data, overwrite)
    

def merge(table1, table2, by, only_matching=False):
  """
  Returns a new table containing the data from both tables. The rows are 
  combined based on the common values in the column(s) by. The option 'by' can
  be a list of column names. When this is the case, merging is based on
  multiple columns.
  For example, the two tables below

  ==== ====
  x     y            
  ==== ====
   1    10
   2    15
   3    20
  ==== ====
  
  ==== ====
  x     u
  ==== ====
    1  100
    3  200
    4  400
  ==== ====

  ===== ===== =====
  x      y     u
  ===== ===== =====
  1      10    100
  2      15    None
  3      20    200
  4      None  400
  ===== ===== =====
  
  when merged by column x, produce the following output:
  """
  def _key(row, indices):
    return tuple([row[i] for i in indices])
  def _keep(indices, cn, ct, ni):
    ncn, nct, nni=([],[],[])
    for i in range(len(cn)):
      if i not in indices:
        ncn.append(cn[i])
        nct.append(ct[i])
        nni.append(ni[i])
    return ncn, nct, nni
  col_names=list(table2.col_names)
  col_types=list(table2.col_types)
  new_index=[i for i in range(len(col_names))]
  if isinstance(by, str):
    common2_indices=[col_names.index(by)]
  else:
    common2_indices=[col_names.index(b) for b in by]
  col_names, col_types, new_index=_keep(common2_indices, col_names, 
                                        col_types, new_index)

  for i, name in enumerate(col_names):
    try_name=name
    counter=1
    while try_name in table1.col_names:
      counter+=1
      try_name='%s_%d' % (name, counter)
    col_names[i]=try_name
  common1={}
  if isinstance(by, str):
    common1_indices=[table1.col_names.index(by)]
  else:
    common1_indices=[table1.col_names.index(b) for b in by]
  for row in table1.rows:
    key=_key(row, common1_indices)
    if key in common1:
      raise ValueError('duplicate key "%s in first table"' % (str(key)))
    common1[key]=row
  common2={}
  for row in table2.rows:
    key=_key(row, common2_indices)
    if key in common2:
      raise ValueError('duplicate key "%s" in second table' % (str(key)))
    common2[key]=row
  new_tab=Table(table1.col_names+col_names, table1.col_types+col_types)
  for k, v in common1.iteritems():
    row=v+[None for i in range(len(table2.col_names)-len(common2_indices))]
    matched=False
    if k in common2:
      matched=True
      row2=common2[k]
      for i, index in enumerate(new_index):
        row[len(table1.col_names)+i]=row2[index]
    if only_matching and not matched:
      continue
    new_tab.add_row(row)
  if only_matching:
    return new_tab
  for k, v in common2.iteritems():
    if not k in common1:
      v2=[v[i] for i in new_index]
      row=[None for i in range(len(table1.col_names))]+v2
      for common1_index, common2_index in zip(common1_indices, common2_indices):
        row[common1_index]=v[common2_index]
      new_tab.add_row(row)
  return new_tab

