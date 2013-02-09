import unittest
import glob
import os

class TabTestCase(unittest.TestCase):

  def tearDown(self):
    for filename in glob.glob('*_out.*'):
      os.remove(filename)

  def compare_row_count(self, t, row_count):
    '''
    Compare the number of rows
    '''
    self.assertEqual(len(t.rows),
                      row_count,
                      "row count (%i) different from expected value (%i)" \
                      %(len(t.rows), row_count))

  def compare_col_count(self, t, col_count):
    '''
    Compare the number of columns
    '''
    self.assertEqual(len(t.col_names),
                      col_count,
                      "column count (%i) different from expected value (%i)" \
                      %(len(t.col_names), col_count))

  def compare_col_names(self, t, col_names):
    '''
    Compare all column names of the table with a list of reference col names
    '''
    self.compare_col_count(t, len(col_names))
    for i, (col_name, ref_name) in enumerate(zip(t.col_names, col_names)):
        self.assertEqual(col_name,
                          ref_name,
                          "column name (%s) different from expected name (%s) at col %i" \
                          %(col_name, ref_name, i))

  def compare_data_from_dict(self, t, data_dict):
    '''
    Compare all values of a table with reference values given in the form of a
    dictionary containing a list of values for each column.
    '''
    self.compare_col_count(t, len(data_dict))
    for k, v in data_dict.iteritems():
      self.compare_data_for_col(t, k, v)
      
  def compare_data_for_col(self, t, col_name, ref_data):
    '''
    Compare the values of each row of ONE column specified by its name with
    the reference values specified as a list of values for this column.
    '''
    self.compare_row_count(t, len(ref_data))
    idx = t.col_index(col_name)
    col_type = t.col_types[idx]
    for i, (row, ref) in enumerate(zip(t.rows, ref_data)):
      if (isinstance(ref, float) or isinstance(ref, int)) and (isinstance(row[idx], float) or isinstance(row[idx], int)):
        self.assertAlmostEqual(row[idx],
                                ref,
                                msg="data (%s) in col (%s), row (%i) different from expected value (%s)" \
                                %(row[idx], col_name, i, ref))
      else:
        self.assertEqual(row[idx],
                          ref,
                          "data (%s) in col (%s), row (%i) different from expected value (%s)" \
                          %(row[idx], col_name, i, ref))

  def compare_col_types(self, t, col_names, ref_types):
    '''
    Compare the types of n columns specified by their names with reference
    values specified either as a string consisting of the short type names 
    (e.g 'sfb') or a list of strings consisting of the long type names
    (e.g. ['string','float','bool'])
    '''
    if type(ref_types)==str:
      trans = {'s' : 'string', 'i': 'int', 'b' : 'bool', 'f' : 'float'}
      ref_types = [trans[rt] for rt in ref_types]
    if type(col_names)==str:
      col_names = [col_names]
    self.assertEqual(len(col_names),
                      len(ref_types),
                      "number of col names (%i) different from number of reference col types (%i)" \
                      %(len(col_names), len(ref_types)))
    idxs = [t.col_index(x) for x in col_names]
    for idx, ref_type in zip(idxs, ref_types):
      self.assertEqual(t.col_types[idx],
                        ref_type,
                        "column type (%s) at column %i, different from reference col type (%s)" \
                        %(t.col_types[idx], idx, ref_type))

  def compare_images(self, img1, img2):
    '''
    Compares two images based on all pixel values. This function needs the
    python imaging library (PIL) package.
    '''
    if not HAS_PIL:
      return
    diff = ImageChops.difference(img1, img2)
    self.assertEqual(diff.getbbox(),None)
