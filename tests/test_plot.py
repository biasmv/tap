import unittest, os


HAS_NUMPY=True
HAS_SCIPY=True
HAS_MPL=True
HAS_PIL=True
try:
  import numpy as np
except ImportError:
  HAS_NUMPY=False
  print "Could not find numpy: ignoring some table class unit tests"

try:
  import scipy.stats.mstats
except ImportError:
  HAS_SCIPY=False
  print "Could not find scipy.stats.mstats: ignoring some table class unit tests"
  
try:
  import matplotlib
  matplotlib.use('Agg')
except ImportError:
  HAS_MPL=False
  print "Could not find matplotlib: ignoring some table class unit tests"
  
try:
  import Image
  import ImageChops
except ImportError:
  HAS_PIL=False

from table import Table

import fixtures

class TestPlotExtension(unittest.TestCase):

  def test_plot(self):
    if not HAS_MPL or not HAS_NUMPY:
      return
    tab = fixtures.create_test_table()
    self.assertRaises(ValueError, tab.plot, 'second', x_range=1)
    self.assertRaises(ValueError, tab.plot, x='second', y='third', y_range=[1,2,3])
    self.assertRaises(ValueError, tab.plot, x='second', y='third', z_range='st')

  def test_hexbin(self):
    if not HAS_MPL or not HAS_NUMPY:
      return
    tab = fixtures.create_test_table()
    self.assertRaises(ValueError, tab.plot_hexbin, x='second', y='third', x_range=1)
    self.assertRaises(ValueError, tab.plot_hexbin, x='second', y='third', x_range=[1,2,3])

  def test_plot_enrichment(self):
    if not HAS_MPL or not HAS_PIL:
      return
    tab = Table(['score', 'rmsd', 'classific'], 'ffb',
                score=[2.64,1.11,2.17,0.45,0.15,0.85,1.13,2.90,0.50,1.03,1.46,2.83,1.15,2.04,0.67,1.27,2.22,1.90,0.68,0.36,1.04,2.46,0.91,0.60],
                rmsd=[9.58,1.61,7.48,0.29,1.68,3.52,3.34,8.17,4.31,2.85,6.28,8.78,0.41,6.29,4.89,7.30,4.26,3.51,3.38,0.04,2.21,0.24,7.58,8.40],
                classific=[False,True,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,True,False,False])
 
    pl = tab.plot_enrichment(score_col='score', score_dir='-',
                            class_col='rmsd', class_cutoff=2.0,
                            class_dir='-',
                            save=os.path.join("tests/data","enrichment-out.png"))
    img1 = Image.open(os.path.join("tests/data","enrichment-out.png"))
    
