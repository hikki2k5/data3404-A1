"""
QUICK START GUIDE - Python SimpleDB Database
"""

# Quick Start Guide

## Step 1: Verify Installation

Python 3.7+ is required. Check your installation:

```bash
python3 --version
```

## Step 2: Navigate to Project

```bash
cd "SimpleDB"
```

## Step 3: Run the Demo

```bash
python3 -B -m simpledb.run.demo
```

You should see:

```bash
SimpleDB Query Engine
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
SELECT name, age FROM Students;
```

**2. SELECT with projection:**
```sql
SELECT name, class FROM Students;
```

**3. JOIN query:**
```sql
SELECT name, tutor FROM Students JOIN Tutors ON class = id;
```

**4. Full command with semicolon:**
```sql
SELECT name, age, class FROM Students;
```

## Running Tests

In the `tests/` directory:

```bash
cd tests
python3 -B -m unittest discover -s tests -p "test_*.py" -v 2>&1
```

Or with pytest:

```bash
pytest tests/test_main/test_database_manager.py -v
```

## Module Overview

| Module | Purpose |
|--------|---------|
| `main/` | Global constants, database manager |
| `main/catalog` | Type system, schema |
| `heap/` | Tuple representation and heap file management |
| `disk/` | Disk manager and page I/O |
| `buffer/` | Buffer pool with MRU replacement |
| `access/` | Record access (read/write iterators) |
| `parser/` | SQL query parsing |
| `executor/` | Query engine with REPL |
| `executor/join/` | Join algorithm implementations |

## Creating Custom Queries

To use the database programmatically:

```python
from simpledb.main.database_manager import DatabaseManager
from simpledb.main.catalog.tuple_desc import TupleDesc

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
cd "/path/to/SimpleDB"
python3 -B -m simpledb.run.demo
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
2. **Block Size**: For NestedLoopJoin, adjust block frames:
   ```python
   NestedLoopJoin(left, right, condition, block_size=4)
   ```
3. **Join Algorithm**: Choose based on data size:
   - Small tables: NestedLoopJoin

## Project Structure

```
Join-Algorithms/
├── simpledb/            # Main implementation
├── tests/               # Unit tests
├── README.md            # Full documentation
├── QUICK_START.md       # This file
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
1. Check README.md for detailed documentation
2. Review the test cases in tests/
3. Examine the code comments in simpledb/

---

**Happy database exploring!**
