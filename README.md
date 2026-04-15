# SimpleDB - Python Database Engine

This repository contains the Python version of the SimpleDB teaching database used in DATA3404 at the University of Sydney.

## Project Structure

```text
simpledb/
|-- main/                   # Global constants and configuration
|   `-- catalog/            # Catalog and type representations
|-- heap/                   # Heap file management and tuple representation
|-- disk/                   # Disk management and page I/O
|-- buffer/                 # Buffer pool management
|-- access/                 # Record access (read/write iterators)
|-- parser/                 # Query parsing
|-- executor/               # Query execution engine
|   |-- projection/         # Projection operator
|   |-- join/               # Join implementations
|   |-- filter/             # WHERE filtering
|   |-- ordering/           # ORDER BY support
|   `-- limit/              # LIMIT support
|-- index/                  # Integrated hash index extension
`-- run/                    # Demo programs

tests/
|-- test_main/              # Database manager tests
|-- test_buffer/            # Buffer manager tests
|-- test_parser/            # Parser tests
|-- test_executor/          # Executor and extension tests
`-- performance/            # AuctionDB performance data and helper script
```

## Key Features

- Pipelined query execution
- Separate parser, planner, and executor stages
- Heap-file storage with slotted pages
- Buffer manager with random replacement
- Support for `STRING`, `INTEGER`, `DOUBLE`, and `BOOLEAN`
- Integrated hash-index extension for equality predicates

## Installation

The core database mainly uses the Python standard library. A few development and runtime helper packages are listed in `requirements.txt`.

```powershell
python3 -m pip install -r requirements.txt
```

## Running the Demo

From the repository root:

```powershell
python3 -m simpledb.run.demo
```

This starts the interactive query engine.

Example queries:

```sql
SELECT name, age FROM Students;
SELECT name, tutor FROM Students JOIN Tutors ON class = id;
```

## Running Unit Tests

```powershell
python3 -m unittest discover -s tests -p "test*.py"
```

## Running Coverage

```powershell
python3 -m coverage run -m unittest
python3 -m coverage report -m
```

## Performance Evaluation Support

After the recent upstream update, the repository also includes AuctionDB example databases and a helper script for larger performance experiments:

- `tests/performance/auctiondb.py`
- `tests/performance/data3404_auctiondb_test.db`
- `tests/performance/data3404_auctiondb_small.db`
- `tests/performance/data3404_auctiondb_large.db`

These are useful if you want to test behaviour beyond the small built-in demo data.

## Acknowledgements

SimpleDB is based on the PASTA JavaDB project from INFO3404/DATA3404, mainly written by Scott Sidwell, Chris Natoli, and Bryn Jeffries.

## References

- PASTA / JavaDB teaching project
- O'Reilly, *Database Internals*
- Ramakrishnan and Gehrke, *Database Management Systems*
