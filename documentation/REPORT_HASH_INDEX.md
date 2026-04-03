# Report: Integrated Hash Index Extension

## 1. Introduction

For this assignment I implemented **Option 4 (Very High) - Integrated Index Structure** for the Python version of SimpleDB. The extension I chose was a **hash index**.

The main idea was to add an index that stores **full tuples directly inside the index structure**, rather than only storing pointers or references. I also wanted the extension to be properly integrated into query execution, so that SimpleDB would actually choose the index for suitable equality predicates instead of always doing a sequential scan.

The main objectives of my implementation were:
- satisfy the assignment requirements for the integrated index option
- keep the solution consistent with the existing SimpleDB architecture
- handle edge cases properly
- include strong unit tests and a clear evaluation/demo

## 2. Summary of the Implementation

The extension has four main parts.

### 2.1 Hash index structure

I added a new `HashIndex` class in `simpledb/index/hash_index.py`.

This class supports:
- configurable bucket count
- deterministic hashing
- duplicate keys
- collision handling through bucket lists
- storing **full tuples directly in the buckets**
- building an index from an existing table
- exact-match lookup
- simple statistics for testing and evaluation

This satisfies the main requirement that the index should be integrated and should store data directly.

### 2.2 Query processing integration

I updated the planner in `simpledb/executor/query_planner.py` so that the system can choose a `HASH INDEX SCAN` when all of the following are true:
- the predicate is an equality predicate
- the predicate is on an indexed column
- the query shape is suitable for using the index

If these conditions are not met, the system falls back to `SEQ SCAN`.

To fit the existing architecture, I added a new `IndexScan` iterator instead of creating a completely separate execution path.

### 2.3 Metadata and index creation

I extended the catalog so it can register indexes for each table and column. I also added `create_hash_index(...)` to `DatabaseManager`, which creates the index, builds it from current table contents, and registers it.

### 2.4 Insert maintenance

If tuples are inserted after an index is created, the index is updated automatically through the normal insert path. This was important for correctness and for meeting the requirement that the feature should behave like part of the database system rather than a one-off demo structure.

## 3. Design Choices

## 3.1 Why I used a hash index

I chose a hash index because the assignment specifically mentions optimised predicate scans, especially equality predicates. Hashing is a natural fit for exact-match lookups, and it was also a good choice for this codebase because it could be added without changing the whole storage layer.

## 3.2 Why the index stores full tuples

The key requirement in this extension is that the structure should be an **integrated index**, not just an auxiliary map from key to tuple pointer. For that reason, the buckets store copies of the complete tuples. This makes the extension clearly different from a pointer-based index.

## 3.3 Why metadata was added to the catalog

The catalog already stores table-related metadata, so it made sense to store index registrations there as well. This keeps index information in one place and makes planner lookup simpler.

## 3.4 Why insert maintenance uses a callback

The base system already had a working insert path through `HeapFile` and `HeapFileInserter`. Instead of replacing that path, I added a callback so the index can be updated after a successful insert. I think this was the cleanest option because it kept the rest of the write path stable.

## 4. Testing and Evaluation

## 4.1 Unit testing

I added a dedicated test file for the new extension: `tests/test_executor/test_hash_index.py`.

The tests cover:
- empty table
- single tuple lookup
- duplicate keys
- missing key lookup
- collision handling
- building index from existing table data
- planner choosing index scan for equality on indexed column
- fallback to sequential scan for non-indexed columns
- fallback to sequential scan for unsupported range predicates
- equality between indexed results and sequential results
- correctness after insertions
- index statistics

I also ran the full existing test suite to make sure the extension did not break earlier functionality.

Command used:

```powershell
py -m unittest discover -s tests -p "test*.py"
```

Result:
- all tests passed
- total tests run: `90`

## 4.2 Coverage

I measured coverage using:

```powershell
py -m coverage run -m unittest
py -m coverage report -m
```

Results at the time of submission:
- overall project coverage: about **87%**
- extension feature area: **80%+**
- `hash_index.py`: **95%**
- `index_scan.py`: **87%**
- `query_planner.py`: **86%**

This meets the target of at least 80% coverage for the extended feature set.

## 4.3 Demo and simple performance comparison

