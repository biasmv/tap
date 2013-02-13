
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

def guess_array_type(iterable):
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


class ColTypeParser:
  SHORT_TO_LONG_TYPES = {'s' : 'string', 'i': 'int', 'b' : 'bool', 'f' : 'float'}

  SHORT_TYPES = SHORT_TO_LONG_TYPES.keys()
  LONG_TYPES = SHORT_TO_LONG_TYPES.values()

  def from_str(self, type_str):
    type_str = type_str.lower()
    
    # single value
    if type_str in ColTypeParser.LONG_TYPES:
      return [type_str]
    if type_str in ColTypeParser.SHORT_TYPES:
      return [ColTypeParser.SHORT_TO_LONG_TYPES[type_str]]
    
    # comma separated list of long or short types
    type_list = []
    if type_str.find(',')!=-1:
      for t in type_str.split(','):
        if t in ColTypeParser.LONG_TYPES:
          type_list.append(t)
        elif t in ColTypeParser.SHORT_TYPES:
          type_list.append(ColTypeParser.SHORT_TO_LONG_TYPES[t])
        else:
          raise ValueError('Unknown type %s in types %s'%(t,type_str))
    
    # string of short types
    else:
      for t in type_str:
        if t in ColTypeParser.SHORT_TYPES:
          type_list.append(ColTypeParser.SHORT_TO_LONG_TYPES[t])
        else:
          raise ValueError('Unknown type %s in types %s'%(t,type_str))
    return type_list
  
  def from_list(self, types):
    type_list = []
    for t in types:
      # must be string type
      if type(t)==str:
        t = t.lower()
        if t in ColTypeParser.LONG_TYPES:
          type_list.append(t)
        elif t in ColTypeParser.SHORT_TYPES:
          type_list.append(ColTypeParser.SHORT_TO_LONG_TYPES[t])
        else:
          raise ValueError('Unknown type %s in types %s'%(t,types))
      
      # non-string type
      else:
        raise ValueError('Col type %s must be string or list'%types)
    return type_list
  

  def parse(self, types, exp_num=None):
    if types==None:
      return None
    
    type_list = []
    
    # string type
    if is_scalar(types):
      if type(types) == str:
        type_list = self.from_str(types)
      else:
        raise ValueError('Col type %s must be string or list' % types)
    # list type
    else:
      type_list = self.from_list(types)

    if exp_num:
      if len(type_list)!=exp_num:
        raise ValueError('Parsed number of col types (%i) differs from ' + \
                         'expected (%i) in types %s'%(len(type_list),exp_num,types))
      
    return type_list


