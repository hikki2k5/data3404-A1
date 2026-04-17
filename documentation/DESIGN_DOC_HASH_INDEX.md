# Design Documentation

## Integrated Hash Index for SimpleDB

## 1. Aim of the Extension

For this assignment I implemented **Option 4 (Very High) - Integrated Index Structure** using a **hash index**.

The main goal of the extension was to add an index that does more than just store references. In this implementation, the hash index stores **full tuples directly inside its buckets**. I also integrated it into query execution so that the system can actually choose an index-based access path for suitable queries, instead of always doing a full sequential scan.

The main design goals were:
- keep the implementation consistent with the current SimpleDB code structure
- make only the necessary architectural changes
- support equality lookup on one indexed column
- preserve existing query semantics when the index cannot be used
- keep the code readable and easy to test

## 2. Existing Code Structure and Where the Extension Fits

Before adding the index, the system already had a clear iterator-based execution flow. After inspecting the codebase, the main points relevant to this extension were:

- **Table scan** happened in `QueryPlanner._build_iterator(...)` when an `access` node returned `HeapFile.iterator()`
- **Selection predicates** were evaluated in `QueryPlanner.filter_where(...)`, which wrapped the child iterator with `Filter`
- **Metadata** in the catalog only stored schemas, not index information
- **Tuple insertion** happened through `HeapFile.inserter()` and `HeapFileInserter.insert(...)`

From this, the cleanest places to extend the system were:
- the **catalog**, to store index metadata
- the **database manager**, to create and register indexes
- the **insert path**, so indexes stay up to date after inserts
- the **query planner/executor**, so it can choose an index scan for eligible predicates

## 3. Files Changed

The main files involved in the extension are listed below.

### Core index and execution files
- `simpledb/index/hash_index.py`
- `simpledb/index/index_scan.py`
- `simpledb/executor/query_planner.py`
- `simpledb/main/database_manager.py`
- `simpledb/main/catalog/catalog.py`

### Insert maintenance
- `simpledb/heap/heap_file.py`
- `simpledb/access/write/heap_file_inserter.py`

### Parser support
- `simpledb/parser/query.py`
- `simpledb/parser/filter_args.py`

### Testing and demo
- `tests/test_executor/test_hash_index.py`
- `simpledb/run/hash_index_demo.py`
- `tests/performance/auctiondb.py`
- `tests/performance/import_csv.py`
- `tests/performance/evaluate_hash_index.py`

## 4. Main Design Decisions

## 4.1 `HashIndex` class

The main owner of the new index structure is the `HashIndex` class.

Its responsibilities are:
- validate index setup
- hash key values into buckets
- store full tuples in bucket lists
- support duplicate keys
- support equality lookup
- report simple statistics for testing and evaluation

The main public methods are:
- `build_from_table(table)`
- `insert(tuple_obj)`
- `lookup(key)`
- `stats()`

The most important design decision here is that the buckets store **tuple copies**, not tuple IDs or page references. This directly matches the requirement for an integrated index structure.

## 4.2 `IndexScan` operator

To keep the extension compatible with the current execution pipeline, I added `IndexScan` as a lightweight `AccessIterator`.

This was useful because:
- it fits naturally into the existing iterator model
- projection, ordering, and limit operators can still work above it
- the access path remains visible in tests and demo output

## 4.3 Index metadata in the catalog

I extended the `Catalog` with a simple index registry:
- `add_index(...)`
- `get_index(...)`
- `get_indexes(...)`

This felt like the right place because the catalog already manages table-related metadata. It also means the planner can check whether a column has an index without hardcoding anything.

## 4.4 Index creation and maintenance in `DatabaseManager`

I added `create_hash_index(...)` to `DatabaseManager`, which:
- validates the table and column
- creates the `HashIndex`
- builds it from existing heap data
- registers it in the catalog

I also used `DatabaseManager` to maintain indexes after inserts, because it already sits between the catalog and heap-file access.

## 5. How Query Processing Uses the Index

The planner now uses a simple rule-based decision:

Use `HASH INDEX SCAN` only when:
- the query is filtering a single table
- the predicate is an equality predicate, for example `class = 'COMP3221'`
- the filtered column has a registered hash index

Use `SEQ SCAN` when:
- the filtered column is not indexed
- the predicate is unsupported, such as `>`, `<`, `!=`, `<=`, `>=`
- the access pattern is not a simple access-plus-filter case

I also added a small step that reorders filters so an index-eligible equality predicate is pushed closest to the access node when that is safe to do. This keeps the planner simple, but still lets the index be used in a realistic way.

## 6. Insert Maintenance

The extension keeps the index updated after inserts.

The flow is:
- `DatabaseManager.get_heap_file(...)` provides an insert callback
- `HeapFile` passes that callback into `HeapFileInserter`
- after a tuple is successfully inserted into heap storage, the callback updates any registered indexes for that table

I chose this approach because it avoids creating a separate insertion API for indexed tables and keeps heap storage as the main source of truth.

## 7. Edge Cases Considered

The design and tests cover the following cases:
- empty tables
- single tuple insertion
- duplicate key values
- missing key lookups
- collisions where multiple tuples land in the same bucket
- unsupported predicates on indexed columns
- queries on non-indexed columns
- inserts after index creation

These cases were important because the rubric places a strong emphasis on correctness, not just having the feature present.

## 8. Verification Plan

I used three levels of verification.

### Unit tests for the index itself
- build on empty table
- single insert and lookup
- duplicate keys
- missing keys
- collision handling
- build from existing table
- stats validation

### Integration tests
- planner chooses `HASH INDEX SCAN` for indexed equality predicates
- planner falls back to `SEQ SCAN` for non-indexed columns
- planner falls back to `SEQ SCAN` for unsupported range predicates
- indexed results match sequential results
- inserts after index creation are reflected in lookups

### Demo/evaluation
- run a deterministic demo script
- print plan choice and result tuples
- compare tuples examined for sequential scan vs index scan
- optionally test on the larger AuctionDB example files added by the upstream update
- import AuctionDB tables with `tests/performance/import_csv.py` and create hash indexes during import for Option 4 evaluation
- reopen indexed AuctionDB databases with `tests/performance/auctiondb.py --rebuild-hash-indexes` so the planner can rebuild the session-local hash indexes
- collect repeated benchmark metrics using `tests/performance/evaluate_hash_index.py`

## 9. Assumptions and Limitations

The implementation assumes:
- one hash index is defined on one column at a time
- the main optimisation target is exact-match lookup
- table data still remains in heap storage as before

Current limitations are:
- no delete or update maintenance, because the base system does not fully support those operations
- no persistent on-disk index storage
- no cost-based optimiser
- only equality predicates use the hash index

## 10. Summary

Overall, I think this design fits the existing SimpleDB codebase well. The main reason is that it extends the current architecture rather than replacing it. The hash index is isolated in its own module, metadata is stored in the catalog, the database manager handles creation and maintenance, and the planner decides when the index is valid to use.

This keeps the extension modular and readable while still providing a genuine improvement over the original always-sequential access path.
