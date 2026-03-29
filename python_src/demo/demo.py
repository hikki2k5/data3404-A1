"""
Demo for the Join Algorithm Database System.
"""

from python_src.global_module.database_manager import DatabaseManager
from python_src.execution.query_engine import QueryEngine
from python_src.heap.tuple_desc import TupleDesc


STUDENT_ROWS_SMALL = [
    ["Michael", 19, "INFO1103", True],
    ["Jan", 18, "INFO1903", False],
    ["Roger", 20, "INFO1103", True],
    ["Rachael", 21, "ELEC1601", False]
]

TUTOR_ROWS_SMALL = [
    ["INFO1103", "Joshua"],
    ["INFO1103", "Scott"],
    ["COMP2129", "Maxwell"],
    ["INFO1903", "Steven"]
]


def insert_rows(table, rows):
    """Insert rows into a table."""
    with table.inserter() as inserter:
        for row in rows:
            inserter.insert(row)


def main():
    """Run the demo."""
    dbms = DatabaseManager()
    
    # Create Test Schema for students
    student_schema = TupleDesc()
    student_schema.add_string("name").add_integer("age").add_string("class").add_boolean("male")
    dbms.get_catalog().add_schema(student_schema, "students")
    students = dbms.get_heap_file("students")
    
    # Create Test Schema for tutors
    tutor_schema = TupleDesc()
    tutor_schema.add_string("id").add_string("tutor")
    dbms.get_catalog().add_schema(tutor_schema, "tutors")
    tutors = dbms.get_heap_file("tutors")
    
    # Insert rows
    insert_rows(students, STUDENT_ROWS_SMALL)
    insert_rows(tutors, TUTOR_ROWS_SMALL)
    
    # Run query engine
    query_engine = QueryEngine(dbms)
    query_engine.run()
    
    # Flush dirty pages
    dbms.get_buffer_manager().flush_dirty()


if __name__ == "__main__":
    main()
