"""
QUICK START GUIDE - Python Join Algorithms Database
"""

# Quick Start Guide

## Step 1: Verify Installation

Python 3.7+ is required. Check your installation:

```bash
python3 --version
```

## Step 2: Navigate to Project

```bash
cd "python_src"
```

## Step 3: Run the Demo

```bash
python3 ../python_src/demo/demo.py
```

You should see:
```
Join Algorithm Query Engine
Type 'quit' to exit

SQL>
```

## Step 4: Try Sample Queries

### Create tables and insert data - The demo automatically sets up:
- `students` table with columns: name (STRING), age (INTEGER), class (STRING), male (BOOLEAN)
- `tutors` table with columns: id (STRING), tutor (STRING)

### Sample Queries:

**1. Simple SELECT:**
```sql
SELECT name, age FROM students;
```

**2. SELECT with projection:**
```sql
SELECT name, class FROM students;
```

**3. JOIN query:**
```sql
SELECT name, tutor FROM students JOIN tutors ON class = id;
```

**4. Full command with semicolon:**
```sql
SELECT name, age, class FROM students;
```

## Running Tests

In the `python_test/` directory:

```bash
cd ../python_test
python3 -m unittest test_basic.py -v
```

Or with pytest:

```bash
pytest test_basic.py -v
```

## Module Overview

| Module | Purpose |
|--------|---------|
| `global_module/` | Type system, constants, database manager |
| `heap/` | Tuple representation and heap file management |
| `disk/` | Disk manager and page I/O |
| `buffer/` | Buffer pool with MRU replacement |
| `access/` | Record access (read/write iterators) |
| `join/` | Join algorithm implementations |
| `parser/` | SQL query parsing |
| `execution/` | Query engine with REPL |

## Creating Custom Queries

To use the database programmatically:

```python
from python_src.global_module.database_manager import DatabaseManager
from python_src.heap.tuple_desc import TupleDesc

# Initialize database
dbms = DatabaseManager()

# Create a schema
schema = TupleDesc()
schema.add_string("name").add_integer("age")
dbms.get_catalog().add_schema(schema, "my_table")

# Get the table
table = dbms.get_heap_file("my_table")

# Insert rows
with table.inserter() as inserter:
    inserter.insert(["Alice", 30])
    inserter.insert(["Bob", 25])

# Read data
for tuple_obj in table.iterator():
    print(tuple_obj)
```

## Common Issues

### Issue: Module not found
**Solution**: Make sure you're running from the correct directory
```bash
cd "/path/to/Join-Algorithms"
python3 python_src/demo/demo.py
```

### Issue: Query syntax error
**Solution**: Ensure your query follows this format:
```sql
SELECT col1, col2 FROM table [JOIN table2 ON col1 = col2];
```

### Issue: Table/Column not found
**Solution**: 
1. Verify the schema was added: `dbms.get_catalog().read_schema("table_name")`
2. Check column names match exactly (case-sensitive)

## Performance Tips

1. **Buffer Pool**: Configured with 32 frames - adjust in `database_constants.py`
2. **Block Size**: For BlockNestedLoopJoin, adjust block frames:
   ```python
   NestedLoopJoin(left, right, condition, block_size=4)
   ```
3. **Join Algorithm**: Choose based on data size:
   - Small tables: NestedLoopJoin

## Project Structure

```
Join-Algorithms/
├── python_src/           # Main implementation
├── python_test/          # Unit tests
├── PYTHON_README.md     # Full documentation
├── CONVERSION_SUMMARY.md # Conversion details
├── QUICK_START.md       # This file
└── src/                 # Original Java source (reference)
```

## File Size Reference

- Database file grows as data is inserted
- Page size: 1024 bytes (fixed)
- Max buffer frames: 32

## Next Steps

1. **Learn the architecture**: Read PYTHON_README.md
2. **Understand the conversion**: Read CONVERSION_SUMMARY.md
3. **Study the code**: Start with demo.py
4. **Experiment**: Try different join queries
5. **Extend**: Add new features or algorithms

## Documentation

- **API Documentation**: Docstrings in each Python file
- **Type Hints**: All functions have Python type annotations
- **Examples**: See demo.py for usage patterns

## Support

For issues or questions:
1. Check PYTHON_README.md for detailed documentation
2. Review the test cases in python_test/test_basic.py
3. Examine the code comments in python_src/

---

**Happy database exploring!**
