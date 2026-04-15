"""
Unit tests for DataPage class.
"""

import unittest
from simpledb.disk.data_page import DataPage
from simpledb.main.database_constants import DatabaseConstants
from simpledb.heap.page_id import PageId
from simpledb.heap.tuple import Tuple
from simpledb.main.catalog.tuple_desc import TupleDesc
from simpledb.main.catalog.type import Type


class TestDataPage(unittest.TestCase):
    """Test cases for DataPage."""

    def setUp(self):
        """Set up test schema."""
        self.schema = TupleDesc()
        self.schema.add_string("name").add_integer("age")
        self.tuple1 = Tuple(self.schema)
        self.tuple1.set_column(0, "Alice")
        self.tuple1.set_column(1, 25)
        self.tuple2 = Tuple(self.schema)
        self.tuple2.set_column(0, "Bob")
        self.tuple2.set_column(1, 30)

    def test_initialise(self):
        """Test initialisation of DataPage."""
        page = DataPage()
        page.initialise("test_table")
        self.assertEqual(page.get_magic(), DatabaseConstants.PAGE_MAGIC)
        self.assertEqual(page.get_version_type(), DatabaseConstants.DATA_PAGE_TYPE)
        self.assertEqual(page.get_next_page().get(), DatabaseConstants.INVALID_PAGE_ID)
        self.assertEqual(page.get_num_slots(), 0)
        self.assertEqual(page.get_free_start(), DataPage.SLOT_DIR_START)
        self.assertEqual(page.get_free_end(), DatabaseConstants.PAGE_SIZE)
        self.assertEqual(page.get_schema_name(), "test_table")

    def test_insert_get_record(self):
        """Test inserting and getting records."""
        page = DataPage()
        page.initialise("test_table")
        success = page.insert_record(self.tuple1)
        self.assertTrue(success)
        self.assertEqual(page.get_record_count(), 1)

        retrieved_tuple = Tuple(self.schema)
        page.get_record(0, retrieved_tuple)
        self.assertEqual(retrieved_tuple.get_column(0), "Alice")
        self.assertEqual(retrieved_tuple.get_column(1), 25)

    def test_insert_multiple_records(self):
        """Test inserting multiple records."""
        page = DataPage()
        page.initialise("test_table")
        self.assertTrue(page.insert_record(self.tuple1))
        self.assertTrue(page.insert_record(self.tuple2))
        self.assertEqual(page.get_record_count(), 2)

        retrieved1 = Tuple(self.schema)
        retrieved2 = Tuple(self.schema)
        page.get_record(0, retrieved1)
        page.get_record(1, retrieved2)
        self.assertEqual(retrieved1.get_column(0), "Alice")
        self.assertEqual(retrieved2.get_column(0), "Bob")

    def test_get_max_records_on_page(self):
        """Test max records calculation."""
        max_records = DataPage.get_max_records_on_page(self.schema)
        self.assertGreater(max_records, 0)
        self.assertLessEqual(max_records, DatabaseConstants.MAX_SLOT_ENTRIES)

    def test_insert_full_page(self):
        """Test inserting multiple records till page is full."""
        page = DataPage()
        page.initialise("test_table")
        expected_num_tuples = (DatabaseConstants.PAGE_SIZE - DatabaseConstants.PAGE_HEADER_SIZE) // (self.schema.get_max_tuple_length() + DatabaseConstants.SLOT_ENTRY_SIZE) 
        for i in range(expected_num_tuples):
	        self.assertTrue(page.insert_record(self.tuple1))
        self.assertFalse(page.insert_record(self.tuple2))
        self.assertEqual(page.get_record_count(), expected_num_tuples)


if __name__ == '__main__':
    unittest.main()