class TableFormatter:

  def __init__(self, float_format='%.3f', int_format='%d', rows=None):
    self.float_format = float_format
    self.int_format = int_format
    self.rows = rows


  def rows_to_format(self, tab):
    if self.rows:
      return tab.rows[self.rows[0]:self.rows[1]]
    return tab.rows

  def width_for_cols(self, tab, *cols):
    col_idxs = [tab.col_index(col) for col in cols]
    widths = [len(tab.col_names[col_idx]) for col_idx in col_idxs]
    for row in self.rows_to_format(tab):
      for i, col_idx in enumerate(col_idxs):
        value = row[col_idx]
        if value==None:
          widths[i]=max(widths[i], len('NA'))
        elif tab.col_types[col_idx]=='float':
          widths[i]=max(widths[i], len(self.float_format % value))
        elif tab.col_types[col_idx]=='int':
          widths[i]=max(widths[i], len(self.int_format % value))
        else:
          widths[i]=max(widths[i], len(str(value)))
    return widths

  def format_value(self, value, type, width):
    if value==None:
      return 'NA'.center(width+2)
    if type=='float':
      return (self.float_format % value).rjust(width+2)
    if type=='int':
      return (self.int_format % value).rjust(width+2)
    return ' '+str(value).ljust(width+1)

  def format(self, table):
    s=''
    if table.comment:
      s+=''.join(['# %s\n' % l for l in table.comment.split('\n')])

    widths=self.width_for_cols(table, *table.col_names)
    total_width=sum(widths)+2*len(widths)
    for width, col_name in zip(widths, table.col_names):
      s+=col_name.center(width+2)
    s+='\n%s\n' % ('-'*total_width)
    for row in self.rows_to_format(table):
      for width, ty, col in zip(widths, table.col_types, row):
        s+=self.format_value(col, ty, width)
      s+='\n'
    return s
