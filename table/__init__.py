from base import Table, merge

from reader import load


import plot
import writer

for ext in [plot, writer]:
  ext.EXT.apply(Table)
