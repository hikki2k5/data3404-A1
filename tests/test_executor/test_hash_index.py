"""Tests for the integrated hash index and planner/executor integration."""

import os
import tempfile
import unittest

from simpledb.executor.query_planner import QueryPlanner
from simpledb.index.hash_index import HashIndex
from simpledb.main.catalog.tuple_desc import TupleDesc
from simpledb.main.database_manager import DatabaseManager
from simpledb.parser.query import Query


class TestHashIndex(unittest.TestCase):
    """Covers index correctness, maintenance, and query-planner integration."""

    def setUp(self):
        """Create a small test database with deterministic sample rows."""
        self.db_name = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
        self.dbms = DatabaseManager(self.db_name)
        self.planner = QueryPlanner(self.dbms)

        self.schema = TupleDesc().add_integer("id").add_string("name").add_string("class")
        self.dbms.get_catalog().add_schema(self.schema, "students")
        self.students = self.dbms.get_heap_file("students")

        self.sample_rows = [
            [1, "Alice", "COMP3221"],
            [2, "Bob", "INFO1103"],
            [3, "Carol", "COMP3221"],
            [4, "Dave", "INFO1103"],
            [5, "Eve", "COMP3308"],
            [6, "Frank", "COMP3308"],
            [7, "Grace", "COMP3221"],
        ]

    def tearDown(self):
        """Clean up the temporary database file."""
        self.dbms.close()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def _insert_students(self, rows=None):
        """Insert rows into the students table for a test scenario."""
        with self.students.inserter() as inserter:
            for row in rows or self.sample_rows:
                inserter.insert(row)

    def _run_query(self, sql: str):
        """Plan and execute a query, returning rows plus execution details."""
        query = Query.generate_query(sql)
        self.assertIsNotNone(query, f"Failed to parse query: {sql}")
        self.assertIsNone(query.validate(self.dbms.get_catalog()))
        logical_plan = self.planner.create_logical_plan(query)
        execution_plan = self.planner.create_execution_plan(logical_plan)
        try:
            results = [tuple_obj.row[:] for tuple_obj in execution_plan]
        finally:
            execution_plan.close()
        return results, self.planner.get_last_execution_details()

    def test_hash_index_on_empty_table(self):
        """Proves empty tables build cleanly and exact-match probes return no rows."""
        index = self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=4)

        lookup = index.lookup("COMP3221")

        self.assertEqual(lookup.tuples, [])
        self.assertEqual(index.stats()["total_tuples"], 0)
        self.assertEqual(index.stats()["non_empty_buckets"], 0)

    def test_hash_index_single_insert_and_lookup(self):
        """Proves one inserted tuple can be found by an exact-match hash probe."""
        self._insert_students([[1, "Alice", "COMP3221"]])
        index = self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)

        lookup = index.lookup("COMP3221")

        self.assertEqual(len(lookup.tuples), 1)
        self.assertEqual(lookup.tuples[0].row, [1, "Alice", "COMP3221"])

    def test_hash_index_duplicate_keys(self):
        """Proves duplicate indexed values are all preserved inside the index."""
        self._insert_students()
        index = self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)

        lookup = index.lookup("COMP3221")

        self.assertEqual([tuple_obj.get_column("id") for tuple_obj in lookup.tuples], [1, 3, 7])

    def test_hash_index_missing_key_returns_empty(self):
        """Proves probing for an absent key returns an empty result without errors."""
        self._insert_students()
        index = self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)

        lookup = index.lookup("MATH1001")

        self.assertEqual(lookup.tuples, [])
        self.assertGreaterEqual(lookup.tuples_examined, 0)

    def test_hash_index_collision_handling(self):
        """Proves multiple keys sharing one bucket remain distinguishable on lookup."""
        self._insert_students(
            [
                [1, "Alice", "COMP3221"],
                [2, "Bob", "INFO1103"],
                [3, "Carol", "COMP3221"],
            ]
        )
        index = self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=1)

        lookup = index.lookup("COMP3221")
        stats = index.stats()

        self.assertEqual([tuple_obj.get_column("id") for tuple_obj in lookup.tuples], [1, 3])
        self.assertEqual(lookup.tuples_examined, 3)
        self.assertEqual(stats["max_bucket_size"], 3)
        self.assertEqual(stats["non_empty_buckets"], 1)

    def test_build_index_from_existing_table(self):
        """Proves index creation scans existing heap data and stores all matching tuples."""
        self._insert_students()
        index = self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)

        stats = index.stats()

        self.assertEqual(stats["total_tuples"], len(self.sample_rows))
        self.assertEqual(index.lookup("COMP3308").tuples[0].get_column("name"), "Eve")

    def test_query_executor_uses_index_for_equality_on_indexed_column(self):
        """Proves the planner chooses HASH INDEX SCAN for eligible equality predicates."""
        self._insert_students()
        self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)

        results, details = self._run_query("SELECT * FROM students WHERE class = 'COMP3221';")

        self.assertEqual(details.plan_name, "HASH INDEX SCAN")
        self.assertEqual(details.index_name, "students_class_idx")
        self.assertEqual(results, [[1, "Alice", "COMP3221"], [3, "Carol", "COMP3221"], [7, "Grace", "COMP3221"]])

    def test_query_executor_falls_back_for_non_indexed_column(self):
        """Proves predicates on non-indexed columns still use the original sequential scan."""
        self._insert_students()
        self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)

        results, details = self._run_query("SELECT * FROM students WHERE name = 'Alice';")

        self.assertEqual(details.plan_name, "SEQ SCAN")
        self.assertEqual(details.reason, "no hash index exists for the filtered column")
        self.assertEqual(results, [[1, "Alice", "COMP3221"]])

    def test_query_executor_falls_back_for_unsupported_range_predicate(self):
        """Proves range predicates on an indexed column still fall back to sequential scan."""
        self._insert_students()
        self.dbms.create_hash_index("students", "id", "students_id_idx", bucket_count=8)

        results, details = self._run_query("SELECT * FROM students WHERE id > 3;")

        self.assertEqual(details.plan_name, "SEQ SCAN")
        self.assertEqual(details.reason, "hash index only supports equality lookup")
        self.assertEqual(results, [[4, "Dave", "INFO1103"], [5, "Eve", "COMP3308"], [6, "Frank", "COMP3308"], [7, "Grace", "COMP3221"]])

    def test_indexed_results_match_sequential_scan_results(self):
        """Proves indexed execution preserves the same query semantics as sequential filtering."""
        self._insert_students()

        seq_results, seq_details = self._run_query("SELECT * FROM students WHERE class = 'COMP3221';")
        self.assertEqual(seq_details.plan_name, "SEQ SCAN")

        self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)
        indexed_results, indexed_details = self._run_query("SELECT * FROM students WHERE class = 'COMP3221';")

        self.assertEqual(indexed_details.plan_name, "HASH INDEX SCAN")
        self.assertEqual(indexed_results, seq_results)

    def test_insert_after_index_creation_updates_index(self):
        """Proves post-creation inserts are reflected in future index lookups."""
        self._insert_students([[1, "Alice", "COMP3221"]])
        index = self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)

        with self.students.inserter() as inserter:
            inserter.insert([2, "Bob", "COMP3221"])

        lookup = index.lookup("COMP3221")

        self.assertEqual([tuple_obj.get_column("id") for tuple_obj in lookup.tuples], [1, 2])

    def test_index_stats_are_correct(self):
        """Proves reported statistics stay consistent with indexed contents."""
        self._insert_students()
        index = self.dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=4)

        stats = index.stats()

        self.assertEqual(stats["name"], "students_class_idx")
        self.assertEqual(stats["table_name"], "students")
        self.assertEqual(stats["column_name"], "class")
        self.assertEqual(stats["bucket_count"], 4)
        self.assertEqual(stats["total_tuples"], len(self.sample_rows))
        self.assertGreaterEqual(stats["non_empty_buckets"], 1)
        self.assertGreaterEqual(stats["max_bucket_size"], 1)

    def test_hash_index_direct_build_from_table(self):
        """Proves the standalone HashIndex owner can be built independently when needed."""
        self._insert_students()
        index = HashIndex("manual_students_class_idx", "students", "class", self.schema, bucket_count=8)

        built = index.build_from_table(self.students)

        self.assertIs(built, index)
        self.assertEqual(len(index.lookup("INFO1103").tuples), 2)


if __name__ == "__main__":
    unittest.main()
