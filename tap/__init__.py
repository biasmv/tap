from base import Tab, merge

from reader import load


import plot
import writer

for ext in [plot, writer]:
  ext.EXT.apply(Tab)

