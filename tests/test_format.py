
import unittest
import sys

from tap import format
import tap

class TestTableFormatter(unittest.TestCase):
  def test_formats_empty_table(self):
    tf = format.TableFormatter()
    self.assertEqual(' x  y \n------\n', tf.format(tap.Tab(['x','y'])))

  def test_determines_colummn_width(self):
    tf = format.TableFormatter()
    tab = tap.Tab(['x', 'y', 'z'], x=[1,2,4,10],y=[2.33,None,20,11],
                  z='one two three sixtysix'.split())
    self.assertEqual(tf.width_for_cols(tab, 'x'), [2])
    self.assertEqual(tf.width_for_cols(tab, 'y'), [6])
    self.assertEqual(tf.width_for_cols(tab, 'z'), [8])

  def test_formats_none_as_na(self):
    tf = format.TableFormatter()
    self.assertEqual(tf.format_value(None, 'bool', 8), '    NA    ')
    self.assertEqual(tf.format_value(None, 'string', 8), '    NA    ')
    self.assertEqual(tf.format_value(None, 'int', 8), '    NA    ')
    self.assertEqual(tf.format_value(None, 'float', 8), '    NA    ')
  def test_right_aligns_float_values(self):
    tf = format.TableFormatter()
    self.assertEqual(tf.format_value(3.141, 'float', 8), '     3.141')

  def test_right_aligns_int_values(self):
    tf = format.TableFormatter()
    self.assertEqual(tf.format_value(42, 'int', 8), '        42')

  def test_formats_tables(self):
    tf = format.TableFormatter()
    tab = tap.Tab(['x', 'y', 'z'], x=[1,2],y=[2.33,None],
                  z='one two'.split())
    self.assertEqual(tf.format(tab), 
                     ' x    y     z  \n---------------\n  1  2.330 one \n  2   NA   two \n')



    
