import unittest

from table import typeutil

class TestCoerce(unittest.TestCase):

  def test_coerces_na_to_none(self):
    self.assertEqual(typeutil.coerce('NA', 'float'), None)

  def test_coerces_values_to_bool(self):
    self.assertEqual(typeutil.coerce('1', 'bool'), True)
    self.assertEqual(typeutil.coerce(1, 'bool'), True)
    self.assertEqual(typeutil.coerce(0, 'bool'), False)
    self.assertEqual(typeutil.coerce(2, 'bool'), True)
    self.assertEqual(typeutil.coerce(True, 'bool'), True)
    self.assertEqual(typeutil.coerce(False, 'bool'), False)
    self.assertEqual(typeutil.coerce('YES', 'bool'), True)
    self.assertEqual(typeutil.coerce('TRUE', 'bool'), True)
    self.assertEqual(typeutil.coerce(None, 'bool'), None)

  def test_coerces_values_to_int(self):
    self.assertEqual(typeutil.coerce(1, 'int'), 1)
    self.assertEqual(typeutil.coerce(True, 'int'), 1)
    self.assertEqual(typeutil.coerce(False, 'int'), 0)
    self.assertEqual(typeutil.coerce(None, 'int'), None)


  def test_coerces_values_to_string(self):
    self.assertEqual(typeutil.coerce('0.5', 'string'), '0.5')
    self.assertEqual(typeutil.coerce(1, 'string'), '1')
    self.assertEqual(typeutil.coerce(True, 'string'), 'True')
    self.assertEqual(typeutil.coerce(False, 'string'), 'False')
    self.assertEqual(typeutil.coerce(None, 'string'), None)

  def test_coerces_values_to_float(self):
    self.assertEqual(typeutil.coerce('0.5', 'float'), 0.5)
    self.assertEqual(typeutil.coerce(1, 'float'), 1.0)
    self.assertEqual(typeutil.coerce(True, 'float'), 1.0)
    self.assertEqual(typeutil.coerce(False, 'float'), 0.0)
    self.assertEqual(typeutil.coerce(None, 'float'), None)

  def test_raises_value_error_for_unsupported_types(self):
    self.assertRaises(ValueError, typeutil.coerce, 'value', 'flo')

class TestTypeutil(unittest.TestCase):

  def test_is_string_like(self):
    self.assertTrue(typeutil.is_string_like(u'unicode'))
    self.assertTrue(typeutil.is_string_like('ascii'))
    self.assertTrue(typeutil.is_string_like(b'byte-string'))

    self.assertFalse(typeutil.is_string_like(3))
    self.assertFalse(typeutil.is_string_like(['a','b']))

  def test_guess_col_type(self):
    self.assertEqual(typeutil.guess_col_type(['1', '1.3', '2']), 'float')
    self.assertEqual(typeutil.guess_col_type(['1', '1', '2']), 'int')
    self.assertEqual(typeutil.guess_col_type(['NONE', '1', '1', '2']), 'int')
    self.assertEqual(typeutil.guess_col_type(['NONE', '1', '1', '2']), 'int')
    self.assertEqual(typeutil.guess_col_type(['NONE', '1', '1', 'a']), 'string')
    self.assertEqual(typeutil.guess_col_type(['NONE', 'TRUE', 'False']), 'bool')
    self.assertEqual(typeutil.guess_col_type(['NONE']), 'string')
