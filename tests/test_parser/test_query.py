"""
Tests for SQL query parsing functionality.
"""

import unittest
from simpledb.parser.query import Query


class TestQueryParsing(unittest.TestCase):
    """Test SQL query parsing."""

    def test_simple_select(self):
        """Test parsing a simple SELECT query."""
        query = Query.generate_query("SELECT name, age FROM people;")
        self.assertIsNotNone(query)
        self.assertEqual(query.get_table_name(), "people")
        self.assertFalse(query.has_join_arguments())

    def test_join_query_parsing(self):
        """Test parsing a JOIN query."""
        query = Query.generate_query("SELECT name, age FROM people JOIN classes ON id = class_id;")
        self.assertIsNotNone(query)
        self.assertTrue(query.has_join_arguments())


if __name__ == '__main__':
    unittest.main()
