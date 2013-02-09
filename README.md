# tap - tables and python

tap grew out of the need of having an simple and unified interface to interact with tabular data. Our daily business required reading and writing hundreds of small files with tabular content. These files did not warrant to be put into a relational database. That's why we developed tap.


# usage

import tap

tab = tap.Tab(name=['Anton', 'Moritz', 'Theo'],
               age=[25,66,32]) 
print tab

tab.sort('age')
print ages

salaries = tab.Tab(name=['Anton', 'Moritz', 'Theo'],
                   salary=[100,200,150])

merged = tap.merge(tab, salaries, by='name')

print merged