I added a runnable demo in `simpledb/run/hash_index_demo.py`.

The demo shows:
- creating sample tables
- inserting tuples
- creating and building indexes
- printing index statistics
- running queries that do and do not use the index
- showing the chosen plan (`HASH INDEX SCAN` or `SEQ SCAN`)
- checking correctness
- comparing tuples examined between sequential scan and index scan

For the example query on `Students WHERE class = 'COMP3221'`, the demo showed:
- sequential scan tuples examined: `8`
- hash index tuples examined: `3`
- reduction in examined tuples: `62.50%`

This is not a full benchmark, but it is a useful logical evaluation showing that the index is actually being used and is reducing work for the intended query type.

## 5. What Worked Well

The main thing that worked well was that the existing SimpleDB structure already used iterators, which made the new `IndexScan` operator fit naturally into the execution pipeline.

Another positive part of the implementation was the separation of responsibilities:
- `HashIndex` handles indexing logic
- `Catalog` stores index metadata
- `DatabaseManager` creates and updates indexes
- `QueryPlanner` decides whether to use the index

This made the extension easier to reason about and easier to test.

## 6. Limitations

There are still some limitations in the current version.

### 6.1 Equality predicates only

The hash index is only used for exact-match predicates. Range predicates such as `>`, `<`, and `>=` still use sequential scan.

### 6.2 No persistent index storage

The index metadata and buckets are currently managed in memory. If the database manager is restarted, the indexes would need to be recreated.

### 6.3 No delete/update maintenance

The current base system does not provide a full delete or update workflow, so I did not extend index maintenance to those operations.

### 6.4 Planner is rule-based

The planner uses a simple rule-based decision instead of a full cost-based optimiser. For this assignment I think that is acceptable, but it would be a limitation in a larger database system.

## 7. What I Learned

One of the main things I learned from this task is that adding an index is not only about implementing a data structure. The bigger challenge is integrating that structure into metadata management, write maintenance, and query planning while still preserving correctness.

I also learned that fallback behaviour is very important. An optimisation is only useful if it is applied in the right cases and avoided in the wrong cases. In this assignment, making sure unsupported predicates still returned correct results through sequential scan was just as important as making equality lookups faster.

## 8. genAI Usage and Reflection

genAI was allowed for this assignment, and I used it as a coding and writing assistant during development. It was mainly useful for:
- helping inspect the codebase structure
- suggesting implementation structure
- drafting test cases
- helping organise documentation

However, I did not use generated output without checking it.

### 8.1 Problems that still needed human correction

Some AI-generated suggestions were not correct or not fully suitable for this codebase. For example:
- some early suggestions did not properly handle temporary file cleanup on Windows
- parser support for `SELECT *` and quoted strings needed manual adjustment for the intended demo queries
- some generated output was more generic than codebase-specific, so it had to be adapted to the actual SimpleDB architecture
- the first version of the demo used Unicode checkmarks, which caused console encoding issues on Windows

### 8.2 How I verified the work

To make sure the final implementation was reliable, I:
- inspected the existing project files before making architectural changes
- ran targeted tests while implementing the feature
- ran the full unit-test suite after integration
- checked coverage explicitly
- ran the demo to verify that the planner really chose `HASH INDEX SCAN`
- reviewed and refined both code and documentation manually

### 8.3 Reflection on using genAI

I found genAI most useful for speeding up exploration and drafting. It was less reliable for details that depend heavily on the local codebase or the execution environment. Because of that, I think genAI works best as a support tool rather than a replacement for debugging, testing, and design judgement.

## 9. Future Improvements

If I continued this project, I would improve it in the following ways:
- persist index metadata and possibly index contents
- support dynamic bucket growth or resizing
- add delete/update maintenance
- support more advanced planner rules
- evaluate performance with larger datasets and page-level metrics

## 10. Conclusion

In conclusion, this extension successfully adds an integrated hash index to SimpleDB and connects it to real query execution. The final version:
- stores full tuples directly in the index
- uses the index for valid equality predicates
- falls back to sequential scan when needed
- preserves correctness
- includes comprehensive tests and a runnable evaluation demo

Overall, I believe the extension meets the expectations of the “Very High” difficulty option while staying clean, modular, and consistent with the existing SimpleDB project.
