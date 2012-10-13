
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
    if isinstance(value, str) or isinstance(value, unicode):
      if value.upper() in ('FALSE', 'NO',):
        return False
      return True
    return bool(value)
  raise ValueError('Unknown type %s' % ty)
