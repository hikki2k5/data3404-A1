"""Demonstration of integrated hash-index query execution in SimpleDB."""

from __future__ import annotations

import os
import tempfile

from simpledb.executor.query_planner import QueryPlanner
from simpledb.main.catalog.tuple_desc import TupleDesc
from simpledb.main.database_manager import DatabaseManager
from simpledb.parser.query import Query


STUDENTS = [
    [1, "Alice", "COMP3221"],
    [2, "Bob", "INFO1103"],
    [3, "Carol", "COMP3221"],
    [4, "Dan", "INFO1103"],
    [5, "Ellen", "COMP3308"],
    [6, "Frank", "COMP3308"],
    [7, "Grace", "COMP3221"],
    [8, "Heidi", "INFO1103"],
]

TUTORS = [
    [101, "Dr Jones", "AI"],
    [102, "Dr Smith", "DB"],
    [103, "Dr Patel", "Security"],
    [104, "Dr Lee", "Systems"],
    [105, "Dr Wang", "Networks"],
    [106, "Dr Brown", "Theory"],
]


def create_tables(dbms: DatabaseManager) -> None:
    """Create demo tables and populate them with sample tuples."""
    student_schema = TupleDesc().add_integer("id").add_string("name").add_string("class")
    tutor_schema = TupleDesc().add_integer("id").add_string("name").add_string("specialty")

    dbms.get_catalog().add_schema(student_schema, "Students")
    dbms.get_catalog().add_schema(tutor_schema, "Tutors")

    students = dbms.get_heap_file("Students")
    tutors = dbms.get_heap_file("Tutors")

    with students.inserter() as inserter:
        for row in STUDENTS:
            inserter.insert(row)

    with tutors.inserter() as inserter:
        for row in TUTORS:
            inserter.insert(row)


def run_query(planner: QueryPlanner, sql: str):
    """Execute one query through the real planner/executor and return rows plus plan details."""
    query = Query.generate_query(sql)
    if query is None:
        raise ValueError(f"Could not parse SQL: {sql}")
    validation_error = query.validate(planner.dbms.get_catalog())
    if validation_error is not None:
        raise ValueError(validation_error)

    logical_plan = planner.create_logical_plan(query)
    execution_plan = planner.create_execution_plan(logical_plan)
    try:
        rows = [tuple_obj.row[:] for tuple_obj in execution_plan]
    finally:
        execution_plan.close()
    return rows, planner.get_last_execution_details()


def sequential_results(dbms: DatabaseManager, sql: str):
    """Run the query logic using the original heap scan path for correctness comparison."""
    query = Query.generate_query(sql)
    table = dbms.get_heap_file(query.get_table_name())
    iterator = table.iterator()
    try:
        if query.has_filter_arguments():
            for filter_args in query.get_filter_args():
                iterator = QueryPlanner.filter_where(iterator, filter_args)
        rows = [tuple_obj.row[:] for tuple_obj in iterator]
    finally:
        iterator.close()
    return rows


def print_rows(rows):
    """Pretty-print rows using tuple-style formatting."""
    for row in rows:
        print(f"  ({', '.join(repr(value) for value in row)})")


def print_index_stats(index) -> None:
    """Print formatted statistics for one hash index."""
    stats = index.stats()
    print(f"Index: {stats['name']}")
    print(f"  Table: {stats['table_name']}")
    print(f"  Column: {stats['column_name']}")
    print(f"  Buckets: {stats['bucket_count']}")
    print(f"  Total tuples: {stats['total_tuples']}")
    print(f"  Non-empty buckets: {stats['non_empty_buckets']}")
    print(f"  Load factor: {stats['load_factor']:.2f}")
    print(f"  Max bucket size: {stats['max_bucket_size']}")
    print()


