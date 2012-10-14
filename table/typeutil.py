
def is_string_like(value):
  '''
  Helper function to determine whether a certain value behaves like a string
  '''
  return isinstance(value, basestring)

def is_null_string(value):
  '''
  Returns true when the string is either empty, 'NULL', 'NONE' or 'NA'
  '''
  value=value.strip().upper()
  return value in ('', 'NULL', 'NONE', 'NA')

def is_scalar(value):
  '''
  Returns true, if *value* is scalar, e.g not a iterable or a string-like
  object
  '''
  if is_string_like(value):
    return True
  try:
    iter(value)
    return False
  except:
    return True

def guess_col_type(iterable):
  '''
  guess column type for iterable
  '''
  empty=True
  possibilities=set(['bool', 'int', 'float'])
  for ele in iterable:
    str_ele=str(ele).upper()
    if is_null_string(str_ele):
      continue
    empty=False
    if 'int' in possibilities:
      try:
        int(str_ele)
      except ValueError:
        possibilities.remove('int')

    if 'float' in possibilities:
      try:
        float(str_ele)
      except ValueError:
        possibilities.remove('float')
    if 'bool' in possibilities:
      if str_ele not in set(['YES', 'NO', 'TRUE', 'FALSE']):
        possibilities.remove('bool')

    if len(possibilities)==0:
      return 'string'
  if len(possibilities)==2:
    return 'int'
  if empty:
    return 'string'
  # return the last element available
  return possibilities.pop()

def coerce(value, ty):
  '''
  Try to convert values (e.g. from :class:`str` type) to the specified type

  :param value: the value
  :type value: any type

  :param ty: name of type to convert it to (i.e. *int*, *float*, *string*,
              *bool*)
  :type ty: :class:`str`
  '''
  if value=='NA' or value==None:
    return None
  if ty=='int':
    return int(value)
  if ty=='float':
    return float(value)
  if ty=='string':
    return str(value)
  if ty=='bool':
    if is_string_like(value):
      if value.upper() in ('FALSE', 'NO',):
        return False
      return True
    return bool(value)
  raise ValueError('Unknown type %s' % ty)

