"""Tests for the AuctionDB CSV importer helpers used in performance evaluation."""

import os
import tempfile
import unittest

from simpledb.main.catalog.tuple_desc import TupleDesc
from simpledb.main.database_manager import DatabaseManager
from tests.performance.import_csv import (
    build_schema,
    convert_csv_row,
    create_requested_hash_indexes,
    parse_index_columns,
    parse_type_list,
)


class TestImportCsvHelpers(unittest.TestCase):
    """Verify the importer helper functions for Option 4 evaluation setup."""

    def test_parse_type_list_defaults_to_strings(self):
        """Importer should default all CSV fields to strings when schema is omitted."""
        self.assertEqual(parse_type_list(None, ["a", "b", "c"]), ["str", "str", "str"])

    def test_parse_type_list_rejects_invalid_length(self):
        """Importer should reject a schema list that does not match CSV column count."""
        with self.assertRaises(ValueError):
            parse_type_list("int,str", ["a"])

    def test_convert_csv_row_converts_types(self):
        """Importer should convert raw CSV strings into the expected Python values."""
        row = convert_csv_row(
            ["12", "3.5", "true", "alice@example.com"],
            ["id", "score", "active", "email"],
            ["int", "float", "bool", "str"],
        )
        self.assertEqual(row[:3], [12, 3.5, True])
        self.assertTrue(row[3].endswith("@example.com"))

    def test_build_schema_and_create_hash_indexes(self):
        """Importer should be able to build schema objects and create requested hash indexes."""
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db_name = temp_file.name
        temp_file.close()

        try:
            dbms = DatabaseManager(db_name)
            schema = build_schema(["user_id", "name"], ["int", "str"])
            self.assertIsInstance(schema, TupleDesc)
            dbms.get_catalog().add_schema(schema, "users")

            table = dbms.get_heap_file("users")
            with table.inserter() as inserter:
                inserter.insert([1, "Alice"])
                inserter.insert([2, "Bob"])

            created = create_requested_hash_indexes(dbms, "users", ["user_id"], bucket_count=16)

            self.assertEqual(created, ["users_user_id_hash_idx"])
            self.assertIsNotNone(dbms.get_index("users", "user_id"))
        finally:
            dbms.close()
            if os.path.exists(db_name):
                os.remove(db_name)

    def test_parse_index_columns(self):
        """Importer should parse a comma-separated index column list cleanly."""
        self.assertEqual(parse_index_columns(" user_id, item_id , category "), ["user_id", "item_id", "category"])


if __name__ == "__main__":
    unittest.main()
