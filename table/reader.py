"""
Contains tabular data importers
"""
import csv, re, cPickle, os
import base, typeutil

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
      tab=base.Table(fieldnames, fieldtypes)
      header=True
      continue
    tab.add_row([x.strip('"') for x in values_pattern.findall(line)])
  if num_lines==0:
    raise IOError("Cannot read table from empty stream")
  return tab

def _coerce_col_types(table):
  for col_idx in range(len(table.col_names)):
    table.col_types[col_idx]=typeutil.guess_col_type(table[table.col_names[col_idx]])
  for row in table.rows:
    for idx in range(len(row)):
      row[idx]=typeutil.coerce(row[idx], table.col_types[idx])
      

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
      tab=base.Table(header, types)
      first=False
    else:
      tab.add_row(row)
  if first:
    raise IOError('trying to load table from empty CSV stream/file')

  _coerce_col_types(tab)
  return tab

def _load_pickle(stream_or_filename):
  if not hasattr(stream_or_filename, 'read'):
    stream=open(stream_or_filename, 'rb')
  else:
    stream=stream_or_filename
  return cPickle.load(stream)

def guess_format(filename):
  try:
    filename = filename.name
  except AttributeError, e:
    pass
  extension = os.path.splitext(filename)[1].lower()
  if extension == '.csv':
    return 'csv'
  if extension == '.pickle':
    return 'pickle'
  return 'ost'
  
  
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
    format = guess_format(stream_or_filename)
    
  if format=='ost':
    return _load_ost(stream_or_filename)
  if format=='csv':
    return _load_csv(stream_or_filename, sep=sep)
  if format=='pickle':
    return _load_pickle(stream_or_filename)
  raise ValueError('unknown format ""' % format)

