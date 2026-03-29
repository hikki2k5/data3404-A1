# Week 7 - Join-Algorithms

This week we are looking at different types of Joins. In the lectures, we covered:

* Simple Nested-Loop
* Block Nested-Loop
* Index Nested-Loop
* Sort-Merge

For the PASTA task, you have the choice of implementing either Simple Nested-Loop, Block Nested-Loop or Sort-Merge joins; for 2, 3 or 4 points respectively.

This week, you will only need to change the files that are in the `joins` package. Some of the boilerplate is already taken care of for you (see `AbstractJoin.java`), however feel free to customise it and make it your own.

We have also extended `AccessIterator` to make your implementation easier, by including the method `mark()` to tell an iterator to remember its current state and `reset()` to return an iterator to its marked state (or the state when originally constructed if `mark()` hasn't been called since). This will allow you to save the position of an iterator and revert back to it. The `NestedLoopJoin` class includes`resetRight()` method to assist your implementation, and you are welcome to re-use this approach in the other join implementations.

We have also added a `JoinComparator` class that may help you compare tuples for a join.

## Simple Nested-Loop (2 Marks)
- Implement the algorithm in the `NestedLoopJoin.java` file.
- Pass all tests in `NestedLoopJoinTest.java`

## Block Nested-Loop (3 Marks)
- Implement the algorithm in the `BlockNestedLoopJoin.java` file.
- Pass all tests in `BlockNestedLoopJoinTest.java`

The `BlockNestedLoopJoin` class contains the method `getNextBlock(AccessIterator)` - which will return the next B pages worth of tuples from the iterator. This may be useful in generating the blocks to iterate over.

## Sort-Merge (4 Marks)
- Implement the algorithm in the `SortMergeJoin.java` file.
- Pass all tests in `SortMergeJoinTest.java`
