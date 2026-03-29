"""
README for the Python conversion of USYD JavaDB to SimpleDB.
"""

# SimpleDB - Python Version

This is a complete Python conversion of the original Java database join algorithms project for teaching DATA3404 at the University of Sydney.

## Project Structure

```
simpledb/
├── main/                   # Global constants and configuration
    └── catalog/            # Catalog and Type representations
├── heap/                   # Heap file management and tuple representation
├── disk/                   # Disk management and page I/O
├── buffer/                 # Buffer pool management
├── access/                 # Record access (read/write iterators)
├── parser/                 # Query parsing
├── executor/               # Query execution engine
    ├── projection/         # Column projection
    └── join/               # Join algorithm implementations
└── run/                    # Demo application

tests/                      # Unit tests
├── test_main/              # unit tests of database manager
└── test_parser/            # unit tests for query parsing
```

## Key Features

- **Join Algorithms**:
  - Nested Loop Join

- **Database Management**:
  - Buffer pool with MRU replacement policy
  - Disk manager with file I/O
  - Catalog for schema management

- **Type System**:
  - Support for STRING, INTEGER, DOUBLE, and BOOLEAN types
  - Type-safe tuple operations
  - Schema validation

## Installation

No external dependencies are required - uses only Python standard library.

```bash
cd .
```

## Running the Demo

```bash
python3 -B -m simpledb.run.demo
```

This starts an interactive query engine where you can:
- Create tables with schemas
- Insert data
- Execute SELECT and JOIN queries

Example queries:
```sql
SELECT name, age FROM students;
SELECT name, tutor FROM students JOIN tutors ON class = id;
```

## Running Tests

```bash
python3 -B -m unittest discover -s tests -p "test_*.py" -v 2>&1
```

## Implementation Notes

### Differences from Java Version

1. **Type Handling**: Python's dynamic typing is used with explicit type hints where needed
2. **File I/O**: Using Python's built-in file operations instead of RandomAccessFile
3. **Serialization**: Using `struct` module for binary serialization instead of ByteBuffer
4. **Memory Management**: Python's garbage collection handles object lifecycle
5. **Collections**: Using Python lists and dicts instead of Java's ArrayList and HashMap

### Key Classes

- `Tuple`: Represents a row in the database
- `TupleDesc`: Schema definition
- `Page/DataPage`: Fixed-size disk pages (1KB)
- `DiskManager`: Handles disk I/O
- `BufferManager`: Manages buffer pool
- `HeapFile`: Collection of data pages
- `AccessIterator`: Abstract iterator for table access
- Join algorithms: NestedLoopJoin

## Architecture

The system follows a layered architecture:

```
Query Engine
    ↓
Query Parser
    ↓  
Join Operators + Projection
    ↓
Access Layer (Iterators)
    ↓
Buffer Manager
    ↓
Disk Manager
```

## Performance Considerations

- Buffer pool uses a random replacement policy
- Page size: 1024 bytes
- Maximum buffer frames: 32
- Join algorithms have different I/O costs (documented in the original Java code)

## Future Enhancements

- Add more replacement policies (LRU, Clock)
- Implement additional join algorithms (Hash Join, Radix Join)
- Add query optimization
- Support for indexes
- Transaction management

## References

- Original Java Project: JavaDB (University of Sydney, DATA3404/INFO3404)
- O'Reilly "Database Internals" for disk management concepts
- "Database Management System" methodology

---

**Note**: This is an educational reimplementation. For production use, consider established databases like PostgreSQL, MySQL, or SQLite.
