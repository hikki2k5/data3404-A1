"""
In-memory ORDER BY implementation.
"""

from functools import cmp_to_key
from simpledb.access.read.access_iterator import AccessIterator
from simpledb.main.catalog.tuple_desc import TupleDesc
from simpledb.executor.ordering.column_comparator import ColumnComparator


class InMemoryOrderBy(AccessIterator):
    """
    In-memory sort operator for order-by.
     - Loads all of the tuples into memory, and then sorts this list
     - Returns the sorted tuples in order when the iterator is accessed
    """

    def __init__(self, child_iter: AccessIterator, columns):
        """
        Constructor for the in-memory OrderBy sort iterator
         - We will need to sort the tuples in the constructor
         - Look at using `new ColumnComparator(columns)` and Collections.sort(...)
         @param child_iter  iterator over the rows to sort
         @param columns     the columns to sort on
        """
        self.schema = child_iter.get_schema()
        self.tuples = []
        self.index = 0

        # materialize all tuples from child and sort in memory
        while child_iter.has_next():
            self.tuples.append(child_iter.__next__())

        self.tuples.sort(key=cmp_to_key(ColumnComparator(columns).compare))
        child_iter.close()

    def close(self):
        self.tuples.clear()

    def get_schema(self) -> TupleDesc:
        return self.schema

    def has_next(self) -> bool:
        return self.index < len(self.tuples)

    def __next__(self):
        if not self.has_next():
            raise StopIteration()
        tuple_obj = self.tuples[self.index]
        self.index += 1
        return tuple_obj

    def __iter__(self):
        return self

    def mark(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()
