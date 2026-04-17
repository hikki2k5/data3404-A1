"""Integrated hash index storing full tuples directly inside buckets."""

# genAI acknowledgement:
# genAI was used only for limited support during drafting and wording cleanup.
# The index design, integrated-storage approach, collision handling choices,
# and final tested implementation were decided and revised by the team.

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List

from simpledb.heap.tuple import Tuple
from simpledb.main.catalog.tuple_desc import TupleDesc


@dataclass(frozen=True)
class HashIndexLookupResult:
    """Result of probing a hash index for an exact-match key."""

    tuples: List[Tuple]
    bucket_id: int
    tuples_examined: int


class HashIndex:
    """Bucket-based hash index storing full tuples for one table column."""

    def __init__(
        self,
        name: str,
        table_name: str,
        column_name: str,
        schema: TupleDesc,
        bucket_count: int = 8,
    ) -> None:
        if bucket_count <= 0:
            raise ValueError("bucket_count must be positive")
        if not schema.has_field(column_name):
            raise KeyError(f"Column '{column_name}' not found in schema")

        self.name = name
        self.table_name = table_name
        self.column_name = column_name.lower()
        self.schema = schema
        self.bucket_count = bucket_count
        self.column_index = schema.get_index_from_name(self.column_name)
        self._buckets: List[List[Tuple]] = [[] for _ in range(bucket_count)]
        self._tuple_count = 0

    def build_from_table(self, table) -> "HashIndex":
        """Populate the index from all tuples currently stored in a table."""
        self.clear()
        iterator = table.iterator()
        try:
            for tuple_obj in iterator:
                self.insert(tuple_obj)
        finally:
            iterator.close()
        return self

    def clear(self) -> None:
        """Remove all indexed tuples while keeping index metadata intact."""
        self._buckets = [[] for _ in range(self.bucket_count)]
        self._tuple_count = 0

    def insert(self, tuple_obj: Tuple) -> None:
        """Insert a tuple into the appropriate hash bucket."""
        if tuple_obj.get_schema() != self.schema:
            raise ValueError("Tuple schema does not match index schema")

        key = tuple_obj.get_column(self.column_index)
        bucket_id = self._bucket_for_key(key)
        self._buckets[bucket_id].append(self._copy_tuple(tuple_obj))
        self._tuple_count += 1

    def lookup(self, key: Any) -> HashIndexLookupResult:
        """Return all tuples whose indexed column exactly matches key."""
        bucket_id = self._bucket_for_key(key)
        bucket = self._buckets[bucket_id]
        matched = [self._copy_tuple(t) for t in bucket if t.get_column(self.column_index) == key]
        return HashIndexLookupResult(
            tuples=matched,
            bucket_id=bucket_id,
            tuples_examined=len(bucket),
        )

    def stats(self) -> Dict[str, Any]:
        """Return basic index statistics useful for testing and demo output."""
        bucket_sizes = [len(bucket) for bucket in self._buckets]
        non_empty = sum(1 for size in bucket_sizes if size > 0)
        return {
            "name": self.name,
            "table_name": self.table_name,
            "column_name": self.column_name,
            "bucket_count": self.bucket_count,
            "total_tuples": self._tuple_count,
            "non_empty_buckets": non_empty,
            "load_factor": self._tuple_count / self.bucket_count,
            "max_bucket_size": max(bucket_sizes, default=0),
            "bucket_sizes": bucket_sizes,
        }

    def _bucket_for_key(self, key: Any) -> int:
        digest = hashlib.sha256(self._normalise_key(key).encode("utf-8")).hexdigest()
        return int(digest, 16) % self.bucket_count

    @staticmethod
    def _normalise_key(key: Any) -> str:
        return f"{type(key).__name__}:{key}"

    def _copy_tuple(self, tuple_obj: Tuple) -> Tuple:
        copied = Tuple(self.schema, [tuple_obj.get_column(i) for i in range(self.schema.get_num_fields())])
        copied.set_page_id(tuple_obj.get_page_id())
        copied.set_slot_id(tuple_obj.get_slot_id())
        return copied
