# tap - tables and python

tap grew out of the need of having an simple and unified interface to interact with tabular data. Our daily business required reading and writing hundreds of small files with tabular content. These files did not warrant to be put into a relational database. That's why we developed tap.


# usage

```python
import tap

ages = tap.Tab(name=['Anton', 'Moritz', 'Theo'],
               age=[25,66,32]) 
ages.sort('age')
print ages
#  age   name  
# -------------
#  25    Anton  
#  32    Theo
#  66    Moritz   

salaries = tap.Tab(name=['Anton', 'Moritz', 'Theo'],
                   salary=[100,200,150])

merged = tap.merge(ages, salaries, by='name')

print merged
#  age   name   salary 
#---------------------
# 66    Moritz  200      
# 32    Theo    150   
# 25    Anton   100      
```

# read the docs

The documentation for the latest version of `tap` is available [here](https://tap.readthedocs.org/en/latest/)




