"""Iterator for returning tuples produced by a hash index lookup."""

from __future__ import annotations

from typing import List, Optional

from simpledb.access.read.access_iterator import AccessIterator
from simpledb.heap.tuple import Tuple
from simpledb.main.catalog.tuple_desc import TupleDesc


class IndexScan(AccessIterator):
    """In-memory iterator over tuples returned by an index probe."""

    def __init__(
        self,
        tuples: List[Tuple],
        schema: TupleDesc,
        index_name: str,
        tuples_examined: int,
        lookup_key: object,
    ) -> None:
        self._tuples = tuples
        self._schema = schema
        self.index_name = index_name
        self.lookup_key = lookup_key
        self.tuples_examined = tuples_examined
        self._position = 0
        self._mark = 0
        self._next_tuple: Optional[Tuple] = None

    def has_next(self) -> bool:
        if self._next_tuple is not None:
            return True
        if self._position >= len(self._tuples):
            return False
        self._next_tuple = self._tuples[self._position]
        self._position += 1
        return True

    def __next__(self) -> Tuple:
        if self.has_next():
            result = self._next_tuple
            self._next_tuple = None
            return result
        raise StopIteration()

    def get_schema(self) -> TupleDesc:
        return self._schema

    def close(self) -> None:
        self._next_tuple = None
        self._position = len(self._tuples)

    def mark(self) -> None:
        self._mark = self._position - (1 if self._next_tuple is not None else 0)

    def reset(self) -> None:
        self._position = self._mark
        self._next_tuple = None
