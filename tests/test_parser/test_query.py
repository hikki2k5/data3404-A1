"""
Tests for SQL query parsing functionality.
"""

import unittest
from simpledb.parser.query import Query
from simpledb.main.catalog.catalog import Catalog
from simpledb.main.catalog.tuple_desc import TupleDesc

class TestQueryParsing(unittest.TestCase):
    """Test SQL query parsing."""

    def test_simple_select(self):
        """Test parsing a simple SELECT query."""
        query = Query.generate_query("SELECT name, age FROM Students;")
        self.assertIsNotNone(query)
        self.assertEqual(query.get_table_name(), "Students")
        self.assertTrue(query.get_projected_columns() == ["name", "age"])
        self.assertFalse(query.has_join_arguments())

    def test_join_query_parsing(self):
        """Test parsing a JOIN query."""
        query = Query.generate_query("SELECT name, age FROM students JOIN courses ON id = class_id;")
        self.assertIsNotNone(query)
        self.assertEqual(query.get_table_name(), "students")
        self.assertTrue(query.get_projected_columns() == ["name", "age"])
        self.assertTrue(query.has_join_arguments())
        join_args = query.get_join_args()
        self.assertIsNotNone(join_args)
        self.assertEqual(join_args.get_join_table(), "courses")
        self.assertEqual(join_args.get_left_column(), "id")
        self.assertEqual(join_args.get_right_column(), "class_id")

    def test_validate_query(self):
        catalog = Catalog()
        student_schema = TupleDesc()
        student_schema.add_string("name").add_integer("age").add_string("course_id")
        catalog.add_schema(student_schema, "Students")
        course_schema = TupleDesc()
        course_schema.add_string("id").add_string("title")
        catalog.add_schema(course_schema, "Courses")
        query = Query.generate_query("SELECT name, age FROM Students JOIN Courses ON course_id = id")
        self.assertIsNotNone(query)
        error = query.validate(catalog)
        self.assertIsNone(error)
    
if __name__ == '__main__':
    unittest.main()
