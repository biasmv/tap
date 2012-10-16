import unittest, os, sys
from table import Table, load
from table import reader
import fixtures
import helper

class TestReader(helper.TableTestCase):
  def test_guess_format_from_file_extensions(self):
    self.assertEqual(reader.guess_format('table_test.CSV'), 'csv')
    self.assertEqual(reader.guess_format('table_test.PICKLE'), 'pickle')
    self.assertEqual(reader.guess_format('table_test.csv'), 'csv')
    self.assertEqual(reader.guess_format('table_test.pickle'), 'pickle')
    self.assertEqual(reader.guess_format('table_test.tab'), 'ost')
    self.assertEqual(reader.guess_format('table_test.ost'), 'ost')
    self.assertEqual(reader.guess_format('table_test.xyz'), 'ost')
    
  def test_load_imports_table_from_stream(self):
    # FIXME: Implement
    pass

  def test_load_detects_format_from_file_extension(self):   
    tab = fixtures.create_test_table()

    # FIXME: We shouldn't need to write the files first. That's bad test design
    # write to disc
    tab.save("saveloadtable_filename_out.csv", format='csv')
    tab.save("saveloadtable_filename_out.tab", format='ost')
    tab.save("saveloadtable_filename_out.pickle", format='pickle')
    
    # read from disc: csv
    in_stream_csv = open("saveloadtable_filename_out.csv", 'r')
    tab_loaded_stream_csv = load(in_stream_csv)
    in_stream_csv.close()
    tab_loaded_fname_csv = load('saveloadtable_filename_out.csv')

    # check content: csv
    self.compare_data_from_dict(tab_loaded_stream_csv, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    self.compare_data_from_dict(tab_loaded_fname_csv, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
  
    # read from disc: pickle
    in_stream_pickle = open("saveloadtable_filename_out.pickle", 'rb')
    tab_loaded_stream_pickle = load(in_stream_pickle)
    in_stream_pickle.close()
    tab_loaded_fname_pickle = load('saveloadtable_filename_out.pickle')

    # check content: pickle
    self.compare_data_from_dict(tab_loaded_stream_pickle, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    self.compare_data_from_dict(tab_loaded_fname_pickle, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})

    # read from disc: ost
    in_stream_ost = open("saveloadtable_filename_out.tab", 'rb')
    tab_loaded_stream_ost = load(in_stream_ost)
    in_stream_ost.close()
    tab_loaded_fname_ost = load('saveloadtable_filename_out.tab')

    # check content: ost
    self.compare_data_from_dict(tab_loaded_stream_ost, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    self.compare_data_from_dict(tab_loaded_fname_ost, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
  

  def test_loadTableOSTUnknownType(self):
    self.assertRaises(ValueError, load, os.path.join('tests/data','ost-table-unknown-type.tab'))

  def testloadTableOSTNoType(self):
    tab = load(os.path.join('tests/data','ost-table-notype.tab'))
    self.compare_data_from_dict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    
  def test_loads_difficult_headers(self):
    tab = load(os.path.join('tests/data','ost-table-difficult-headers.tab'))
    self.assertEquals(tab.col_types, ['float','float','float','float','float'])

  def test_saves_and_loads_ost_tables(self):
    tab = fixtures.create_test_table()
    self.compare_data_from_dict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    
    # write to disc
    tab.save("saveloadtable_filename_out.tab")
    out_stream = open("saveloadtable_stream_out.tab", 'w')
    tab.save(out_stream)
    out_stream.close()
    
    # read from disc
    in_stream = open("saveloadtable_stream_out.tab", 'r')
    tab_loaded_stream = load(in_stream)
    in_stream.close()
    tab_loaded_fname = load('saveloadtable_filename_out.tab')
    
    # check content
    self.compare_data_from_dict(tab_loaded_stream, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    self.compare_data_from_dict(tab_loaded_fname, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    
    # check Errors for empty/non existing files
    self.assertRaises(IOError, load, 'nonexisting.file')
    self.assertRaises(IOError, load, os.path.join('tests/data','emptytable.tab'))
    in_stream = open(os.path.join('tests/data','emptytable.csv'), 'r')
    self.assertRaises(IOError, load, in_stream)
    
  def test_save_escapes_whitespaces(self):
    tab = fixtures.create_test_table()
    tab.add_row(['hello spaces',10, 10.1], overwrite=None)
    self.compare_data_from_dict(tab, {'first': ['x','foo',None,'hello spaces'], 'second': [3,None,9,10], 'third': [None,2.2,3.3,10.1]})

    # write to disc
    tab.save("saveloadtable_withspaces_filename_out.tab")

    # read from disc
    tab_loaded_fname = load('saveloadtable_withspaces_filename_out.tab')
    self.compare_data_from_dict(tab_loaded_fname, {'first': ['x','foo',None,'hello spaces'], 'second': [3,None,9,10], 'third': [None,2.2,3.3,10.1]})
  def test_saves_html_files(self):
    import StringIO
    tab = fixtures.create_test_table()
    stream = StringIO.StringIO()
    tab.save(stream, format='html')
    self.assertEqual(stream.getvalue(), '<table><tr><th>first</th><th>second</th><th>third</th></tr><tr><td>x</td><td>3</td><td></td></tr><tr><td>foo</td><td></td><td>2.200</td></tr><tr><td></td><td>9</td><td>3.300</td></tr></table>')
  def test_saves_context_files(self):
    import StringIO
    tab = fixtures.create_test_table()
    stream = StringIO.StringIO()
    tab.save(stream, format='context')
    self.assertEqual(stream.getvalue(), 
                     '\\starttable[l|r|i3r|]\n\\HL\n\\NC \\bf first\\NC \\bf second\\NC \\bf third \\AR\\HL\n\\NC x\\NC 3\\NC --- \\AR\n\\NC foo\NC ---\NC 2.200 \\AR\n\\NC ---\\NC 9\\NC 3.300 \\AR\n\\HL\n\\stoptable')

  def test_saves_and_loads_csv_files(self):
    tab = fixtures.create_test_table()
    self.compare_data_from_dict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})

    # write to disc
    tab.save("saveloadtable_filename_out.csv", format='csv')
    out_stream = open("saveloadtable_stream_out.csv", 'w')
    tab.save(out_stream, format='csv')
    out_stream.close()
    
    # read from disc
    in_stream = open("saveloadtable_stream_out.csv", 'r')
    tab_loaded_stream = load(in_stream, format='csv')
    in_stream.close()
    tab_loaded_fname = load('saveloadtable_filename_out.csv', format='csv')

    # check content
    self.compare_data_from_dict(tab_loaded_stream, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    self.compare_data_from_dict(tab_loaded_fname, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
  
  def test_saves_and_loads_pickled_tables(self):
    tab = fixtures.create_test_table()
    self.compare_data_from_dict(tab, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    # write to disc
    tab.save("saveloadtable_filename_out.pickle", format='pickle')
    out_stream = open("saveloadtable_stream_out.pickle", 'wb')
    tab.save(out_stream, format='pickle')
    out_stream.close()

    # read from disc
    in_stream = open("saveloadtable_stream_out.pickle", 'rb')
    tab_loaded_stream = load(in_stream, format='pickle')
    in_stream.close()
    tab_loaded_fname = load('saveloadtable_filename_out.pickle', format='pickle')

    # check content
    self.compare_data_from_dict(tab_loaded_stream, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
    self.compare_data_from_dict(tab_loaded_fname, {'first': ['x','foo',None], 'second': [3,None,9], 'third': [None,2.2,3.3]})
