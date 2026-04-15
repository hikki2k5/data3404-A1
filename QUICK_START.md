# Quick Start Guide

This is a short setup and run guide for the Python SimpleDB assignment code.

## Step 1: Install requirements

From the repository root:

```powershell
python3 -m pip install -r requirements.txt
```

## Step 2: Run the standard demo

```powershell
python3 -m simpledb.run.demo
```

You should see:

```text
SimpleDB Query Engine
Type 'quit' to exit
SQL>
```

## Step 3: Try a few sample queries

```sql
SELECT name, age FROM Students;
SELECT name, class FROM Students;
SELECT name, tutor FROM Students JOIN Tutors ON class = id;
SELECT name, age, class FROM Students JOIN Tutors ON class = id WHERE tutor = Scott ORDER BY name LIMIT 2;
```

## Step 4: Run the hash-index demo

```powershell
python3 -m simpledb.run.hash_index_demo
```

This demo shows:
- index creation
- index statistics
- when the planner chooses `HASH INDEX SCAN`
- when it falls back to `SEQ SCAN`
- a simple logical performance comparison

## Step 5: Run all tests

```powershell
python3 -m unittest discover -s tests -p "test*.py"
```

## Step 6: Check coverage

```powershell
python3 -m coverage run -m unittest
python3 -m coverage report -m
```

## Optional: Performance evaluation with AuctionDB

The repository now includes larger example databases and a helper script in `tests/performance/`.

Files included:
- `tests/performance/auctiondb.py`
- `tests/performance/data3404_auctiondb_test.db`
- `tests/performance/data3404_auctiondb_small.db`
- `tests/performance/data3404_auctiondb_large.db`

These are useful if you want to evaluate your implementation on data larger than the small built-in demo tables.

## Common Notes

- Run commands from the root `SimpleDB-Assignment` directory.
- Use `python3` for the commands in this repository.
- The hash index is intended for equality predicates, not range predicates.
