# DATA3404 A1 Extension Submission

## Chosen Extension

This submission implements **Option 4 (Very High) - Integrated Index Structure** using a **hash index** for SimpleDB.

The extension adds:
- an integrated `HashIndex` structure that stores **full tuples directly in index buckets**
- a catalog-level index registry for table/column metadata
- planner/executor support for choosing **HASH INDEX SCAN** for eligible equality predicates
- automatic index maintenance on inserts
- comprehensive unit tests and a runnable evaluation demo

## Main Files Added or Updated

### New files
- `simpledb/index/hash_index.py`
- `simpledb/index/index_scan.py`
- `simpledb/index/__init__.py`
- `simpledb/run/hash_index_demo.py`
- `tests/test_executor/test_hash_index.py`

### Updated files
- `simpledb/executor/query_planner.py`
- `simpledb/main/database_manager.py`
- `simpledb/main/catalog/catalog.py`
- `simpledb/heap/heap_file.py`
- `simpledb/access/write/heap_file_inserter.py`
- `simpledb/parser/query.py`
- `simpledb/parser/filter_args.py`
- `requirements.txt`

## Requirements

Install development dependencies if needed:

```powershell
py -m pip install -r requirements.txt
```

The database itself only uses the Python standard library. The packages in `requirements.txt` are for testing and coverage.

## Run Instructions

### Run all unit tests

```powershell
py -m unittest discover -s tests -p "test*.py"
```

### Run coverage

```powershell
py -m coverage run -m unittest
py -m coverage report -m
```

### Run the integrated hash index demo

```powershell
py -m simpledb.run.hash_index_demo
```

The demo prints:
- index creation and population
- index statistics
- chosen execution plan for each query
- correctness checks
- a simple logical performance comparison between sequential scan and hash index scan

## How to Use the Extension Programmatically

```python
from simpledb.main.database_manager import DatabaseManager
from simpledb.main.catalog.tuple_desc import TupleDesc

dbms = DatabaseManager("demo.db")

schema = TupleDesc().add_integer("id").add_string("name").add_string("class")
dbms.get_catalog().add_schema(schema, "students")

students = dbms.get_heap_file("students")
with students.inserter() as inserter:
    inserter.insert([1, "Alice", "COMP3221"])
    inserter.insert([2, "Bob", "INFO1103"])

index = dbms.create_hash_index("students", "class", "students_class_idx", bucket_count=8)
results = index.lookup("COMP3221")
print([tuple_obj.row for tuple_obj in results.tuples])
```

## Supported Indexed Query Pattern

The planner/executor uses the index for:

```sql
SELECT * FROM Students WHERE class = 'COMP3221';
```

The planner falls back to sequential scan for:
- predicates on non-indexed columns
- unsupported operators such as `>`, `<`, `!=`, `<=`, `>=`
- queries where no valid hash index exists

## Validation Summary

At the time of submission:
- all tests in `tests/` pass
- the integrated hash-index demo runs successfully
- overall project coverage is approximately **87%**
- coverage across the extended hash-index feature area is approximately **80%+**

## Included Documentation

- `README-ASSIGNMENT.md`: submission-specific instructions
- `documentation/DESIGN_DOC_HASH_INDEX.md`: design notes
- `documentation/REPORT_HASH_INDEX.md`: implementation report, evaluation, and reflection

## genAI Disclosure

genAI was used as an implementation and drafting assistant. All generated code and text were reviewed, tested, corrected, and integrated manually. The report includes a dedicated section explaining how genAI was used, where it made mistakes, and how those mistakes were verified and fixed.
