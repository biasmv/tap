import unittest

from table import coerce

class TestCoerce(unittest.TestCase):

  def test_coerces_na_to_none(self):
    self.assertEqual(coerce.coerce('NA', 'float'), None)

  def test_coerces_values_to_bool(self):
    self.assertEqual(coerce.coerce('1', 'bool'), True)
    self.assertEqual(coerce.coerce(1, 'bool'), True)
    self.assertEqual(coerce.coerce(0, 'bool'), False)
    self.assertEqual(coerce.coerce(2, 'bool'), True)
    self.assertEqual(coerce.coerce(True, 'bool'), True)
    self.assertEqual(coerce.coerce(False, 'bool'), False)
    self.assertEqual(coerce.coerce('YES', 'bool'), True)
    self.assertEqual(coerce.coerce('TRUE', 'bool'), True)
    self.assertEqual(coerce.coerce(None, 'bool'), None)

  def test_coerces_values_to_int(self):
    self.assertEqual(coerce.coerce(1, 'int'), 1)
    self.assertEqual(coerce.coerce(True, 'int'), 1)
    self.assertEqual(coerce.coerce(False, 'int'), 0)
    self.assertEqual(coerce.coerce(None, 'int'), None)


  def test_coerces_values_to_string(self):
    self.assertEqual(coerce.coerce('0.5', 'string'), '0.5')
    self.assertEqual(coerce.coerce(1, 'string'), '1')
    self.assertEqual(coerce.coerce(True, 'string'), 'True')
    self.assertEqual(coerce.coerce(False, 'string'), 'False')
    self.assertEqual(coerce.coerce(None, 'string'), None)

  def test_coerces_values_to_float(self):
    self.assertEqual(coerce.coerce('0.5', 'float'), 0.5)
    self.assertEqual(coerce.coerce(1, 'float'), 1.0)
    self.assertEqual(coerce.coerce(True, 'float'), 1.0)
    self.assertEqual(coerce.coerce(False, 'float'), 0.0)
    self.assertEqual(coerce.coerce(None, 'float'), None)

  def test_raises_value_error_for_unsupported_types(self):
    self.assertRaises(ValueError, coerce.coerce, 'value', 'flo')