def main() -> None:
    """Run the integrated hash-index demo."""
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()

    dbms = DatabaseManager(temp_db.name)
    try:
        planner = QueryPlanner(dbms)

        print("=" * 70)
        print("SimpleDB - Query Execution with Integrated Hash Index Support")
        print("=" * 70)
        print()

        print("Creating sample tables...")
        create_tables(dbms)
        print("[OK] Created table: Students")
        print("[OK] Created table: Tutors")
        print()

        print("Inserting sample tuples...")
        print(f"[OK] Inserted {len(STUDENTS)} tuples into Students")
        print(f"[OK] Inserted {len(TUTORS)} tuples into Tutors")
        print()

        students_seq_rows, _ = run_query(planner, "SELECT * FROM Students WHERE class = 'COMP3221';")

        print("Creating hash indexes...")
        students_index = dbms.create_hash_index("Students", "class", "Students_class_idx", bucket_count=8)
        tutors_index = dbms.create_hash_index("Tutors", "id", "Tutors_id_idx", bucket_count=8)
        print("[OK] Created hash index Students_class_idx on Students(class)")
        print("[OK] Created hash index Tutors_id_idx on Tutors(id)")
        print()

        print("Building/populating indexes...")
        print(f"[OK] Students_class_idx built with {students_index.stats()['total_tuples']} tuples")
        print(f"[OK] Tutors_id_idx built with {tutors_index.stats()['total_tuples']} tuples")
        print()

        print("-" * 70)
        print("Index Statistics")
        print("-" * 70)
        print()
        print_index_stats(students_index)
        print_index_stats(tutors_index)

        print("=" * 70)
        print("Query Demo 1: Equality predicate on indexed column")
        sql = "SELECT * FROM Students WHERE class = 'COMP3221';"
        rows, details = run_query(planner, sql)
        print(f"SQL: {sql}")
        print(f"Plan chosen: {details.plan_name} on {details.index_name}")
        print(f"Matched tuples: {len(rows)}")
        print("Results:")
        print_rows(rows)
        print()

        print("=" * 70)
        print("Query Demo 2: Equality predicate on another indexed column")
        sql = "SELECT * FROM Tutors WHERE id = 102;"
        rows, details = run_query(planner, sql)
        print(f"SQL: {sql}")
        print(f"Plan chosen: {details.plan_name} on {details.index_name}")
        print(f"Matched tuples: {len(rows)}")
        print("Results:")
        print_rows(rows)
        print()

        print("=" * 70)
        print("Query Demo 3: Predicate on non-indexed column")
        sql = "SELECT * FROM Students WHERE name = 'Alice';"
        rows, details = run_query(planner, sql)
        print(f"SQL: {sql}")
        print(f"Plan chosen: {details.plan_name}")
        print(f"Reason: {details.reason}")
        print(f"Matched tuples: {len(rows)}")
        print("Results:")
        print_rows(rows)
        print()

        print("=" * 70)
        print("Query Demo 4: Unsupported range predicate on indexed column")
        sql = "SELECT * FROM Tutors WHERE id > 102;"
        rows, details = run_query(planner, sql)
        print(f"SQL: {sql}")
        print(f"Plan chosen: {details.plan_name}")
        print(f"Reason: {details.reason}")
        print(f"Matched tuples: {len(rows)}")
        print("Results:")
        print_rows(rows)
        print()

        print("=" * 70)
        print("Correctness Check")
        print("=" * 70)
        indexed_rows, _ = run_query(planner, "SELECT * FROM Students WHERE class = 'COMP3221';")
        print("[OK] Indexed query result matches sequential scan result" if indexed_rows == students_seq_rows else "[FAIL] Indexed query mismatch")
        print(
            "[OK] Non-indexed query still works correctly"
            if run_query(planner, "SELECT * FROM Students WHERE name = 'Alice';")[0] == sequential_results(dbms, "SELECT * FROM Students WHERE name = 'Alice';")
            else "[FAIL] Non-indexed query mismatch"
        )
        print(
            "[OK] Unsupported predicates correctly fall back to sequential scan"
            if run_query(planner, "SELECT * FROM Tutors WHERE id > 102;")[1].plan_name == "SEQ SCAN"
            else "[FAIL] Unexpected access path for range predicate"
        )
        print()

        print("=" * 70)
        print("Performance / Evaluation")
        print("=" * 70)
        sequential_examined = dbms.get_heap_file("Students").count_tuples()
        _, details = run_query(planner, "SELECT * FROM Students WHERE class = 'COMP3221';")
        reduction = 100.0 * (sequential_examined - details.tuples_examined) / sequential_examined
        print("Example comparison for query: Students WHERE class = 'COMP3221'")
        print(f"Sequential scan tuples examined: {sequential_examined}")
        print(f"Hash index tuples examined: {details.tuples_examined}")
        print(f"Improvement: reduced examined tuples by {reduction:.2f}%")
        print()
        print("Note:")
        print("- This is a logical evaluation for the extension")
        print("- Exact timing is optional, but tuple work comparison is shown")
        print()

        print("=" * 70)
        print("All demo tasks completed successfully")
        print("=" * 70)
    finally:
        dbms.close()
        if os.path.exists(temp_db.name):
            os.remove(temp_db.name)


if __name__ == "__main__":
    main()
